"""应用配置管理"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 智谱 AI 配置
    zhipu_api_key: str = ""
    
    # 服务配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # 向量数据库配置
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "knowledge_base"
    
    # 文件上传配置
    upload_dir: str = "./data/uploads"
    max_file_size: int = 10485760  # 10MB
    
    # RAG 配置
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k: int = 3
    temperature: float = 0.7
    
    # 模型配置
    llm_model: str = "glm-4-air"
    embedding_model: str = "embedding-3"

    # 搜索工具配置（博查 API，可选）
    bocha_api_key: str = ""
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
