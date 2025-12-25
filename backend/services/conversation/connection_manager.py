from fastapi import WebSocket
from typing import Dict, List
import logging

# 配置日志
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.last_ping: Dict[str, float] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """
        建立新的WebSocket连接
        
        Args:
            websocket: WebSocket实例
            client_id: 客户端ID，如为None则自动生成
            
        Returns:
            str: 客户端ID
        """
        await websocket.accept()
        if client_id is None:
            client_id = str(id(websocket))
        self.active_connections[client_id] = websocket
        self.last_ping[client_id] = 0
        logger.info(f"客户端 {client_id} 已连接，当前连接数: {len(self.active_connections)}")
        return client_id
    
    def disconnect(self, client_id: str) -> None:
        """
        断开WebSocket连接
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"客户端 {client_id} 已断开连接，当前连接数: {len(self.active_connections)}")
        if client_id in self.last_ping:
            del self.last_ping[client_id]
    
    async def send_personal_message(self, message: dict, client_id: str) -> None:
        """
        向特定客户端发送消息
        
        Args:
            message: 消息内容
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict) -> None:
        """
        向所有连接的客户端广播消息
        
        Args:
            message: 消息内容
        """
        for connection in self.active_connections.values():
            await connection.send_json(message)
    
    def update_ping(self, client_id: str) -> None:
        """
        更新客户端的最后心跳时间
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.last_ping:
            self.last_ping[client_id] = 0
    
    def check_timeouts(self, timeout: int = 30) -> List[str]:
        """
        检查客户端连接超时，返回超时的客户端ID列表
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            List[str]: 超时的客户端ID列表
        """
        import time
        current_time = time.time()
        timed_out = []
        
        for client_id, last_ping_time in self.last_ping.items():
            if current_time - last_ping_time > timeout:
                timed_out.append(client_id)
        
        return timed_out
    
    def get_connection_count(self) -> int:
        """
        获取当前连接数
        
        Returns:
            int: 当前连接数
        """
        return len(self.active_connections)
