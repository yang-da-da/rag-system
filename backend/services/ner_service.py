import ollama
import logging
from typing import List, Dict, Any
from utils.embedding_factory import EmbeddingFactory
from utils.embedding_config import EmbeddingProvider, EmbeddingConfig
from pymilvus import MilvusClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NERService:
    """
    金融实体识别服务
    识别文本中的金融实体，如公司、产品、指标、法规等
    """
    
    def __init__(self):
        """初始化金融实体识别服务"""
        self.financial_entity_types = [
            "COMPANY",      # 公司
            "PRODUCT",      # 金融产品
            "INDICATOR",    # 金融指标
            "REGULATION",   # 法规
            "CURRENCY",     # 货币
            "MARKET",       # 市场
            "RISK",         # 风险类型
            "ACCOUNT",      # 账户类型
            "INSTRUMENT",   # 金融工具
            "PERSON"        # 人名
        ]
        
        self.entity_patterns = {
            "COMPANY": ["公司", "银行", "保险", "基金", "证券", "投资", "信托"],
            "PRODUCT": ["基金", "债券", "股票", "期权", "期货", "保险", "理财"],
            "INDICATOR": ["利率", "汇率", "收益率", "风险", "波动率", "夏普比率"],
            "REGULATION": ["法规", "规定", "政策", "标准", "指引", "办法"],
            "CURRENCY": ["美元", "欧元", "人民币", "日元", "英镑", "港币"],
            "MARKET": ["股市", "债市", "汇市", "期货市场", "期权市场"],
            "RISK": ["信用风险", "市场风险", "操作风险", "流动性风险"],
            "ACCOUNT": ["活期账户", "定期账户", "投资账户", "信用账户"],
            "INSTRUMENT": ["股票", "债券", "期权", "期货", "互换", "远期"],
            "PERSON": ["分析师", "基金经理", "投资顾问", "风险经理"]
        }

    def extract_entities(self, text: str, llm_options: Dict[str, str], 
                        provider: str = "huggingface", model: str = "BAAI/bge-m3",
                        db_name: str = "financial_bge_m3", collection_name: str = "financial_concepts") -> Dict[str, Any]:
        """
        从文本中提取金融实体
        
        Args:
            text: 输入文本
            llm_options: 大语言模型配置
            provider: 嵌入模型提供商
            model: 嵌入模型名称
            db_name: 向量数据库名称
            collection_name: 集合名称
            
        Returns:
            提取的实体信息
        """
        try:
            # 使用规则匹配进行初步实体识别
            rule_entities = self._extract_entities_by_rules(text)
            
            # 使用LLM进行实体识别
            llm_entities = self._extract_entities_by_llm(text, llm_options)
            
            # 使用向量数据库进行实体验证和扩展
            vector_entities = self._extract_entities_by_vector(text, provider, model, db_name, collection_name)
            
            # 合并和去重实体
            all_entities = self._merge_entities(rule_entities, llm_entities, vector_entities)
            
            # 计算置信度
            for entity in all_entities:
                entity['confidence'] = self._calculate_confidence(entity, text)
            
            # 按置信度排序
            all_entities.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                "text": text,
                "entities": all_entities,
                "entity_count": len(all_entities),
                "entity_types": list(set([entity['type'] for entity in all_entities])),
                "message": "实体识别完成"
            }
            
        except Exception as e:
            logger.error(f"实体识别失败: {str(e)}")
            return {
                "text": text,
                "entities": [],
                "entity_count": 0,
                "entity_types": [],
                "message": f"实体识别失败: {str(e)}"
            }

    def _extract_entities_by_rules(self, text: str) -> List[Dict]:
        """使用规则匹配提取实体"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    start_pos = text.find(pattern)
                    entities.append({
                        "text": pattern,
                        "type": entity_type,
                        "start": start_pos,
                        "end": start_pos + len(pattern),
                        "method": "rule_based",
                        "confidence": 0.7
                    })
        
        return entities

    def _extract_entities_by_llm(self, text: str, llm_options: Dict[str, str]) -> List[Dict]:
        """使用大语言模型提取实体"""
        try:
            provider = llm_options.get("provider", "ollama")
            model = llm_options.get("model", "qwen2.5:7b")
            
            if provider == "ollama":
                return self._extract_entities_with_ollama(text, model)
            else:
                logger.warning(f"不支持的LLM提供商: {provider}")
                return []
                
        except Exception as e:
            logger.error(f"LLM实体识别失败: {str(e)}")
            return []

    def _extract_entities_with_ollama(self, text: str, model: str) -> List[Dict]:
        """使用Ollama进行实体识别"""
        try:
            prompt = f"""
            请从以下金融文本中识别所有金融实体，包括公司、产品、指标、法规、货币、市场、风险类型、账户类型、金融工具和人名。
            
            文本: {text}
            
            请以JSON格式返回结果，格式如下:
            {{
                "entities": [
                    {{
                        "text": "实体文本",
                        "type": "实体类型",
                        "start": 起始位置,
                        "end": 结束位置,
                        "description": "实体描述"
                    }}
                ]
            }}
            
            只返回JSON，不要其他内容。
            """
            
            response = ollama.chat(model=model, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            # 解析响应
            content = response['message']['content']
            try:
                import json
                result = json.loads(content)
                entities = result.get('entities', [])
                
                # 添加方法标识
                for entity in entities:
                    entity['method'] = 'llm_based'
                    entity['confidence'] = 0.8
                
                return entities
                
            except json.JSONDecodeError:
                logger.warning("LLM返回的不是有效JSON格式")
                return []
                
        except Exception as e:
            logger.error(f"Ollama实体识别失败: {str(e)}")
            return []

    def _extract_entities_by_vector(self, text: str, provider: str, model: str, 
                                   db_name: str, collection_name: str) -> List[Dict]:
        """使用向量数据库进行实体验证和扩展"""
        try:
            # 这里应该连接向量数据库进行搜索
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logger.error(f"向量数据库实体识别失败: {str(e)}")
            return []

    def _merge_entities(self, rule_entities: List[Dict], llm_entities: List[Dict], 
                       vector_entities: List[Dict]) -> List[Dict]:
        """合并和去重实体"""
        all_entities = []
        seen_entities = set()
        
        # 添加规则识别的实体
        for entity in rule_entities:
            key = (entity['text'], entity['type'])
            if key not in seen_entities:
                all_entities.append(entity)
                seen_entities.add(key)
        
        # 添加LLM识别的实体
        for entity in llm_entities:
            key = (entity['text'], entity['type'])
            if key not in seen_entities:
                all_entities.append(entity)
                seen_entities.add(key)
        
        # 添加向量数据库识别的实体
        for entity in vector_entities:
            key = (entity['text'], entity['type'])
            if key not in seen_entities:
                all_entities.append(entity)
                seen_entities.add(key)
        
        return all_entities

    def _calculate_confidence(self, entity: Dict, text: str) -> float:
        """计算实体识别的置信度"""
        base_confidence = entity.get('confidence', 0.5)
        
        # 根据方法调整置信度
        method = entity.get('method', 'unknown')
        if method == 'rule_based':
            base_confidence *= 0.9
        elif method == 'llm_based':
            base_confidence *= 1.0
        elif method == 'vector_based':
            base_confidence *= 0.95
        
        # 根据实体长度调整置信度
        entity_length = len(entity['text'])
        if entity_length >= 3:
            base_confidence *= 1.1
        elif entity_length <= 1:
            base_confidence *= 0.8
        
        # 根据文本中的出现频率调整置信度
        frequency = text.count(entity['text'])
        if frequency == 1:
            base_confidence *= 1.0
        elif frequency > 1:
            base_confidence *= 0.9
        
        return min(base_confidence, 1.0)

    def get_entity_statistics(self, entities: List[Dict]) -> Dict[str, Any]:
        """获取实体统计信息"""
        if not entities:
            return {
                "total_entities": 0,
                "entity_type_distribution": {},
                "confidence_distribution": {},
                "method_distribution": {}
            }
        
        # 实体类型分布
        type_dist = {}
        for entity in entities:
            entity_type = entity['type']
            type_dist[entity_type] = type_dist.get(entity_type, 0) + 1
        
        # 置信度分布
        confidence_dist = {"high": 0, "medium": 0, "low": 0}
        for entity in entities:
            conf = entity.get('confidence', 0)
            if conf >= 0.8:
                confidence_dist["high"] += 1
            elif conf >= 0.6:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1
        
        # 方法分布
        method_dist = {}
        for entity in entities:
            method = entity.get('method', 'unknown')
            method_dist[method] = method_dist.get(method, 0) + 1
        
        return {
            "total_entities": len(entities),
            "entity_type_distribution": type_dist,
            "confidence_distribution": confidence_dist,
            "method_distribution": method_dist
        }
