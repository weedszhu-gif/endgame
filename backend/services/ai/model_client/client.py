from typing import Optional, List, Dict, Any
from .types import ModelRequest, ModelResponse, ModelType
from .strategies import (
    ModelStrategy,
    OpenAIStrategy,
    DoubaoStrategy,
    ErnieStrategy,
    QwenStrategy,
    HunyuanStrategy,
    ClaudeStrategy,
    GeminiStrategy
)


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
