"""
定义各种大语言模型(LLM)调用时使用的提示(prompt)模板
"""

# 诗词相关提示模板
POETRY_GENERATION_PROMPT = """
请根据以下要求创作一首诗词：
主题：{theme}
风格：{style}
格式要求：{format_requirement}

请确保诗词符合韵律和意境。
"""

POETRY_EXPLANATION_PROMPT = """
请对以下诗词进行详细解释：
诗词内容：{poetry_content}

请从以下几个方面进行分析：
1. 诗词大意
2. 创作背景
3. 艺术手法
4. 情感表达
"""

POETRY_RHYME_PROMPT = """
请完成下面的诗句接龙任务：
当前诗句：{current_line}
请接出下一句，要求：{requirements}
"""

# 对话类提示模板
CONVERSATION_SYSTEM_PROMPT = """
你是一个专业的中国古典诗词助手，专门帮助用户了解和学习中国古典诗词。
你需要保持专业性，对于非诗词相关的问题可以礼貌地引导回到诗词话题。
"""

ANSWER_TO_POETRY_QUESTION_PROMPT = """
根据以下上下文信息回答用户的问题：
上下文：{context}
用户问题：{question}

请简洁明了地回答用户问题，如果无法根据上下文回答，请说明"根据现有信息无法回答此问题"。
"""

# 飞花令提示模板
FLY_FLOWER_ORDER_PROMPT = """
现在开始玩飞花令游戏。
关键字是："{keyword}"
请提供一句含有"{keyword}"字的诗句，该字必须出现在诗句中且符合规则。
你可以选择回应或等待其他参与者的回应。
"""

# 诗词接龙提示模板
POETRY_CHAIN_PROMPT = """
现在开始诗词接龙游戏。
上一句是："{previous_line}"
请根据这句诗的意境或某个关键字，接出下一联或者下一句诗词。
"""

# 通用模板
GENERAL_QA_PROMPT = """
问题：{question}
请提供准确且相关的答案。
"""

# RAG相关提示模板
RAG_RETRIEVAL_PROMPT = """
根据以下上下文信息回答问题：
上下文：{context_str}
问题：{query_str}

请根据提供的上下文信息回答问题，如果问题与上下文无关或上下文信息不足以回答问题，
请明确说明无法根据给定信息回答。
"""

# 可选的行动
ACTIONS = """
action_type:
- search_by_keyword: 根据关键词搜索诗词,行动参数有keyword(搜索关键词)和top_k(返回结果数量)
- search_by_vector: 根据向量搜索诗词,行动参数有keyword(搜索关键词)和top_k(返回结果数量)
- update_memory: 更新会话记忆,行动参数有memory_data(记忆数据，用json格式保存)
- update_user_memory: 更新用户记忆,行动参数有memory_data(记忆数据，用json格式保存)
- send_message: 发送消息给用户

注意，返回的JSON对象格式为：
{
  "action_type": "search_by_keyword",
  ...(更多参数)
}
"""

# Agent系统提示
AGENT_SYSTEM_MESSAGE = """
你是一个智能诗词助手，你的职责是：
1. 帮助用户进行诗词相关的游戏活动，如飞花令、诗词接龙等，具体游戏规则见下文。
2. 确保用户体验良好，并确保游戏规则清晰且可理解。

# 游戏规则
具体游戏规则：
{game_rules}

# 行动
你可以采取的行动：
action_type:
- search_by_keyword: 根据关键词搜索诗词,行动参数有keyword(搜索关键词)和top_k(返回结果数量)
- search_by_vector: 根据向量搜索诗词,行动参数有keyword(搜索关键词)和top_k(返回结果数量)
- update_memory: 更新会话记忆,行动参数有memory_data(记忆数据，用json格式保存)
- update_user_memory: 更新用户记忆,行动参数有memory_data(记忆数据，用json格式保存)
- send_message: 发送消息给用户,行动参数有message(消息内容)


# 会话记录
以下是你的对话记录：
{recent_messages}

# 用户记忆信息
下面是关于用户的长期记忆信息：
{user_memory}

# 会话记忆信息
下面是当前会话的历史记忆信息：
{conversation_memory}

# 用户输入
用户当前输入：{user_input}

# 行动历史
以下是本轮会话中你的行动历史：
{tools_calls_history}

# 具体处理过程（参考下面的步骤处理）
1. 理解用户输入，并理解其意图。
2. 根据用户意图，选择合适的工具进行调用。例如，当飞“月”字时，调用"search_by_keyword"工具，参数为"月"和10。
3. 调用工具，获取工具返回结果。
4. 根据工具返回结果，生成答案。
5. 思考是否需要更新会话记忆（保存当前游戏轮数等信息）和用户记忆（记录用户行为习惯）。
  - 如果需要更新会话记忆，请将更新后的记忆数据保存在"memory_data"参数中，并返回"update_memory"动作。
  - 如果需要更新用户记忆，请将更新后的记忆数据保存在"memory_data"参数中，并返回"update_user_memory"动作。
6. 返回动作。

# 返回格式要求
返回一个python可以解析的List对象，列表中的每个元素都是一个JSON对象，内容是行动计划和参数，格式示例：
[
{{
  'action_type': 'send_message',
  'message': '请输入本轮飞的字：'
}}
]

# 提示
1. 确保你的回答符合用户要求。
2. 注意会话记忆和用户记忆要保持简洁，如无必要无需修改。
3. 先考虑更新会话记忆和用户记忆信息再回复。
4. 不要直接回复文本，按要求回复一个List列表，列表的每个元素都是一个JSON对象。
5. 搜索得到的诗词都使用过了的话可以考虑增大top_k参数。
6. 用户提出意见或要求时，要考虑把要求添加到用户记忆或会话记忆中。
7. 注意memory_data参数也是JSON对象，例如:
"memory_data": {{
  "key": "value"
}}

"""

# 错误处理提示
ERROR_HANDLING_PROMPT = """
遇到无法处理的请求时，请礼貌地告知用户：
"抱歉，我暂时无法处理您的请求。我是专注于中国古典诗词的助手，如果您有关于诗词的问题，我会很乐意为您解答。"
"""


def get_prompt_by_template(template_name: str, **kwargs) -> str:
    """
    根据模板名称和参数获取具体的prompt字符串
    
    Args:
        template_name: 模板名称
        **kwargs: 模板中需要替换的参数
        
    Returns:
        替换后的prompt字符串
    """
    templates = {
        "poetry_generation": POETRY_GENERATION_PROMPT,
        "poetry_explanation": POETRY_EXPLANATION_PROMPT,
        "poetry_rhyme": POETRY_RHYME_PROMPT,
        "conversation_system": CONVERSATION_SYSTEM_PROMPT,
        "answer_to_poetry_question": ANSWER_TO_POETRY_QUESTION_PROMPT,
        "fly_flower_order": FLY_FLOWER_ORDER_PROMPT,
        "poetry_chain": POETRY_CHAIN_PROMPT,
        "general_qa": GENERAL_QA_PROMPT,
        "rag_retrieval": RAG_RETRIEVAL_PROMPT,
        "agent_system_message": AGENT_SYSTEM_MESSAGE,
        "error_handling": ERROR_HANDLING_PROMPT,
        "poetry_game": AGENT_SYSTEM_MESSAGE,
    }
    # print(kwargs)
    if template_name not in templates:
        raise ValueError(f"Unknown template name: {template_name}")

    template = templates[template_name]
    return template.format(**kwargs)
