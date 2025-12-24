import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """应用配置类"""
    
    def __init__(self):
        # 服务器配置
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
        
        # CORS配置
        allow_origins = os.getenv("ALLOW_ORIGINS", "*")
        if isinstance(allow_origins, str):
            self.allow_origins = [origin.strip() for origin in allow_origins.split(",")]
        else:
            self.allow_origins = ["*"]
        
        # AI模型配置
        self.ai_model_type = os.getenv("AI_MODEL_TYPE", "doubao")  # 模型类型：openai, doubao, ernie, qwen, hunyuan, claude, gemini
        self.ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.ai_max_tokens = int(os.getenv("AI_MAX_TOKENS", "100"))
        
        # 数据库配置
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
