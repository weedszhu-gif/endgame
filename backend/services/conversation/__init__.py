# 对话管理模块
from .connection_manager import ConnectionManager
from .conversation_history import ConversationHistory

# 创建连接管理器实例
connection_manager = ConnectionManager()

# 创建对话历史管理器实例
conversation_history = ConversationHistory()

__all__ = ["connection_manager", "conversation_history", "ConnectionManager", "ConversationHistory"]
