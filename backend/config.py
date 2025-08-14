import os
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "金融领域专有名词标准化系统"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS配置
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # 默认LLM配置
    default_llm_provider: str = "ollama"
    default_llm_model: str = "qwen2.5:7b"
    
    # 默认嵌入模型配置
    default_embedding_provider: str = "huggingface"
    default_embedding_model: str = "BAAI/bge-m3"
    default_db_name: str = "financial_bge_m3"
    default_collection_name: str = "financial_concepts"
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 性能配置
    max_workers: int = 4
    timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()
