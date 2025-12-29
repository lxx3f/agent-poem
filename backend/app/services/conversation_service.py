from typing import List, Dict, Any, Optional, Literal

from backend.app.core.exceptions import BusinessException
from backend.app.services.mysql_service import MySQLService

RoleType = Literal["user", "assistant", "system"]


class ConversationService:

    def __init__(self, mysql_service: MySQLService = MySQLService()):
        self.mysql_service = mysql_service

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
        if not self.mysql_service.user_exists(user_id):
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
        if not self.mysql_service.conversation_belongs_to_user(
                conversation_id,
                user_id,
        ):
            raise BusinessException(
                code=403,
                message="Conversation not found or access denied",
            )

    # =====================
    # Conversation
    # =====================

    def create_conversation(
        self,
        user_id: int,
        title: str,
    ) -> int:
        """
        创建新会话，返回 conversation_id
        """

        self._check_user_exists(user_id)
        return self.mysql_service.create_conversation(
            user_id=user_id,
            title=title,
        )

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ):
        """
        删除会话
        """
        self._check_conversation_owner(conversation_id, user_id)
        self.mysql_service.delete_conversation(conversation_id)

    def list_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出用户的会话列表
        """

        self._check_user_exists(user_id)

        return self.mysql_service.get_conversations_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
