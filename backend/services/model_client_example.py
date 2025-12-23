#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型客户端示例脚本
演示如何使用ModelClient调用不同的大模型
"""

from model_client import ModelClient, ModelType
import os


def example_openai():
    """OpenAI模型示例"""
    print("=== OpenAI模型示例 ===")
    try:
        client = ModelClient(
            ModelType.OPENAI,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_doubao():
    """豆包模型示例"""
    print("\n=== 豆包模型示例 ===")
    try:
        client = ModelClient(
            ModelType.DOUBAO,
            api_key=os.getenv("DOUBAO_API_KEY"),
            secret_key=os.getenv("DOUBAO_SECRET_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_ernie():
    """文心一言模型示例"""
    print("\n=== 文心一言模型示例 ===")
    try:
        client = ModelClient(
            ModelType.ERNIE,
            access_token=os.getenv("ERNIE_ACCESS_TOKEN")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_qwen():
    """通义千问模型示例"""
    print("\n=== 通义千问模型示例 ===")
    try:
        client = ModelClient(
            ModelType.QWEN,
            api_key=os.getenv("QWEN_API_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_hunyuan():
    """混元大模型示例"""
    print("\n=== 混元大模型示例 ===")
    try:
        client = ModelClient(
            ModelType.HUNYUAN,
            secret_id=os.getenv("HUNYUAN_SECRET_ID"),
            secret_key=os.getenv("HUNYUAN_SECRET_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_claude():
    """Claude模型示例"""
    print("\n=== Claude模型示例 ===")
    try:
        client = ModelClient(
            ModelType.CLAUDE,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_gemini():
    """Gemini模型示例"""
    print("\n=== Gemini模型示例 ===")
    try:
        client = ModelClient(
            ModelType.GEMINI,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        response = client.generate(
            prompt="如何解方程 2x + 3 = 7？",
            system_prompt="你是一位初中数学老师，使用苏格拉底式提问引导学生思考。"
        )
        
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行示例
    print("大模型客户端示例")
    print("================")
    
    # 根据环境变量配置选择运行哪个示例
    model_type = os.getenv("AI_MODEL_TYPE", "openai")
    
    if model_type.lower() == "openai":
        example_openai()
    elif model_type.lower() == "doubao":
        example_doubao()
    elif model_type.lower() == "ernie":
        example_ernie()
    elif model_type.lower() == "qwen":
        example_qwen()
    elif model_type.lower() == "hunyuan":
        example_hunyuan()
    elif model_type.lower() == "claude":
        example_claude()
    elif model_type.lower() == "gemini":
        example_gemini()
    else:
        # 运行所有示例
        example_openai()
        example_doubao()
        example_ernie()
        example_qwen()
        example_hunyuan()
        example_claude()
        example_gemini()
