import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_websocket_connection():
    """测试WebSocket连接"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送ping消息
            await websocket.send_json({"type": "ping"})
            # 接收pong响应
            response = await websocket.receive_json()
            assert response == {"type": "pong"}


@pytest.mark.asyncio
async def test_websocket_step_message():
    """测试WebSocket step消息处理"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送step消息
            await websocket.send_json({"type": "step", "content": "设未知数x"})
            # 接收hint响应
            response = await websocket.receive_json()
            assert response["type"] == "hint"
            assert isinstance(response["content"], str)


@pytest.mark.asyncio
async def test_websocket_error_report():
    """测试WebSocket error_report消息处理"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送error_report消息
            await websocket.send_json({"type": "error_report", "content": "测试错误报告"})
            # 接收acknowledge响应
            response = await websocket.receive_json()
            assert response == {"type": "acknowledge", "content": "错误报告已接收"}


@pytest.mark.asyncio
async def test_websocket_invalid_message():
    """测试WebSocket无效消息处理"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送无效消息（缺少type字段）
            await websocket.send_json({"content": "无效消息"})
            # 接收error响应
            response = await websocket.receive_json()
            assert response["type"] == "error"
            assert "消息格式错误" in response["content"]


@pytest.mark.asyncio
async def test_websocket_unknown_message_type():
    """测试WebSocket未知消息类型处理"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送未知类型消息
            await websocket.send_json({"type": "unknown_type", "content": "未知类型消息"})
            # 接收error响应
            response = await websocket.receive_json()
            assert response["type"] == "error"
            assert "未知消息类型" in response["content"]


@pytest.mark.asyncio
async def test_websocket_step_message_without_content():
    """测试WebSocket step消息缺少content字段处理"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.websocket_connect("/ws") as websocket:
            # 发送缺少content字段的step消息
            await websocket.send_json({"type": "step"})
            # 接收error响应
            response = await websocket.receive_json()
            assert response["type"] == "error"
            assert "消息格式错误" in response["content"]


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "服务正常运行"}


@pytest.mark.asyncio
async def test_root_endpoint():
    """测试根路径端点"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "欢迎使用初中数学残局挑战系统 API"}
