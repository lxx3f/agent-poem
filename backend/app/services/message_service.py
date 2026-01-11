from typing import List, Dict, Any, Optional, Literal

from app.core.exceptions import BusinessException
from app.services.mysql_service import MySQLService

RoleType = Literal["user", "assistant", "system"]
StatusType = Literal["pending", "done", "failed"]


class MessageService:

    def __init__(self, mysql_service: MySQLService = MySQLService()):
        pass

    # =====================
    # 校验相关
    # =====================
    def _check_user_exists(self, user_id: int):
        '''
        校验用户是否存在
        
        :param self: 说明
        :param user_id: 说明
        :type user_id: int
        '''
        mysql_service = MySQLService()
        if not mysql_service.user_exists(user_id):
            raise BusinessException(
                code=404,
                message="User does not exist",
            )

    def _check_conversation_owner(
        self,
        conversation_id: int,
        user_id: int,
    ):
        '''
        校验会话归属, 确保会话属于该用户,否则抛出异常
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :param user_id: 说明
        :type user_id: int
        '''
        mysql_service = MySQLService()
        if not mysql_service.conversation_belongs_to_user(
                conversation_id,
                user_id,
        ):
            raise BusinessException(
                code=403,
                message="Conversation not found or access denied",
            )

    def _check_message_owner(
        self,
        message_id: int,
        user_id: int,
    ):
        '''
        校验消息归属, 确保消息属于该用户,否则抛出异常
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param user_id: 说明
        :type user_id: int
        '''
        mysql_service = MySQLService()
        if not mysql_service.message_belongs_to_user(
                message_id,
                user_id,
        ):
            raise BusinessException(
                code=403,
                message="Message not found or access denied",
            )

    def _check_message_exists(self, message_id: int):
        '''
        校验消息是否存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        '''
        mysql_service = MySQLService()
        if not mysql_service.message_exists(message_id):
            raise BusinessException(
                code=404,
                message="Message does not exist",
            )

    # =====================
    # Message
    # =====================
    def get_messages_by_conversation(
        self,
        conversation_id: int,
        user_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        '''
        获取会话消息列表
        
        :param conversation_id: 会话ID
        :type conversation_id: int
        :param user_id: 用户ID
        :type user_id: int
        :param limit: 限制数量
        :type limit: int
        :return: 消息列表
        :rtype: List[Dict[str, Any]]
        '''
        mysql_service = MySQLService()
        # 1. 校验
        self._check_user_exists(user_id)
        self._check_conversation_owner(conversation_id, user_id)

        # 2. 获取消息列表
        messages = mysql_service.get_messages_by_conversation(
            conversation_id=conversation_id,
            limit=limit,
        )
        return messages

    def create_message(
        self,
        conversation_id: int,
        user_id: int,
        role: RoleType,
        status: StatusType,
        content: str,
    ) -> int:
        '''
        创建新消息，返回 message_id
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :param user_id: 说明
        :type user_id: int
        :param role: 说明
        :type role: RoleType
        :param content: 说明
        :type content: str
        :return: 说明
        :rtype: int
        '''
        mysql_service = MySQLService()
        # 1. 校验
        self._check_user_exists(user_id)
        self._check_conversation_owner(conversation_id, user_id)

        # 2. 创建消息
        message_id = mysql_service.create_message(
            conversation_id=conversation_id,
            role=role,
            status=status,
            content=content,
        )
        return message_id

    def update_message_status(
        self,
        message_id: int,
        status: StatusType,
    ):
        '''
        更新消息状态
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param status: 说明
        :type status: StatusType
        '''
        mysql_service = MySQLService()
        mysql_service.update_message_status(
            message_id=message_id,
            status=status,
        )

    def update_message_content(
        self,
        message_id: int,
        content: str,
    ):
        '''
        更新消息内容
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param content: 说明
        :type content: str
        '''
        mysql_service = MySQLService()
        self._check_message_exists(message_id)
        mysql_service.update_message_content(
            message_id=message_id,
            content=content,
        )

    def get_message_by_id(
        self,
        user_id: int,
        message_id: int,
    ) -> Dict[str, Any]:
        '''
        根据 message_id 获取消息
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :return: 说明
        :rtype: Optional[Dict[str, Any]]
        '''
        # 校验
        mysql_service = MySQLService()
        self._check_user_exists(user_id)
        self._check_message_exists(message_id)
        self._check_message_owner(message_id, user_id)
        return mysql_service.get_message_by_id(message_id=message_id)
