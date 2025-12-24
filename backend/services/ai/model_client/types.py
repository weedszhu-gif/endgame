from enum import Enum
from typing import Optional, List, Dict


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
