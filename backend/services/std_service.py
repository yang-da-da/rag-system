from pymilvus import MilvusClient
from dotenv import load_dotenv
from utils.embedding_factory import EmbeddingFactory
from utils.embedding_config import EmbeddingProvider, EmbeddingConfig
import os
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class StdService:
    """
    金融术语标准化服务
    使用向量数据库进行金融术语的标准化和相似度搜索
    """
    def __init__(self, 
                 provider="huggingface",
                 model="BAAI/bge-m3",
                 db_path="db/financial_bge_m3.db",
                 collection_name="financial_concepts"):
        """
        初始化标准化服务
        
        Args:
            provider: 嵌入模型提供商 (openai/bedrock/huggingface)
            model: 使用的模型名称
            db_path: Milvus 数据库路径
            collection_name: 集合名称
        """
        # 根据 provider 字符串匹配正确的枚举值
        provider_mapping = {
            'openai': EmbeddingProvider.OPENAI,
            'bedrock': EmbeddingProvider.BEDROCK,
            'huggingface': EmbeddingProvider.HUGGINGFACE
        }
        
        # 创建 embedding 函数
        embedding_provider = provider_mapping.get(provider.lower())
        if embedding_provider is None:
            raise ValueError(f"Unsupported provider: {provider}")
            
        config = EmbeddingConfig(
            provider=embedding_provider,
            model_name=model
        )
        self.embedding_func = EmbeddingFactory.create_embedding_function(config)
        
        # 连接 Milvus
        self.client = MilvusClient(db_path)
        self.collection_name = collection_name
        self.client.load_collection(self.collection_name)

    def search_similar_terms(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索与查询文本相似的金融术语
        
        Args:
            query: 查询文本
            limit: 返回结果的最大数量
            
        Returns:
            包含相似术语信息的列表，每个术语包含：
            - term_id: 术语ID
            - term_name: 术语名称
            - category: 术语类别
            - definition: 术语定义
            - synonyms: 同义词
            - related_terms: 相关术语
            - distance: 相似度距离
        """
        # 获取查询的向量表示
        query_embedding = self.embedding_func.embed_query(query)
        
        # 设置搜索参数
        search_params = {
            "collection_name": self.collection_name,
            "data": [query_embedding],
            "limit": limit,
            "output_fields": [
                "term_id", "term_name", "category", 
                "definition", "synonyms", "related_terms"
            ]
        }
        
        # 搜索相似项
        search_result = self.client.search(**search_params)

        results = []
        for hit in search_result[0]:
            results.append({
                "term_id": hit['entity'].get('term_id'),
                "term_name": hit['entity'].get('term_name'),
                "category": hit['entity'].get('category'),
                "definition": hit['entity'].get('definition'),
                "synonyms": hit['entity'].get('synonyms'),
                "related_terms": hit['entity'].get('related_terms'),
                "distance": hit['distance']
            })
        
        return results

    def standardize_text(self, text: str, provider: str = "huggingface", 
                        model: str = "BAAI/bge-m3", db_name: str = "financial_bge_m3", 
                        collection_name: str = "financial_concepts") -> Dict:
        """
        标准化金融文本中的术语
        
        Args:
            text: 输入文本
            provider: 嵌入模型提供商
            model: 模型名称
            db_name: 数据库名称
            collection_name: 集合名称
            
        Returns:
            标准化结果
        """
        try:
            # 如果参数不同，重新初始化服务
            if (provider != "huggingface" or model != "BAAI/bge-m3" or 
                db_name != "financial_bge_m3" or collection_name != "financial_concepts"):
                self.__init__(provider, model, f"db/{db_name}.db", collection_name)
            
            # 搜索相似术语
            similar_terms = self.search_similar_terms(text, limit=3)
            
            if not similar_terms:
                return {
                    "original_text": text,
                    "standardized_terms": [],
                    "confidence": 0.0,
                    "message": "未找到匹配的标准术语"
                }
            
            # 计算置信度（基于距离）
            best_match = similar_terms[0]
            confidence = 1.0 - min(best_match['distance'], 1.0)
            
            # 构建标准化结果
            standardized_terms = []
            for term in similar_terms:
                standardized_terms.append({
                    "standard_term": term['term_name'],
                    "category": term['category'],
                    "definition": term['definition'],
                    "synonyms": term['synonyms'],
                    "confidence": 1.0 - min(term['distance'], 1.0)
                })
            
            return {
                "original_text": text,
                "standardized_terms": standardized_terms,
                "confidence": confidence,
                "best_match": best_match['term_name'],
                "message": "标准化完成"
            }
            
        except Exception as e:
            logger.error(f"标准化失败: {str(e)}")
            return {
                "original_text": text,
                "standardized_terms": [],
                "confidence": 0.0,
                "message": f"标准化失败: {str(e)}"
            }

    def get_term_categories(self) -> List[str]:
        """
        获取所有术语类别
        
        Returns:
            术语类别列表
        """
        try:
            # 这里应该从数据库查询所有类别
            # 暂时返回预定义的金融类别
            return [
                "投资术语",
                "银行术语", 
                "保险术语",
                "证券术语",
                "衍生品术语",
                "风险管理术语",
                "会计术语",
                "税务术语",
                "监管术语"
            ]
        except Exception as e:
            logger.error(f"获取术语类别失败: {str(e)}")
            return []

    def get_related_terms(self, term_name: str, limit: int = 5) -> List[Dict]:
        """
        获取相关术语
        
        Args:
            term_name: 术语名称
            limit: 返回结果的最大数量
            
        Returns:
            相关术语列表
        """
        try:
            # 搜索相关术语
            similar_terms = self.search_similar_terms(term_name, limit=limit)
            
            # 过滤掉完全相同的术语
            related_terms = [term for term in similar_terms if term['term_name'] != term_name]
            
            return related_terms[:limit]
            
        except Exception as e:
            logger.error(f"获取相关术语失败: {str(e)}")
            return []
