from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel

# 配置日志
logger = logging.getLogger(__name__)

# 导入服务层
from services.hint.socratic_hint import generate_socratic_hint
from services.ai.ai_service import get_ai_hint
from services.conversation.connection_manager import ConnectionManager

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
