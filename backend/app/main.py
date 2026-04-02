"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import get_settings
from loguru import logger
import sys

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 创建 FastAPI 应用
app = FastAPI(
    title="RAG Knowledge Assistant API",
    description="基于 RAG 的企业知识库问答系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "RAG Knowledge Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    settings = get_settings()
    logger.info("=" * 50)
    logger.info("RAG Knowledge Assistant API Starting...")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info(f"Chroma DB: {settings.chroma_persist_dir}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("RAG Knowledge Assistant API Shutting down...")


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
