from enum import Enum
from typing import Optional
from pydantic import BaseModel

class EmbeddingProvider(Enum):
    """嵌入模型提供商枚举"""
    OPENAI = "openai"
    BEDROCK = "bedrock"
    HUGGINGFACE = "huggingface"

class EmbeddingConfig(BaseModel):
    """嵌入模型配置"""
    provider: EmbeddingProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_length: int = 512
    device: str = "cpu"
    trust_remote_code: bool = True
    
    class Config:
        use_enum_values = True
