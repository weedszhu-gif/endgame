from abc import ABC, abstractmethod
from enum import Enum
import os
from typing import Optional, List, Dict, Any

# 导入各模型的客户端库（按需安装）
# pip install openai anthropic google-generativeai dashscope tencentcloud-sdk-python baidu-aip

# 模型类型枚举
class ModelType(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    ERNIE = "ernie"  # 文心一言
    QWEN = "qwen"    # 通义千问
    HUNYUAN = "hunyuan"  # 混元大模型
    DOUBAO = "doubao"  # 豆包

# 请求模型
class ModelRequest:
    def __init__(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str = "",
        messages: Optional[List[Dict[str, str]]] = None
    ):
        """
        模型请求参数
        
        Args:
            prompt: 用户提示词
            temperature: 温度参数，控制生成的随机性
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            messages: 对话历史，格式为[{"role": "user/system/assistant", "content": "..."}]
        """
        self.prompt = prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.messages = messages or []
        
        # 如果没有对话历史，使用prompt创建
        if not self.messages:
            if system_prompt:
                self.messages.append({"role": "system", "content": system_prompt})
            self.messages.append({"role": "user", "content": prompt})

# 响应模型
class ModelResponse:
    def __init__(self, text: str, model_type: ModelType):
        """
        模型响应
        
        Args:
            text: 生成的文本
            model_type: 模型类型
        """
        self.text = text
        self.model_type = model_type

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

# 大模型客户端类
class ModelClient:
    def __init__(
        self,
        model_type: ModelType,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        初始化大模型客户端
        
        Args:
            model_type: 模型类型
            api_key: API密钥（通用参数，优先使用环境变量）
            **kwargs: 其他模型特定参数
        """
        self.model_type = model_type
        self.api_key = api_key
        self.strategy = self._get_strategy(**kwargs)
    
    def _get_strategy(self, **kwargs) -> ModelStrategy:
        """获取对应模型的策略实现"""
        if self.model_type == ModelType.OPENAI:
            return OpenAIStrategy(
                api_key=kwargs.get("api_key", self.api_key),
                base_url=kwargs.get("base_url")
            )
        elif self.model_type == ModelType.CLAUDE:
            return ClaudeStrategy(api_key=kwargs.get("api_key", self.api_key))
        elif self.model_type == ModelType.GEMINI:
            return GeminiStrategy(api_key=kwargs.get("api_key", self.api_key))
        elif self.model_type == ModelType.ERNIE:
            return ErnieStrategy(access_token=kwargs.get("access_token", self.api_key))
        elif self.model_type == ModelType.QWEN:
            return QwenStrategy(api_key=kwargs.get("api_key", self.api_key))
        elif self.model_type == ModelType.HUNYUAN:
            return HunyuanStrategy(
                secret_id=kwargs.get("secret_id", self.api_key),
                secret_key=kwargs.get("secret_key")
            )
        elif self.model_type == ModelType.DOUBAO:
            return DoubaoStrategy(
                api_key=kwargs.get("api_key", self.api_key),
                secret_key=kwargs.get("secret_key")
            )
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str = "",
        messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            messages: 对话历史
            
        Returns:
            生成的文本
        """
        request = ModelRequest(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            messages=messages
        )
        
        response = self.strategy.call(request)
        return response.text
    
    async def agenerate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str = "",
        messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        异步生成文本（预留接口，部分模型支持异步调用）
        """
        return self.generate(prompt, temperature, max_tokens, system_prompt, messages)

# 使用示例
if __name__ == "__main__":
    # 1. 使用环境变量配置API密钥
    # 例如：export OPENAI_API_KEY="your-api-key"
    
    # 2. 创建客户端实例
    # client = ModelClient(ModelType.OPENAI)
    # client = ModelClient(ModelType.DOUBAO)
    
    # 3. 生成文本
    # response = client.generate("如何解方程 2x + 3 = 7？", system_prompt="你是一位数学老师")
    # print(response)
    
    print("大模型客户端已初始化，可通过环境变量配置API密钥后使用")
