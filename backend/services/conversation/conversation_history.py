from typing import Dict, List, Optional, Any
from datetime import datetime


class ConversationHistory:
    """对话历史管理器，用于管理用户和AI之间的对话历史"""
    
    def __init__(self, max_history_length: int = 20):
        """
        初始化对话历史管理器
        
        Args:
            max_history_length: 最大历史记录长度，超过后会自动裁剪
        """
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_length = max_history_length
    
    def add_message(self, client_id: str, role: str, content: str, message_type: str = "text") -> None:
        """
        添加对话消息
        
        Args:
            client_id: 客户端ID
            role: 角色（user, ai, system）
            content: 消息内容
            message_type: 消息类型（text, hint, error等）
        """
        if client_id not in self.conversations:
            self.conversations[client_id] = []
        
        message = {
            "role": role,
            "content": content,
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.conversations[client_id].append(message)
        
        # 裁剪历史记录，保持在最大长度以内
        if len(self.conversations[client_id]) > self.max_history_length:
            self.conversations[client_id] = self.conversations[client_id][-self.max_history_length:]
    
    def get_history(self, client_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            client_id: 客户端ID
            limit: 返回的最大消息数，None表示返回全部
        
        Returns:
            List[Dict[str, Any]]: 对话历史列表
        """
        history = self.conversations.get(client_id, [])
        if limit and len(history) > limit:
            return history[-limit:]
        return history
    
    def get_context(self, client_id: str, recent_messages: int = 5) -> str:
        """
        获取对话上下文，用于AI生成响应
        
        Args:
            client_id: 客户端ID
            recent_messages: 最近的消息数，用于生成上下文
        
        Returns:
            str: 格式化的对话上下文
        """
        history = self.get_history(client_id, recent_messages)
        context = ""
        
        for message in history:
            if message["role"] == "user":
                context += f"学生: {message['content']}\n"
            elif message["role"] == "ai":
                context += f"老师: {message['content']}\n"
        
        return context.strip()
    
    def clear_history(self, client_id: str) -> None:
        """
        清除对话历史
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.conversations:
            del self.conversations[client_id]
    
    def remove_client(self, client_id: str) -> None:
        """
        移除客户端的对话历史
        
        Args:
            client_id: 客户端ID
        """
        self.clear_history(client_id)
    
    def get_client_count(self) -> int:
        """
        获取当前管理的客户端数量
        
        Returns:
            int: 客户端数量
        """
        return len(self.conversations)
