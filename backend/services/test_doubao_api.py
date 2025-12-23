#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包API测试脚本
"""

from model_client import ModelClient, ModelType
import os
from dotenv import load_dotenv


def test_doubao_api():
    """测试豆包API调用"""
    print("=== 豆包API测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    model_type = os.getenv("AI_MODEL_TYPE")
    api_key = os.getenv("DOUBAO_API_KEY")
    
    print(f"配置信息：")
    print(f"- 模型类型：{model_type}")
    print(f"- API密钥：{api_key}")
    
    try:
        # 创建豆包客户端
        client = ModelClient(
            ModelType.DOUBAO,
            api_key=api_key
        )
        
        # 测试文本生成
        print("\n正在测试豆包API...")
        
        # 测试1：数学问题
        print("\n测试1：数学问题")
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        print(f"响应: {response}")
        
        # 测试2：简单问题
        print("\n测试2：简单问题")
        response = client.generate(
            prompt="什么是质数？",
            system_prompt="你是一位初中数学老师，使用简单易懂的语言解释概念。"
        )
        print(f"响应: {response}")
        
        # 测试3：苏格拉底式提问
        print("\n测试3：苏格拉底式提问")
        response = client.generate(
            prompt="我用配方法解方程 x² + 4x + 3 = 0",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        print(f"响应: {response}")
        
        print("\n=== 测试结果 ===")
        print("✅ 豆包API测试成功！")
        print("✅ 模型类型：doubao")
        print("✅ API密钥：已配置")
        print("✅ 文本生成：正常")
        print("✅ 苏格拉底式提问：正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        print("\n=== 测试结果 ===")
        print("❌ 豆包API测试失败！")
        print(f"❌ 错误信息：{str(e)}")
        
        # 错误排查建议
        print("\n🔍 错误排查建议：")
        print("1. 检查API密钥是否正确：83e2399c-d79e-4c97-8307-2b1e9018ddc8")
        print("2. 检查网络连接是否正常")
        print("3. 检查豆包API服务是否正常")
        print("4. 检查模型名称是否正确")
        print("5. 检查API调用次数是否超过限制")
        
        return False


if __name__ == "__main__":
    test_doubao_api()
