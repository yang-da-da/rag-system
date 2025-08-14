from typing import Callable, List
from .embedding_config import EmbeddingProvider, EmbeddingConfig
import logging

logger = logging.getLogger(__name__)

class EmbeddingFactory:
    """嵌入模型工厂类"""
    
    @staticmethod
    def create_embedding_function(config: EmbeddingConfig) -> Callable[[str], List[float]]:
        """
        根据配置创建嵌入函数
        
        Args:
            config: 嵌入模型配置
            
        Returns:
            嵌入函数
        """
        try:
            if config.provider == EmbeddingProvider.HUGGINGFACE:
                return EmbeddingFactory._create_huggingface_embedding(config)
            elif config.provider == EmbeddingProvider.OPENAI:
                return EmbeddingFactory._create_openai_embedding(config)
            elif config.provider == EmbeddingProvider.BEDROCK:
                return EmbeddingFactory._create_bedrock_embedding(config)
            else:
                raise ValueError(f"不支持的嵌入模型提供商: {config.provider}")
                
        except Exception as e:
            logger.error(f"创建嵌入函数失败: {str(e)}")
            # 返回一个默认的嵌入函数
            return EmbeddingFactory._create_default_embedding()

    @staticmethod
    def _create_huggingface_embedding(config: EmbeddingConfig) -> Callable[[str], List[float]]:
        """创建HuggingFace嵌入函数"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # 加载模型
            model = SentenceTransformer(
                config.model_name,
                device=config.device,
                trust_remote_code=config.trust_remote_code
            )
            
            def embed_query(text: str) -> List[float]:
                """嵌入查询文本"""
                try:
                    embeddings = model.encode([text], max_length=config.max_length)
                    return embeddings[0].tolist()
                except Exception as e:
                    logger.error(f"文本嵌入失败: {str(e)}")
                    return [0.0] * 1024  # 返回零向量作为默认值
            
            return embed_query
            
        except ImportError:
            logger.error("sentence_transformers未安装，请运行: pip install sentence_transformers")
            return EmbeddingFactory._create_default_embedding()
        except Exception as e:
            logger.error(f"创建HuggingFace嵌入函数失败: {str(e)}")
            return EmbeddingFactory._create_default_embedding()

    @staticmethod
    def _create_openai_embedding(config: EmbeddingConfig) -> Callable[[str], List[float]]:
        """创建OpenAI嵌入函数"""
        try:
            import openai
            
            if config.api_key:
                openai.api_key = config.api_key
            if config.api_base:
                openai.api_base = config.api_base
            
            def embed_query(text: str) -> List[float]:
                """嵌入查询文本"""
                try:
                    response = openai.Embedding.create(
                        input=text,
                        model=config.model_name
                    )
                    return response['data'][0]['embedding']
                except Exception as e:
                    logger.error(f"OpenAI嵌入失败: {str(e)}")
                    return [0.0] * 1536  # OpenAI默认维度
            
            return embed_query
            
        except ImportError:
            logger.error("openai未安装，请运行: pip install openai")
            return EmbeddingFactory._create_default_embedding()
        except Exception as e:
            logger.error(f"创建OpenAI嵌入函数失败: {str(e)}")
            return EmbeddingFactory._create_default_embedding()

    @staticmethod
    def _create_bedrock_embedding(config: EmbeddingConfig) -> Callable[[str], List[float]]:
        """创建Bedrock嵌入函数"""
        try:
            import boto3
            
            bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name='us-east-1'  # 默认区域
            )
            
            def embed_query(text: str) -> List[float]:
                """嵌入查询文本"""
                try:
                    # 这里需要根据具体的Bedrock模型调整请求格式
                    # 暂时返回默认向量
                    logger.warning("Bedrock嵌入功能尚未完全实现")
                    return [0.0] * 1024
                except Exception as e:
                    logger.error(f"Bedrock嵌入失败: {str(e)}")
                    return [0.0] * 1024
            
            return embed_query
            
        except ImportError:
            logger.error("boto3未安装，请运行: pip install boto3")
            return EmbeddingFactory._create_default_embedding()
        except Exception as e:
            logger.error(f"创建Bedrock嵌入函数失败: {str(e)}")
            return EmbeddingFactory._create_default_embedding()

    @staticmethod
    def _create_default_embedding() -> Callable[[str], List[float]]:
        """创建默认嵌入函数（返回零向量）"""
        def embed_query(text: str) -> List[float]:
            """默认嵌入函数，返回零向量"""
            logger.warning("使用默认嵌入函数，返回零向量")
            return [0.0] * 1024
        
        return embed_query

    @staticmethod
    def get_embedding_dimension(provider: EmbeddingProvider, model_name: str) -> int:
        """
        获取嵌入向量的维度
        
        Args:
            provider: 嵌入模型提供商
            model_name: 模型名称
            
        Returns:
            向量维度
        """
        dimension_map = {
            EmbeddingProvider.HUGGINGFACE: {
                "BAAI/bge-m3": 1024,
                "BAAI/bge-large-zh": 1024,
                "BAAI/bge-base-zh": 768,
                "sentence-transformers/all-MiniLM-L6-v2": 384,
                "sentence-transformers/all-mpnet-base-v2": 768
            },
            EmbeddingProvider.OPENAI: {
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072
            },
            EmbeddingProvider.BEDROCK: {
                "amazon.titan-embed-text-v1": 1536,
                "cohere.embed-english-v3": 1024,
                "cohere.embed-multilingual-v3": 1024
            }
        }
        
        return dimension_map.get(provider, {}).get(model_name, 1024)
