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
from services.conversation.conversation_history import ConversationHistory


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

# 创建对话历史管理器实例
conversation_history = ConversationHistory()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点处理函数"""
    client_id = await manager.connect(websocket)

    try:
        while True:
            # 接收客户端消息
            raw_data = await websocket.receive_json()
            logger.info(f"raw_data: {raw_data}")
            try:
                # 验证消息格式
                message = WebSocketMessage(**raw_data)

                # 根据消息类型处理
                if message.type == "step" or message.type == "chat":
                    # 处理解题步骤（chat类型作为step的别名）
                    # 确保type字段为"step"以匹配StepMessage模型
                    step_data = raw_data.copy()
                    step_data["type"] = "step"
                    step_msg = StepMessage(**step_data)
                    step_content = step_msg.content

                    # 提取学生的实际输入部分（从提示词中提取）
                    # step_content 格式通常是：
                    # "你是一个数学解题助手...\n\n题目：...\n\n学生当前的解题步骤：\n{实际输入}\n\n请给出..."
                    student_input = None
                    if "学生当前的解题步骤：" in step_content:
                        # 提取学生实际输入部分
                        parts = step_content.split("学生当前的解题步骤：")
                        if len(parts) > 1:
                            # 获取学生输入部分，去除后续的提示文本
                            student_part = parts[1].split("\n\n请给出")[0].strip()
                            # 如果学生输入不为空且不是占位符，使用它
                            if (
                                student_part
                                and student_part != "（学生还没有开始解题）"
                            ):
                                student_input = student_part

                    # 记录用户消息到对话历史（使用原始 step_content，保持完整上下文）
                    conversation_history.add_message(
                        client_id=client_id,
                        role="user",
                        content=step_content,
                        message_type="step",
                    )

                    # 1. 首先尝试本地苏格拉底式提问规则（只基于学生的实际输入，不包括题目）
                    hint = None
                    hint_keyword = None
                    hint_source = None

                    if student_input:
                        # 获取历史反馈统计，用于优化提示选择
                        feedback_stats = None
                        try:
                            from models.base import SessionLocal
                            from sqlalchemy import func, case
                            from models.models import HintFeedback

                            db = SessionLocal()
                            try:
                                # 统计每个关键词的赞/踩数量
                                stats_query = (
                                    db.query(
                                        HintFeedback.hint_keyword,
                                        func.sum(
                                            case(
                                                (HintFeedback.feedback_type == 1, 1),
                                                else_=0,
                                            )
                                        ).label("likes"),
                                        func.sum(
                                            case(
                                                (HintFeedback.feedback_type == 2, 1),
                                                else_=0,
                                            )
                                        ).label("dislikes"),
                                        func.count(HintFeedback.id).label("total"),
                                    )
                                    .filter(HintFeedback.hint_keyword.isnot(None))
                                    .group_by(HintFeedback.hint_keyword)
                                    .all()
                                )

                                feedback_stats = {}
                                for row in stats_query:
                                    keyword = row.hint_keyword
                                    likes = row.likes or 0
                                    dislikes = row.dislikes or 0
                                    total = row.total or 0
                                    score = likes / total if total > 0 else 0.5
                                    feedback_stats[keyword] = {
                                        "likes": likes,
                                        "dislikes": dislikes,
                                        "total": total,
                                        "score": score,
                                    }
                            finally:
                                db.close()
                        except Exception as e:
                            logger.warning(f"获取反馈统计失败: {str(e)}")
                            feedback_stats = None

                        # 生成提示，返回提示内容和匹配的关键词
                        hint_result = generate_socratic_hint(
                            student_input, feedback_stats
                        )
                        if hint_result[0]:
                            hint, hint_keyword = hint_result
                            hint_source = "socratic"

                    # 2. 如果本地规则没有匹配，调用AI服务
                    if not hint:
                        # 获取对话历史（转换为 messages 格式）
                        # 注意：获取历史时排除当前刚添加的用户消息，只获取之前的对话
                        history = conversation_history.get_history(client_id, limit=10)
                        # 转换为模型需要的格式，排除最后一条（当前用户消息）
                        history_messages = []
                        # 只取历史记录，排除最后一条（当前刚添加的用户消息）
                        for msg in history[:-1]:  # 排除最后一条，因为那是当前消息
                            if msg["role"] == "user":
                                history_messages.append(
                                    {"role": "user", "content": msg["content"]}
                                )
                            elif msg["role"] == "ai":
                                history_messages.append(
                                    {"role": "assistant", "content": msg["content"]}
                                )

                        # 调用AI服务，传入对话历史
                        hint = await get_ai_hint(
                            step_content, conversation_history=history_messages
                        )
                        hint_source = "ai"

                    # 记录AI回复到对话历史
                    conversation_history.add_message(
                        client_id=client_id,
                        role="ai",
                        content=hint,
                        message_type="hint",
                    )

                    logger.info(
                        f"Hint: {hint}, Source: {hint_source}, Keyword: {hint_keyword}"
                    )
                    # 3. 返回提示给客户端（包含元数据，用于反馈）
                    await manager.send_personal_message(
                        {
                            "type": "hint",
                            "content": hint,
                            "metadata": {
                                "source": hint_source,
                                "keyword": hint_keyword,
                                "question_id": None,  # 前端会使用 currentQuestionId
                            },
                        },
                        client_id,
                    )

                elif message.type == "error_report":
                    # 处理错误报告（可扩展）
                    error_msg = ErrorReportMessage(**raw_data)
                    error_data = error_msg.content
                    # 可以在这里记录错误数据到数据库
                    await manager.send_personal_message(
                        {"type": "acknowledge", "content": "错误报告已接收"}, client_id
                    )

                elif message.type == "ping":
                    # 心跳检测
                    ping_msg = PingMessage(**raw_data)
                    manager.update_ping(client_id)
                    await manager.send_personal_message({"type": "pong"}, client_id)

                elif message.type == "reset":
                    # 重置会话，清除对话历史
                    conversation_history.clear_history(client_id)
                    await manager.send_personal_message(
                        {"type": "acknowledge", "content": "会话已重置"}, client_id
                    )

                elif message.type == "history":
                    # 获取历史记录
                    history = conversation_history.get_history(client_id)
                    await manager.send_personal_message(
                        {"type": "history", "content": history}, client_id
                    )

                else:
                    # 未知消息类型
                    await manager.send_personal_message(
                        {"type": "error", "content": f"未知消息类型: {message.type}"},
                        client_id,
                    )

            except ValueError as ve:
                # 消息格式错误
                logger.warning(f"WebSocket消息格式错误: {str(ve)}")
                await manager.send_personal_message(
                    {"type": "error", "content": f"消息格式错误: {str(ve)}"}, client_id
                )
            except Exception as e:
                # 其他处理错误
                logger.error(f"处理WebSocket消息时出错: {str(e)}")
                await manager.send_personal_message(
                    {"type": "error", "content": f"处理消息时出错: {str(e)}"}, client_id
                )

    except WebSocketDisconnect:
        # 客户端断开连接
        manager.disconnect(client_id)
        # 可选：保留对话历史一段时间，或者立即清除
        # conversation_history.remove_client(client_id)  # 如果需要立即清除
    except Exception as e:
        # 处理其他异常
        logger.error(f"WebSocket错误: {str(e)}")
        await manager.send_personal_message(
            {"type": "error", "content": f"服务器错误: {str(e)}"}, client_id
        )
        manager.disconnect(client_id)
