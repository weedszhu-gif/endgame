import asyncio
import json
import logging
import os
import sys
import websockets
from typing import Dict, List

# 添加项目路径到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins"))

from mlops import ChatClient

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("websocket_server")

# 初始化聊天客户端
chat_client = ChatClient()

# 存储活跃连接和会话信息
active_connections = {}
session_history = {}


class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients = set()

    async def register(self, websocket, path):
        """注册新的WebSocket连接"""
        self.clients.add(websocket)
        client_id = id(websocket)
        active_connections[client_id] = websocket

        # 初始化会话历史
        if client_id not in session_history:
            session_history[client_id] = []

        logger.info(f"客户端 {client_id} 已连接，当前连接数: {len(self.clients)}")

        try:
            # 发送欢迎消息
            await websocket.send(
                json.dumps(
                    {"type": "system", "message": "连接成功！您可以开始对话了。"}
                )
            )

            # 处理客户端消息
            await self.handle_client(websocket, client_id)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_id} 连接已关闭")
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 时出错: {e}")
        finally:
            # 清理连接
            self.clients.discard(websocket)
            if client_id in active_connections:
                del active_connections[client_id]
            logger.info(f"客户端 {client_id} 已断开，当前连接数: {len(self.clients)}")

    async def handle_client(self, websocket, client_id):
        """处理客户端消息"""
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get("type", "chat")

                if message_type == "chat":
                    # 处理聊天消息
                    user_message = data.get("message", "")
                    if not user_message:
                        await websocket.send(
                            json.dumps({"type": "error", "message": "消息内容不能为空"})
                        )
                        continue

                    # 添加用户消息到历史记录
                    session_history[client_id].append(
                        {"role": "user", "content": user_message}
                    )

                    # 发送处理中状态
                    await websocket.send(
                        json.dumps({"type": "status", "message": "正在处理您的请求..."})
                    )

                    # 调用AI模型获取回复
                    try:
                        # 使用流式响应
                        response_text = ""
                        await websocket.send(
                            json.dumps(
                                {"type": "ai_response_start", "message": "AI回复开始"}
                            )
                        )

                        for chunk in chat_client.chat_completion(
                            messages=session_history[client_id], stream=True
                        ):
                            if chunk.get("choices"):
                                content = (
                                    chunk["choices"][0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if content:
                                    response_text += content
                                    # 发送部分响应
                                    await websocket.send(
                                        json.dumps(
                                            {
                                                "type": "ai_response_chunk",
                                                "content": content,
                                            }
                                        )
                                    )

                        # 添加AI回复到历史记录
                        session_history[client_id].append(
                            {"role": "assistant", "content": response_text}
                        )

                        # 发送响应结束标记
                        await websocket.send(
                            json.dumps(
                                {"type": "ai_response_end", "message": "AI回复结束"}
                            )
                        )

                    except Exception as e:
                        logger.error(f"调用AI模型时出错: {e}")
                        await websocket.send(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": "处理您的请求时出错，请稍后再试",
                                }
                            )
                        )

                elif message_type == "reset":
                    # 重置会话历史
                    session_history[client_id] = []
                    await websocket.send(
                        json.dumps({"type": "system", "message": "会话已重置"})
                    )

                elif message_type == "history":
                    # 发送会话历史
                    await websocket.send(
                        json.dumps(
                            {"type": "history", "history": session_history[client_id]}
                        )
                    )

                else:
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "error",
                                "message": f"未知消息类型: {message_type}",
                            }
                        )
                    )

            except json.JSONDecodeError:
                await websocket.send(
                    json.dumps({"type": "error", "message": "无效的JSON格式"})
                )
            except Exception as e:
                logger.error(f"处理消息时出错: {e}")
                await websocket.send(
                    json.dumps({"type": "error", "message": "处理消息时出错"})
                )

    async def start_server(self):
        """启动WebSocket服务器"""
        logger.info(f"启动WebSocket服务器，监听 {self.host}:{self.port}")

        # 使用websockets库创建服务器
        server = await websockets.serve(
            self.register, self.host, self.port, ping_interval=20, ping_timeout=10
        )

        logger.info(f"WebSocket服务器已启动，地址: ws://{self.host}:{self.port}")
        await server.wait_closed()


# 主函数
async def main():
    server = WebSocketServer()
    await server.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止")
