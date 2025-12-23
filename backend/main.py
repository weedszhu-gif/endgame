from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 导入路由
from api import websocket

# 加载环境变量
load_dotenv()

# 环境变量配置
class Settings:
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

# 创建配置实例
settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title="初中数学残局挑战系统",
    description="AI辅助的初中数学学习系统，提供实时的解题指导和苏格拉底式提示",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册WebSocket路由
app.add_api_websocket_route("/ws", websocket.websocket_endpoint)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "服务正常运行"}

# 根路径
@app.get("/")
async def root():
    return {"message": "欢迎使用初中数学残局挑战系统 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
