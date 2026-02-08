from typing import Any, Dict, List
from app.agents.base import BaseAgentLoop
from app.services.llm_service import LLMService
from app.services.message_service import MessageService
from app.services.conversation_service import ConversationService
from app.services.poetry_service import PoetryService
from app.services.mysql_service import MySQLService
from app.llm.types import LLMMessage
from app.agents.prompts import get_prompt_by_template


class PoetryGameAgent(BaseAgentLoop):
    """
    诗词游戏 Agent Loop 实现
    用于处理飞花令、诗词接龙等游戏

    实现感知 → (思考+决策 → 执行)n次 → 更新状态 的循环流程
    其中思考+决策和执行步骤会循环执行，直到达到最大迭代次数或满足停止条件
    """

    def __init__(self,
                 conversation_id: int,
                 user_id: int,
                 agent_id: int,
                 max_iterations: int = 5):
        super().__init__()
        self.llm = LLMService()
        self.poetry_service = PoetryService()
        self.conversation_service = ConversationService()
        self.message_service = MessageService()
        self.mysql_service = MySQLService()
        self.max_iterations = max_iterations
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.agent_id = agent_id

    def perceive(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        感知阶段：收集用户输入、会话历史、用户记忆
        返回一个dict，包含会话信息、用户输入、用户ID、会话ID、会话记忆、用户记忆等
        """
        # 获取会话详细信息
        conversation = self.conversation_service.get_conversation(
            conversation_id=self.conversation_id, user_id=self.user_id)

        # 获取最近的消息历史
        recent_messages = self.message_service.get_messages_by_conversation(
            conversation_id=self.conversation_id,
            user_id=self.user_id,
            limit=kwargs.get('history_limit', 10))

        # 获取用户长期记忆数据
        user_memory = self.mysql_service.get_agent_user_memory(
            agent_id=conversation.get('agent_id', 1), user_id=self.user_id)

        # 获取规则prompt
        system_prompt = self.mysql_service.get_agent_by_id(
            agent_id=conversation.get('agent_id', 1)).get('system_prompt', '')

        return {
            'recent_messages': recent_messages,
            'user_input': user_input,
            'conversation_memory': conversation.get('memory_data', {}),
            'user_memory': user_memory,
            'game_rules': system_prompt,
            'tools_call_history': [],
        }

    def think(self, perception: Dict[str, Any], **kwargs) -> str:
        """
        思考阶段：分析用户输入和工具调用结果，决定AI的回应策略
        """
        filtered_perception = {
            'game_rules': perception.get('game_rules', ''),
            'recent_messages': perception.get('recent_messages', []),
            'user_input': perception.get('user_input', ''),
            'tools_calls_history': perception.get('tools_call_history', []),
            'user_memory': perception.get('user_memory', {}),
            'conversation_memory': perception.get('conversation_memory', {})
        }
        prompt = get_prompt_by_template('poetry_game', **filtered_perception)
        res = self.llm.chat(
            messages=[LLMMessage(role="system", content=prompt)])
        return res

    def act(self, action_plan: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行阶段：执行决策，生成回复
        根据 action_plan 中的 action_type 执行相应操作
        action_type:
            - search_by_keyword: 根据关键词搜索诗词
            - search_by_vector: 根据向量搜索诗词
            - update_memory: 更新会话记忆
            - update_user_memory: 更新用户记忆
            - send_message: 发送消息给用户，结束本轮对话
        根据action_type的类型，action_plan中有不同的参数
        返回一个动作结果
        """
        action_result = {'action_type': action_plan['action_type']}
        if action_plan['action_type'] == 'search_by_keyword':
            # 执行诗词关键词搜索
            poems = self.poetry_service.search(
                query=action_plan['keyword'],
                search_type='keyword',
                top_k=action_plan['top_k'],
            )
            poem_texts = [
                f"{poem['title']} - {poem['writer']}\n{poem['content']}"
                for poem in poems
            ]
            result = "\n\n".join(poem_texts)
            action_result['result'] = result
        elif action_plan['action_type'] == 'search_by_vector':
            # 执行诗词向量搜索
            poems = self.poetry_service.search(
                query=action_plan['keyword'],
                search_type='vector',
                top_k=action_plan['top_k'],
            )
            poem_texts = [
                f"{poem['title']} - {poem['writer']}\n{poem['content']}"
                for poem in poems
            ]
            result = "\n\n".join(poem_texts)
            action_result['result'] = result
        elif action_plan['action_type'] == 'update_memory':
            # 更新会话记忆
            self.conversation_service.update_conversation_memory(
                conversation_id=self.conversation_id,
                user_id=self.user_id,
                memory_data=action_plan['memory_data'],
            )
            action_result['result'] = '更新成功'
        elif action_plan['action_type'] == 'update_user_memory':
            # 更新用户长期记忆
            self.mysql_service.create_or_update_agent_user_memory(
                agent_id=self.agent_id,
                user_id=self.user_id,
                memory_data=action_plan['memory_data'],
            )
            action_result['result'] = '更新成功'
        elif action_plan['action_type'] == 'send_message':
            # 发送消息给用户
            message = self.message_service.create_message(
                user_id=self.user_id,
                conversation_id=self.conversation_id,
                role='assistant',
                status='done',
                content=action_plan['message'],
            )
            action_result['result'] = message

        return action_result

    def run(self, user_input: str, **kwargs) -> None:
        '''
        循环执行
        '''
        # 创建用户消息
        user_message_id = self.message_service.create_message(
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            role='user',
            status='pending',
            content=user_input,
        )
        # 感知阶段
        perception = self.perceive(user_input, **kwargs)
        # 循环
        loop_count = 0
        while loop_count < self.max_iterations:
            loop_count += 1
            # 思考阶段
            action_plan_str = self.think(perception, **kwargs)
            # 解析行动计划
            try:
                action_plan = eval(action_plan_str)
            except Exception as e:
                action_plan = {
                    'action_type': 'send_message',
                    'message': '抱歉，我暂时无法处理您的请求。'
                }
            # 执行阶段
            action_result = self.act(action_plan, **kwargs)
            # 更新感知信息
            perception['tools_call_history'].append({
                'action_plan':
                action_plan,
                'action_result':
                action_result,
            })
            # 如果是发送消息，结束循环
            if action_plan['action_type'] == 'send_message':
                break
        self.message_service.update_message_status(
            message_id=user_message_id,
            status='done',
        )
