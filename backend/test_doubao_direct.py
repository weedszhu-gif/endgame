#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试豆包API调用
使用用户提供的API端点和密钥格式
"""

import requests
import json
import os
from dotenv import load_dotenv


def test_doubao_direct():
    """直接测试豆包API调用"""
    print("=== 直接测试豆包API ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    api_key = os.getenv("DOUBAO_API_KEY")
    model = "doubao-seed-1-6-251015"
    
    print(f"配置信息：")
    print(f"- API密钥：{api_key}")
    print(f"- 模型名称：{model}")
    
    # API端点
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 测试1：简单数学问题
    print("\n测试1：简单数学问题")
    payload = {
        "model": model,
        "messages": [
            {
                "content": [
                    {
                        "text": "如何解方程 2x + 3 = 7？",
                        "type": "text"
                    }
                ],
                "role": "user"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"异常: {str(e)}")
    
    # 测试2：苏格拉底式提问
    print("\n测试2：苏格拉底式提问")
    payload = {
        "model": model,
        "messages": [
            {
                "content": [
                    {
                        "text": "我用配方法解方程 x² + 4x + 3 = 0",
                        "type": "text"
                    }
                ],
                "role": "user"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"异常: {str(e)}")
    
    print("\n=== 测试总结 ===")
    print("1. 如果返回状态码200，说明API调用成功")
    print("2. 如果返回 'Invalid API-key provided'，说明API密钥不正确或已过期")
    print("3. 如果返回 'Model not found'，说明模型名称不正确")
    print("4. 如果返回其他错误，请检查网络连接和API端点")
    print("\n建议：")
    print("- 确认API密钥是否正确获取")
    print("- 确认API密钥是否过期")
    print("- 确认模型名称是否正确")
    print("- 确认网络连接是否正常")


if __name__ == "__main__":
    test_doubao_direct()
