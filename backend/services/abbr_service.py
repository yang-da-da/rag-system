import ollama
import logging
from typing import List, Dict, Any, Optional
from utils.embedding_factory import EmbeddingFactory
from utils.embedding_config import EmbeddingProvider, EmbeddingConfig
from pymilvus import MilvusClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AbbrService:
    """
    金融缩写扩展服务
    将金融缩写扩展为完整术语，支持多种扩展方法
    """
    
    def __init__(self):
        """初始化金融缩写扩展服务"""
        # 常见金融缩写词典
        self.financial_abbreviations = {
            # 投资相关
            "ETF": "交易所交易基金",
            "IPO": "首次公开募股",
            "ROI": "投资回报率",
            "ROE": "净资产收益率",
            "ROA": "总资产收益率",
            "PE": "市盈率",
            "PB": "市净率",
            "EPS": "每股收益",
            "P/E": "市盈率",
            "P/B": "市净率",
            
            # 银行相关
            "ATM": "自动取款机",
            "CD": "定期存单",
            "APR": "年化利率",
            "APY": "年化收益率",
            "FDIC": "联邦存款保险公司",
            "LIBOR": "伦敦银行同业拆借利率",
            "SOFR": "有担保隔夜融资利率",
            
            # 保险相关
            "P&C": "财产和意外保险",
            "L&H": "人寿和健康保险",
            "HMO": "健康维护组织",
            "PPO": "优先提供者组织",
            "COBRA": "综合预算调节法案",
            
            # 证券相关
            "SEC": "证券交易委员会",
            "FINRA": "金融业监管局",
            "NYSE": "纽约证券交易所",
            "NASDAQ": "纳斯达克证券交易所",
            "OTC": "场外交易",
            "ADR": "美国存托凭证",
            
            # 衍生品相关
            "FRA": "远期利率协议",
            "IRS": "利率互换",
            "CDS": "信用违约互换",
            "CDO": "担保债务凭证",
            "MBS": "抵押贷款支持证券",
            "ABS": "资产支持证券",
            
            # 风险管理
            "VaR": "风险价值",
            "ES": "期望损失",
            "CVaR": "条件风险价值",
            "SR": "夏普比率",
            "IR": "信息比率",
            "MDD": "最大回撤",
            
            # 会计相关
            "GAAP": "公认会计准则",
            "IFRS": "国际财务报告准则",
            "EBITDA": "息税折旧摊销前利润",
            "EBIT": "息税前利润",
            "EBT": "税前利润",
            "NI": "净利润",
            
            # 税务相关
            "IRS": "美国国税局",
            "W-2": "工资和税收报表",
            "1099": "独立承包商收入报表",
            "K-1": "合伙企业收入报表",
            "1040": "个人所得税申报表"
        }
        
        # 金融术语类别
        self.financial_categories = [
            "投资", "银行", "保险", "证券", "衍生品", 
            "风险管理", "会计", "税务", "监管", "市场"
        ]

    def expand_abbreviation(self, text: str, context: str = "", 
                           method: str = "simple_ollama",
                           llm_options: Dict[str, str] = None,
                           embedding_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        扩展金融缩写
        
        Args:
            text: 输入的缩写文本
            context: 上下文信息
            method: 扩展方法
            llm_options: 大语言模型配置
            embedding_options: 向量数据库配置
            
        Returns:
            扩展结果
        """
        try:
            if method == "simple_ollama":
                return self._expand_with_ollama(text, context, llm_options)
            elif method == "query_db_llm_rerank":
                return self._expand_with_db_llm_rerank(text, context, llm_options, embedding_options)
            elif method == "llm_rank_query_db":
                return self._expand_with_llm_rank_db(text, context, llm_options, embedding_options)
            else:
                return self._expand_with_dictionary(text, context)
                
        except Exception as e:
            logger.error(f"缩写扩展失败: {str(e)}")
            return {
                "abbreviation": text,
                "expansions": [],
                "best_expansion": "",
                "confidence": 0.0,
                "method": method,
                "message": f"扩展失败: {str(e)}"
            }

    def _expand_with_dictionary(self, text: str, context: str = "") -> Dict[str, Any]:
        """使用词典进行缩写扩展"""
        text_upper = text.upper().strip()
        
        # 直接匹配
        if text_upper in self.financial_abbreviations:
            expansion = self.financial_abbreviations[text_upper]
            return {
                "abbreviation": text,
                "expansions": [expansion],
                "best_expansion": expansion,
                "confidence": 0.9,
                "method": "dictionary",
                "message": "词典匹配成功"
            }
        
        # 部分匹配
        partial_matches = []
        for abbr, expansion in self.financial_abbreviations.items():
            if text_upper in abbr or abbr in text_upper:
                partial_matches.append(expansion)
        
        if partial_matches:
            return {
                "abbreviation": text,
                "expansions": partial_matches,
                "best_expansion": partial_matches[0],
                "confidence": 0.7,
                "method": "dictionary_partial",
                "message": "词典部分匹配成功"
            }
        
        return {
            "abbreviation": text,
            "expansions": [],
            "best_expansion": "",
            "confidence": 0.0,
            "method": "dictionary",
            "message": "词典中未找到匹配项"
        }

    def _expand_with_ollama(self, text: str, context: str = "", 
                           llm_options: Dict[str, str] = None) -> Dict[str, Any]:
        """使用Ollama进行缩写扩展"""
        try:
            if not llm_options:
                llm_options = {"provider": "ollama", "model": "qwen2.5:7b"}
            
            model = llm_options.get("model", "qwen2.5:7b")
            
            prompt = f"""
            请将以下金融缩写扩展为完整的中文术语。如果可能，请提供多个可能的扩展。
            
            缩写: {text}
            上下文: {context if context else "无"}
            
            请以JSON格式返回结果，格式如下:
            {{
                "expansions": [
                    {{
                        "term": "完整术语",
                        "category": "术语类别",
                        "description": "术语描述",
                        "confidence": 置信度(0-1)
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
            
            content = response['message']['content']
            try:
                import json
                result = json.loads(content)
                expansions = result.get('expansions', [])
                
                if expansions:
                    # 按置信度排序
                    expansions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
                    best_expansion = expansions[0]['term']
                    avg_confidence = sum(exp.get('confidence', 0.5) for exp in expansions) / len(expansions)
                    
                    return {
                        "abbreviation": text,
                        "expansions": [exp['term'] for exp in expansions],
                        "best_expansion": best_expansion,
                        "confidence": avg_confidence,
                        "method": "ollama",
                        "message": "Ollama扩展成功",
                        "details": expansions
                    }
                else:
                    return {
                        "abbreviation": text,
                        "expansions": [],
                        "best_expansion": "",
                        "confidence": 0.0,
                        "method": "ollama",
                        "message": "Ollama未返回有效扩展"
                    }
                    
            except json.JSONDecodeError:
                logger.warning("Ollama返回的不是有效JSON格式")
                return {
                    "abbreviation": text,
                    "expansions": [],
                    "best_expansion": "",
                    "confidence": 0.0,
                    "method": "ollama",
                    "message": "Ollama返回格式错误"
                }
                
        except Exception as e:
            logger.error(f"Ollama缩写扩展失败: {str(e)}")
            return {
                "abbreviation": text,
                "expansions": [],
                "best_expansion": "",
                "confidence": 0.0,
                "method": "ollama",
                "message": f"Ollama扩展失败: {str(e)}"
            }

    def _expand_with_db_llm_rerank(self, text: str, context: str = "",
                                  llm_options: Dict[str, str] = None,
                                  embedding_options: Optional[Dict] = None) -> Dict[str, Any]:
        """使用向量数据库查询后LLM重排序"""
        try:
            # 这里应该先查询向量数据库获取候选扩展
            # 然后使用LLM进行重排序
            # 暂时使用Ollama方法
            return self._expand_with_ollama(text, context, llm_options)
            
        except Exception as e:
            logger.error(f"数据库查询LLM重排序失败: {str(e)}")
            return {
                "abbreviation": text,
                "expansions": [],
                "best_expansion": "",
                "confidence": 0.0,
                "method": "query_db_llm_rerank",
                "message": f"扩展失败: {str(e)}"
            }

    def _expand_with_llm_rank_db(self, text: str, context: str = "",
                                 llm_options: Dict[str, str] = None,
                                 embedding_options: Optional[Dict] = None) -> Dict[str, Any]:
        """使用LLM排序后查询向量数据库"""
        try:
            # 这里应该先使用LLM生成候选扩展
            # 然后查询向量数据库进行验证
            # 暂时使用Ollama方法
            return self._expand_with_ollama(text, context, llm_options)
            
        except Exception as e:
            logger.error(f"LLM排序数据库查询失败: {str(e)}")
            return {
                "abbreviation": text,
                "expansions": [],
                "best_expansion": "",
                "confidence": 0.0,
                "method": "llm_rank_query_db",
                "message": f"扩展失败: {str(e)}"
            }

    def get_abbreviation_statistics(self, text: str) -> Dict[str, Any]:
        """获取缩写统计信息"""
        # 统计文本中的缩写
        abbreviations = []
        words = text.split()
        
        for word in words:
            word_clean = word.strip('.,!?;:()[]{}"\'').upper()
            if word_clean in self.financial_abbreviations:
                abbreviations.append({
                    "abbreviation": word_clean,
                    "expansion": self.financial_abbreviations[word_clean],
                    "position": text.find(word)
                })
        
        return {
            "total_abbreviations": len(abbreviations),
            "abbreviations": abbreviations,
            "abbreviation_density": len(abbreviations) / len(words) if words else 0
        }

    def suggest_abbreviations(self, term: str) -> List[str]:
        """为完整术语建议可能的缩写"""
        suggestions = []
        
        # 提取首字母
        if len(term) > 2:
            first_letters = ''.join([word[0] for word in term.split() if word])
            if len(first_letters) >= 2:
                suggestions.append(first_letters.upper())
        
        # 提取关键词首字母
        keywords = [word for word in term.split() if len(word) > 2]
        if len(keywords) >= 2:
            keyword_abbr = ''.join([word[:2] for word in keywords[:3]])
            if len(keyword_abbr) >= 3:
                suggestions.append(keyword_abbr.upper())
        
        # 检查是否已有标准缩写
        for abbr, expansion in self.financial_abbreviations.items():
            if term.lower() in expansion.lower() or expansion.lower() in term.lower():
                suggestions.append(abbr)
        
        return list(set(suggestions))

    def validate_abbreviation(self, abbreviation: str, expansion: str) -> Dict[str, Any]:
        """验证缩写和扩展的匹配性"""
        # 检查首字母匹配
        abbr_upper = abbreviation.upper().strip()
        expansion_words = expansion.split()
        
        # 提取扩展词的首字母
        expansion_initials = ''.join([word[0] for word in expansion_words if word])
        
        # 计算匹配度
        if abbr_upper == expansion_initials:
            match_score = 1.0
        elif abbr_upper in expansion_initials or expansion_initials in abbr_upper:
            match_score = 0.8
        else:
            match_score = 0.3
        
        # 检查长度合理性
        length_score = 1.0
        if len(abbr_upper) < 2:
            length_score = 0.5
        elif len(abbr_upper) > len(expansion_words):
            length_score = 0.7
        
        # 综合评分
        overall_score = (match_score + length_score) / 2
        
        return {
            "abbreviation": abbreviation,
            "expansion": expansion,
            "match_score": match_score,
            "length_score": length_score,
            "overall_score": overall_score,
            "is_valid": overall_score >= 0.6,
            "suggestions": self.suggest_abbreviations(expansion)
        }
