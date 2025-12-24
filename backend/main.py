from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 导入配置
from config.settings import Settings

# 导入路由
from api.endpoints.endpoints import router as api_router
from api.websocket.websocket import websocket_endpoint

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

# 注册API路由
app.include_router(api_router)

# 注册WebSocket路由
app.add_api_websocket_route("/ws", websocket_endpoint)

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
