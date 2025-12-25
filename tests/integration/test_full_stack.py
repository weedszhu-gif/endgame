#!/usr/bin/env python3
"""
整体测试脚本 - 测试前后端完整交互流程

该脚本测试初中数学残局挑战系统的完整功能，包括：
1. HTTP API接口测试
2. WebSocket通信测试
3. 多个初中数学例子的测试用例
"""

import asyncio
import httpx
import websockets
import json
from typing import Dict, List

# 配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
TIMEOUT = 10.0  # 增加超时时间
HTTP_TIMEOUT = 15.0  # 单独为HTTP请求设置更长的超时
WS_TIMEOUT = 10.0  # WebSocket超时

# 初中数学测试用例
MATH_TEST_CASES = [
    {
        "id": 1,
        "name": "一元一次方程",
        "content": "解方程：2x + 3 = 7",
        "expected_type": "hint"
    },
    {
        "id": 2,
        "name": "二元一次方程组",
        "content": "解方程组：\n2x + y = 5\nx - y = 1",
        "expected_type": "hint"
    },
    {
        "id": 3,
        "name": "二次方程",
        "content": "解方程：x² - 5x + 6 = 0",
        "expected_type": "hint"
    },
    {
        "id": 4,
        "name": "几何证明",
        "content": "在△ABC中，AB=AC，证明∠B=∠C",
        "expected_type": "hint"
    },
    {
        "id": 5,
        "name": "函数图像",
        "content": "画出函数y = 2x + 1的图像",
        "expected_type": "hint"
    }
]

async def test_http_api():
    """测试HTTP API接口"""
    print("=== 测试HTTP API接口 ===")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=HTTP_TIMEOUT) as client:
        # 测试健康检查
        print("1. 测试健康检查API...")
        response = await client.get("/api/health")
        assert response.status_code == 200, f"健康检查失败，状态码: {response.status_code}"
        result = response.json()
        assert result["status"] == "ok", f"健康检查状态异常: {result}"
        print("✅ 健康检查API测试通过")
        
        # 测试获取提示API
        print("\n2. 测试获取提示API...")
        for test_case in MATH_TEST_CASES[:3]:  # 测试前3个用例
            print(f"   测试用例 {test_case['id']}: {test_case['name']}")
            response = await client.post("/api/hint", json={
                "content": test_case["content"]
            })
            assert response.status_code == 200, f"API调用失败，状态码: {response.status_code}"
            result = response.json()
            assert result["type"] == test_case["expected_type"], f"响应类型不符合预期: {result}"
            assert "content" in result, f"响应缺少content字段: {result}"
            print(f"   ✅ 响应: {result['content'][:50]}...")
        
        # 测试直接使用AI获取提示
        print("\n3. 测试直接使用AI获取提示...")
        response = await client.post("/api/hint", json={
            "content": "解不等式：3x - 5 > 7",
            "use_ai": True
        })
        assert response.status_code == 200, f"API调用失败，状态码: {response.status_code}"
        result = response.json()
        assert "content" in result, f"响应缺少content字段: {result}"
        print(f"   ✅ AI响应: {result['content'][:50]}...")
    
    print("\n✅ 所有HTTP API测试通过！")

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("\n=== 测试WebSocket连接 ===")
    
    # 连接WebSocket
    async with websockets.connect(WS_URL) as websocket:
        print("1. WebSocket连接成功")
        
        # 测试ping消息
        print("2. 测试ping消息...")
        ping_message = {"type": "ping"}
        await websocket.send(json.dumps(ping_message))
        response = await asyncio.wait_for(websocket.recv(), timeout=WS_TIMEOUT)
        response_data = json.loads(response)
        assert response_data["type"] == "pong", f"ping响应不符合预期: {response_data}"
        print("   ✅ ping-pong测试通过")
        
        # 测试解题步骤消息
        print("\n3. 测试解题步骤消息...")
        test_case = MATH_TEST_CASES[0]
        print(f"   测试用例: {test_case['name']}")
        
        # 发送解题步骤
        step_message = {
            "type": "step",
            "content": test_case["content"]
        }
        await websocket.send(json.dumps(step_message))
        
        # 接收响应
        response = await asyncio.wait_for(websocket.recv(), timeout=WS_TIMEOUT)
        response_data = json.loads(response)
        assert response_data["type"] == test_case["expected_type"], f"响应类型不符合预期: {response_data}"
        assert "content" in response_data, f"响应缺少content字段: {response_data}"
        print(f"   ✅ WebSocket响应: {response_data['content'][:50]}...")
    
    print("\n✅ WebSocket测试通过！")

async def test_websocket_multiple_messages():
    """测试WebSocket多消息交互"""
    print("\n=== 测试WebSocket多消息交互 ===")
    
    async with websockets.connect(WS_URL) as websocket:
        print("1. WebSocket连接成功")
        
        # 测试多个测试用例
        for i, test_case in enumerate(MATH_TEST_CASES[:2]):
            print(f"\n2. 测试用例 {i+1}: {test_case['name']}")
            
            # 发送解题步骤
            step_message = {
                "type": "step",
                "content": test_case["content"]
            }
            await websocket.send(json.dumps(step_message))
            
            # 接收响应
            response = await asyncio.wait_for(websocket.recv(), timeout=WS_TIMEOUT)
            response_data = json.loads(response)
            assert response_data["type"] == test_case["expected_type"], f"响应类型不符合预期: {response_data}"
            assert "content" in response_data, f"响应缺少content字段: {response_data}"
            print(f"   ✅ 响应: {response_data['content'][:50]}...")
        
        # 测试错误报告
        print("\n3. 测试错误报告...")
        error_message = {
            "type": "error_report",
            "content": "测试错误报告"
        }
        await websocket.send(json.dumps(error_message))
        
        response = await asyncio.wait_for(websocket.recv(), timeout=WS_TIMEOUT)
        response_data = json.loads(response)
        assert response_data["type"] == "acknowledge", f"错误报告响应不符合预期: {response_data}"
        print(f"   ✅ 错误报告响应: {response_data['content']}")
    
    print("\n✅ WebSocket多消息交互测试通过！")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("初中数学残局挑战系统 - 整体测试")
    print("=" * 60)
    print(f"测试时间: {asyncio.get_event_loop().time()}")
    print(f"测试地址: {BASE_URL}")
    print(f"WebSocket地址: {WS_URL}")
    print("=" * 60)
    
    try:
        # 运行所有测试
        await test_http_api()
        await test_websocket_connection()
        await test_websocket_multiple_messages()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！前后端交互正常！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    asyncio.run(main())
