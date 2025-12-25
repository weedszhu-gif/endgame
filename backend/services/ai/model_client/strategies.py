from abc import ABC, abstractmethod
import os
from typing import Optional
from .types import ModelRequest, ModelResponse, ModelType


# 模型策略接口
class ModelStrategy(ABC):
    @abstractmethod
    def call(self, request: ModelRequest) -> ModelResponse:
        """
        调用模型生成文本
        
        Args:
            request: 请求参数
            
        Returns:
            响应结果
        """
        pass


# OpenAI策略实现
class OpenAIStrategy(ModelStrategy):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化OpenAI策略
        
        Args:
            api_key: OpenAI API密钥
            base_url: 自定义API地址
        """
        from openai import OpenAI
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError("OpenAI API密钥未提供")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用OpenAI API"""
        response = self.client.chat.completions.create(
            model="gpt-4o",  # 可配置
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        text = response.choices[0].message.content
        return ModelResponse(text, ModelType.OPENAI)


# Claude策略实现
class ClaudeStrategy(ModelStrategy):
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Claude策略
        
        Args:
            api_key: Claude API密钥
        """
        from anthropic import Anthropic
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Claude API密钥未提供")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用Claude API"""
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",  # 可配置
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        text = response.content[0].text
        return ModelResponse(text, ModelType.CLAUDE)


# Gemini策略实现
class GeminiStrategy(ModelStrategy):
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Gemini策略
        
        Args:
            api_key: Gemini API密钥
        """
        import google.generativeai as genai
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API密钥未提供")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用Gemini API"""
        # 转换messages格式
        contents = []
        for msg in request.messages:
            contents.append(msg["content"])
        
        response = self.model.generate_content(
            contents,
            generation_config={
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens
            }
        )
        
        text = response.text
        return ModelResponse(text, ModelType.GEMINI)


# 文心一言策略实现
class ErnieStrategy(ModelStrategy):
    def __init__(self, access_token: Optional[str] = None):
        """
        初始化文心一言策略
        
        Args:
            access_token: 文心一言访问令牌
        """
        import erniebot
        
        self.access_token = access_token or os.getenv("ERNIE_ACCESS_TOKEN")
        
        if not self.access_token:
            raise ValueError("文心一言访问令牌未提供")
        
        erniebot.api_type = "aistudio"
        erniebot.access_token = self.access_token
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用文心一言API"""
        response = erniebot.ChatCompletion.create(
            model="ernie-4.0",  # 可配置
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        text = response.result
        return ModelResponse(text, ModelType.ERNIE)


# 通义千问策略实现
class QwenStrategy(ModelStrategy):
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化通义千问策略
        
        Args:
            api_key: 通义千问API密钥
        """
        import dashscope
        
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        
        if not self.api_key:
            raise ValueError("通义千问API密钥未提供")
        
        dashscope.api_key = self.api_key
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用通义千问API"""
        response = dashscope.Generation.call(
            model="qwen-max",  # 可配置
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        text = response.output.text
        return ModelResponse(text, ModelType.QWEN)


# 混元大模型策略实现
class HunyuanStrategy(ModelStrategy):
    def __init__(self, secret_id: Optional[str] = None, secret_key: Optional[str] = None):
        """
        初始化混元大模型策略
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
        """
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
        
        self.secret_id = secret_id or os.getenv("HUNYUAN_SECRET_ID")
        self.secret_key = secret_key or os.getenv("HUNYUAN_SECRET_KEY")
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("混元大模型SecretId和SecretKey未提供")
        
        cred = credential.Credential(self.secret_id, self.secret_key)
        httpProfile = HttpProfile(endpoint="hunyuan.tencentcloudapi.com")
        clientProfile = ClientProfile(httpProfile=httpProfile)
        self.client = hunyuan_client.HunyuanClient(cred, "", clientProfile)
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用混元大模型API"""
        req = models.ChatCompletionsRequest()
        req.Model = "hunyuan-pro"
        req.Messages = [
            {"Role": msg["role"].upper(), "Content": msg["content"]} 
            for msg in request.messages
        ]
        req.Temperature = request.temperature
        req.MaxTokens = request.max_tokens
        
        resp = self.client.ChatCompletions(req)
        text = resp.Result
        return ModelResponse(text, ModelType.HUNYUAN)


# 豆包策略实现
class DoubaoStrategy(ModelStrategy):
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        初始化豆包策略
        
        Args:
            api_key: 豆包API密钥
            secret_key: 豆包SecretKey（预留，当前版本未使用）
        """
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY")
        
        if not self.api_key:
            raise ValueError("豆包API密钥未提供")
        
        # API端点配置
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.default_model = "doubao-seed-1-6-251015"
    
    def call(self, request: ModelRequest) -> ModelResponse:
        """调用豆包API"""
        import requests
        import json
        
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 转换消息格式为豆包API需要的格式
            converted_messages = []
            for msg in request.messages:
                # 豆包API要求content是数组，包含text和type字段
                content = []
                if isinstance(msg["content"], str):
                    # 如果是字符串，转换为豆包API需要的格式
                    content.append({
                        "text": msg["content"],
                        "type": "text"
                    })
                else:
                    # 如果已经是正确的格式，直接使用
                    content = msg["content"]
                
                converted_messages.append({
                    "role": msg["role"],
                    "content": content
                })
            
            # 构建请求体
            payload = {
                "model": self.default_model,
                "messages": converted_messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if result.get("choices") and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"]
                    return ModelResponse(text, ModelType.DOUBAO)
                else:
                    raise RuntimeError(f"豆包API响应格式错误: {json.dumps(result)}")
            else:
                raise RuntimeError(f"豆包API调用失败: 状态码 {response.status_code}, 错误信息: {response.text}")
        except Exception as e:
            raise RuntimeError(f"豆包API调用失败: {str(e)}")
