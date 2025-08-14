from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from services.ner_service import NERService
from services.std_service import StdService
from services.abbr_service import AbbrService
from services.corr_service import CorrService
from services.gen_service import GenService
from middleware import LoggingMiddleware, ErrorHandlingMiddleware, SecurityMiddleware
from utils.helpers import format_response, generate_request_id, validate_financial_text, sanitize_text
from config import settings
from typing import List, Dict, Optional, Literal, Union, Any
import logging
import time

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="基于RAG技术的金融术语标准化和智能处理系统",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityMiddleware)

# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# 初始化各个服务
ner_service = NERService()  # 金融实体识别服务
standardization_service = StdService()  # 金融术语标准化服务
abbr_service = AbbrService()  # 金融缩写扩展服务
gen_service = GenService()  # 金融文本生成服务
corr_service = CorrService()  # 金融拼写纠正服务

# 基础模型类
class BaseInputModel(BaseModel):
    """基础输入模型，包含所有模型共享的字段"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llmOptions: Dict[str, str] = Field(
        default_factory=lambda: {
            "provider": settings.default_llm_provider,
            "model": settings.default_llm_model
        },
        description="大语言模型配置选项"
    )

class EmbeddingOptions(BaseModel):
    """向量数据库配置选项"""
    provider: Literal["huggingface", "openai", "bedrock"] = Field(
        default=settings.default_embedding_provider,
        description="向量数据库提供商"
    )
    model: str = Field(
        default=settings.default_embedding_model,
        description="嵌入模型名称"
    )
    dbName: str = Field(
        default=settings.default_db_name,
        description="向量数据库名称"
    )
    collectionName: str = Field(
        default=settings.default_collection_name,
        description="集合名称"
    )

class TextInput(BaseInputModel):
    """文本输入模型，用于标准化和金融实体识别"""
    text: str = Field(..., description="输入文本")
    options: Dict[str, bool] = Field(
        default_factory=dict,
        description="处理选项"
    )
    termTypes: Dict[str, bool] = Field(
        default_factory=dict,
        description="术语类型"
    )
    embeddingOptions: EmbeddingOptions = Field(
        default_factory=EmbeddingOptions,
        description="向量数据库配置选项"
    )

class AbbrInput(BaseInputModel):
    """金融缩写扩展输入模型"""
    text: str = Field(..., description="输入文本")
    context: str = Field(
        default="",
        description="上下文信息"
    )
    method: Literal["simple_ollama", "query_db_llm_rerank", "llm_rank_query_db"] = Field(
        default="simple_ollama",
        description="处理方法"
    )
    embeddingOptions: Optional[EmbeddingOptions] = Field(
        default_factory=EmbeddingOptions,
        description="向量数据库配置选项"
    )

class ErrorOptions(BaseModel):
    """错误生成选项"""
    errorType: Literal["typo", "abbreviation", "synonym", "contextual"] = Field(
        default="typo",
        description="错误类型"
    )
    severity: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="错误严重程度"
    )
    context: str = Field(
        default="",
        description="上下文信息"
    )

class GenInput(BaseInputModel):
    """金融文本生成输入模型"""
    prompt: str = Field(..., description="生成提示")
    maxLength: int = Field(
        default=500,
        description="最大生成长度"
    )
    temperature: float = Field(
        default=0.7,
        description="生成温度"
    )
    style: Literal["formal", "casual", "technical", "educational"] = Field(
        default="formal",
        description="生成风格"
    )

# API端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "金融领域专有名词标准化系统",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/standardize")
async def standardize_text(input_data: TextInput, request: Request):
    """金融术语标准化"""
    start_time = time.time()
    request_id = generate_request_id()
    
    try:
        # 输入验证
        validation = validate_financial_text(input_data.text)
        if not validation["is_valid"]:
            return format_response(
                data=None,
                success=False,
                message="输入文本验证失败",
                request_id=request_id
            )
        
        # 清理文本
        cleaned_text = sanitize_text(input_data.text)
        
        result = standardization_service.standardize_text(
            cleaned_text,
            input_data.embeddingOptions.provider,
            input_data.embeddingOptions.model,
            input_data.embeddingOptions.dbName,
            input_data.embeddingOptions.collectionName
        )
        
        duration = time.time() - start_time
        return format_response(
            data=result,
            message="标准化处理成功",
            request_id=request_id
        )
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"标准化失败: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"message": "标准化处理失败", "error": str(e), "request_id": request_id}
        )

@app.post("/api/ner")
async def extract_entities(input_data: TextInput):
    """金融实体识别"""
    try:
        result = ner_service.extract_entities(
            input_data.text,
            input_data.llmOptions,
            input_data.embeddingOptions.provider,
            input_data.embeddingOptions.model,
            input_data.embeddingOptions.dbName,
            input_data.embeddingOptions.collectionName
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"实体识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/abbreviation")
async def expand_abbreviation(input_data: AbbrInput):
    """金融缩写扩展"""
    try:
        result = abbr_service.expand_abbreviation(
            input_data.text,
            input_data.context,
            input_data.method,
            input_data.llmOptions,
            input_data.embeddingOptions
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"缩写扩展失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/correction")
async def correct_text(input_data: TextInput):
    """金融拼写纠正"""
    try:
        result = corr_service.correct_text(
            input_data.text,
            input_data.llmOptions
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"拼写纠正失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generation")
async def generate_text(input_data: GenInput):
    """金融文本生成"""
    try:
        result = gen_service.generate_text(
            input_data.prompt,
            input_data.maxLength,
            input_data.temperature,
            input_data.style,
            input_data.llmOptions
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"文本生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        workers=settings.max_workers,
        log_level=settings.log_level.lower()
    )
