
import os
import sys
import logging
import json
from typing import Dict, List
from urllib.parse import parse_qs

# 添加项目路径到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins'))

from django.core.asgi import get_asgi_application
from plugins.mlops import ChatClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("asgi_server")

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# 获取Django ASGI应用
django_asgi_app = get_asgi_application()

# 初始化聊天客户端
chat_client = ChatClient()

# 存储活跃连接和会话信息
active_connections = {}
session_history = {}

class WebSocketMiddleware:
    """WebSocket中间件，处理WebSocket连接"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 检查是否是WebSocket连接
        if scope["type"] == "websocket":
            # 只处理/ws/路径的WebSocket连接
            path = scope.get("path", "")
            if path.startswith("/ws/"):
                await self.websocket_handler(scope, receive, send)
            else:
                # 其他WebSocket连接，关闭连接
                await send({
                    "type": "websocket.close",
                    "code": 1003,
                    "reason": "Unsupported WebSocket path"
                })
        else:
            # 非WebSocket连接，传递给Django处理
            await self.app(scope, receive, send)

    async def websocket_handler(self, scope, receive, send):
        """处理WebSocket连接"""
        # 获取WebSocket连接对象
        websocket = WebSocketConnection(scope, receive, send)
        client_id = id(websocket)
        active_connections[client_id] = websocket

        # 初始化会话历史
        if client_id not in session_history:
            session_history[client_id] = []

        logger.info(f"WebSocket客户端 {client_id} 已连接，当前连接数: {len(active_connections)}")

        try:
            # 发送欢迎消息
            await websocket.send_json({
                "type": "system",
                "message": "连接成功！您可以开始对话了。"
            })

            # 处理客户端消息
            await self.handle_client_messages(websocket, client_id)
        except Exception as e:
            logger.error(f"处理WebSocket客户端 {client_id} 时出错: {e}")
        finally:
            # 清理连接
            if client_id in active_connections:
                del active_connections[client_id]
            logger.info(f"WebSocket客户端 {client_id} 已断开，当前连接数: {len(active_connections)}")

    async def handle_client_messages(self, websocket, client_id):
        """处理客户端消息"""
        while True:
            try:
                # 接收消息
                message = await websocket.receive()
                data = json.loads(message) if isinstance(message, str) else message

                message_type = data.get("type", "chat")

                if message_type == "chat":
                    # 处理聊天消息
                    user_message = data.get("message", "")
                    if not user_message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "消息内容不能为空"
                        })
                        continue

                    # 添加用户消息到历史记录
                    session_history[client_id].append({
                        "role": "user",
                        "content": user_message
                    })

                    # 发送处理中状态
                    await websocket.send_json({
                        "type": "status",
                        "message": "正在处理您的请求..."
                    })

                    # 调用AI模型获取回复
                    try:
                        # 使用流式响应
                        response_text = ""
                        await websocket.send_json({
                            "type": "ai_response_start",
                            "message": "AI回复开始"
                        })

                        for chunk in chat_client.chat_completion(
                            messages=session_history[client_id],
                            stream=True
                        ):
                            if chunk.get("choices"):
                                content = chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    response_text += content
                                    # 发送部分响应
                                    await websocket.send_json({
                                        "type": "ai_response_chunk",
                                        "content": content
                                    })

                        # 添加AI回复到历史记录
                        session_history[client_id].append({
                            "role": "assistant",
                            "content": response_text
                        })

                        # 发送响应结束标记
                        await websocket.send_json({
                            "type": "ai_response_end",
                            "message": "AI回复结束"
                        })

                    except Exception as e:
                        logger.error(f"调用AI模型时出错: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "处理您的请求时出错，请稍后再试"
                        })

                elif message_type == "reset":
                    # 重置会话历史
                    session_history[client_id] = []
                    await websocket.send_json({
                        "type": "system",
                        "message": "会话已重置"
                    })

                elif message_type == "history":
                    # 发送会话历史
                    await websocket.send_json({
                        "type": "history",
                        "history": session_history[client_id]
                    })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"未知消息类型: {message_type}"
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的JSON格式"
                })
            except Exception as e:
                logger.error(f"处理消息时出错: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "处理消息时出错"
                })


class WebSocketConnection:
    """WebSocket连接包装器"""

    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send

    async def receive(self):
        """接收消息"""
        message = await self.receive()
        return message.get("text", "") if message["type"] == "websocket.receive" else ""

    async def send_text(self, text):
        """发送文本消息"""
        await self.send({
            "type": "websocket.send",
            "text": text
        })

    async def send_json(self, data):
        """发送JSON消息"""
        await self.send_text(json.dumps(data))

    async def close(self):
        """关闭连接"""
        await self.send({
            "type": "websocket.close"
        })


# 创建ASGI应用
asgi_app = WebSocketMiddleware(django_asgi_app)
