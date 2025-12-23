from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel

# 配置日志
logger = logging.getLogger(__name__)

# 导入服务层
from services.socratic_hint import generate_socratic_hint
from services.ai_service import get_ai_hint

# WebSocket消息模型
class WebSocketMessage(BaseModel):
    type: str
    content: Optional[str] = None
    metadata: Optional[Dict] = None

class StepMessage(WebSocketMessage):
    type: str = "step"
    content: str

class ErrorReportMessage(WebSocketMessage):
    type: str = "error_report"
    content: str

class PingMessage(WebSocketMessage):
    type: str = "ping"
    content: Optional[str] = None

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.last_ping: Dict[str, float] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """建立新的WebSocket连接"""
        await websocket.accept()
        if client_id is None:
            client_id = str(id(websocket))
        self.active_connections[client_id] = websocket
        self.last_ping[client_id] = 0
        return client_id
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.last_ping:
            del self.last_ping[client_id]
    
    async def send_personal_message(self, message: dict, client_id: str):
        """向特定客户端发送消息"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        for connection in self.active_connections.values():
            await connection.send_json(message)
    
    def update_ping(self, client_id: str):
        """更新客户端的最后心跳时间"""
        if client_id in self.last_ping:
            self.last_ping[client_id] = 0
    
    def check_timeouts(self, timeout: int = 30):
        """检查客户端连接超时，返回超时的客户端ID列表"""
        import time
        current_time = time.time()
        timed_out = []
        
        for client_id, last_ping_time in self.last_ping.items():
            if current_time - last_ping_time > timeout:
                timed_out.append(client_id)
        
        return timed_out

# 创建连接管理器实例
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点处理函数"""
    client_id = await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            raw_data = await websocket.receive_json()
            
            try:
                # 验证消息格式
                message = WebSocketMessage(**raw_data)
                
                # 根据消息类型处理
                if message.type == 'step':
                    # 处理解题步骤
                    step_msg = StepMessage(**raw_data)
                    step_content = step_msg.content
                    
                    # 1. 首先尝试本地苏格拉底式提问规则
                    hint = generate_socratic_hint(step_content)
                    
                    # 2. 如果本地规则没有匹配，调用AI服务
                    if not hint:
                        hint = await get_ai_hint(step_content)
                    
                    # 3. 返回提示给客户端
                    await manager.send_personal_message({
                        'type': 'hint',
                        'content': hint
                    }, client_id)
                
                elif message.type == 'error_report':
                    # 处理错误报告（可扩展）
                    error_msg = ErrorReportMessage(**raw_data)
                    error_data = error_msg.content
                    # 可以在这里记录错误数据到数据库
                    await manager.send_personal_message({
                        'type': 'acknowledge',
                        'content': '错误报告已接收'
                    }, client_id)
                
                elif message.type == 'ping':
                    # 心跳检测
                    ping_msg = PingMessage(**raw_data)
                    manager.update_ping(client_id)
                    await manager.send_personal_message({
                        'type': 'pong'
                    }, client_id)
                
                else:
                    # 未知消息类型
                    await manager.send_personal_message({
                        'type': 'error',
                        'content': f'未知消息类型: {message.type}'
                    }, client_id)
                
            except ValueError as ve:
                # 消息格式错误
                logger.warning(f"WebSocket消息格式错误: {str(ve)}")
                await manager.send_personal_message({
                    'type': 'error',
                    'content': f'消息格式错误: {str(ve)}'
                }, client_id)
            except Exception as e:
                # 其他处理错误
                logger.error(f"处理WebSocket消息时出错: {str(e)}")
                await manager.send_personal_message({
                    'type': 'error',
                    'content': f'处理消息时出错: {str(e)}'
                }, client_id)
                
    except WebSocketDisconnect:
        # 客户端断开连接
        manager.disconnect(client_id)
    except Exception as e:
        # 处理其他异常
        logger.error(f"WebSocket错误: {str(e)}")
        await manager.send_personal_message({
            'type': 'error',
            'content': f'服务器错误: {str(e)}'
        }, client_id)
        manager.disconnect(client_id)
