import ollama
import logging
from typing import List, Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenService:
    """
    金融文本生成服务
    基于金融知识生成专业文本，支持多种生成风格和内容类型
    """
    
    def __init__(self):
        """初始化金融文本生成服务"""
        # 金融文本类型
        self.financial_text_types = [
            "投资分析报告",
            "风险评估报告", 
            "财务分析报告",
            "市场研究报告",
            "产品说明文档",
            "政策解读文档",
            "培训材料",
            "新闻稿",
            "公告",
            "合同条款"
        ]
        
        # 金融文本风格
        self.text_styles = {
            "formal": "正式严谨",
            "casual": "通俗易懂", 
            "technical": "专业术语",
            "educational": "教育科普"
        }
        
        # 金融领域知识库
        self.financial_knowledge = {
            "投资": ["股票", "债券", "基金", "期货", "期权", "房地产", "外汇"],
            "银行": ["存款", "贷款", "信用卡", "理财产品", "外汇业务"],
            "保险": ["人寿保险", "财产保险", "健康保险", "意外保险"],
            "证券": ["股票交易", "债券交易", "衍生品交易", "投资银行"],
            "风险管理": ["信用风险", "市场风险", "操作风险", "流动性风险"],
            "会计": ["财务报表", "会计准则", "审计", "税务"],
            "监管": ["金融监管", "合规要求", "政策法规", "行业标准"]
        }

    def generate_text(self, prompt: str, max_length: int = 500, 
                     temperature: float = 0.7, style: str = "formal",
                     llm_options: Dict[str, str] = None) -> Dict[str, Any]:
        """
        生成金融文本
        
        Args:
            prompt: 生成提示
            max_length: 最大生成长度
            temperature: 生成温度
            style: 生成风格
            llm_options: 大语言模型配置
            
        Returns:
            生成的文本
        """
        try:
            if not llm_options:
                llm_options = {"provider": "ollama", "model": "qwen2.5:7b"}
            
            provider = llm_options.get("provider", "ollama")
            model = llm_options.get("model", "qwen2.5:7b")
            
            if provider == "ollama":
                return self._generate_with_ollama(prompt, max_length, temperature, style, model)
            else:
                logger.warning(f"不支持的LLM提供商: {provider}")
                return {
                    "generated_text": "",
                    "prompt": prompt,
                    "style": style,
                    "length": 0,
                    "message": f"不支持的LLM提供商: {provider}"
                }
                
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": style,
                "length": 0,
                "message": f"文本生成失败: {str(e)}"
            }

    def _generate_with_ollama(self, prompt: str, max_length: int, 
                             temperature: float, style: str, model: str) -> Dict[str, Any]:
        """使用Ollama生成金融文本"""
        try:
            # 构建风格化的提示
            style_prompt = self._build_style_prompt(prompt, style, max_length)
            
            # 设置生成参数
            generation_params = {
                "model": model,
                "prompt": style_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_length,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            # 生成文本
            response = ollama.generate(**generation_params)
            generated_text = response['response']
            
            # 后处理生成的文本
            processed_text = self._post_process_text(generated_text, style)
            
            return {
                "generated_text": processed_text,
                "prompt": prompt,
                "style": style,
                "length": len(processed_text),
                "temperature": temperature,
                "max_length": max_length,
                "message": "文本生成成功",
                "raw_response": generated_text
            }
            
        except Exception as e:
            logger.error(f"Ollama文本生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": style,
                "length": 0,
                "message": f"Ollama生成失败: {str(e)}"
            }

    def _build_style_prompt(self, prompt: str, style: str, max_length: int) -> str:
        """构建风格化的提示"""
        style_descriptions = {
            "formal": "请以正式、严谨的金融专业语言",
            "casual": "请以通俗易懂、简洁明了的语言",
            "technical": "请使用专业的金融术语和概念",
            "educational": "请以教育科普的方式，解释金融概念"
        }
        
        style_desc = style_descriptions.get(style, "请以正式的语言")
        
        base_prompt = f"""
        你是一个专业的金融分析师和撰稿人。{style_desc}，生成一段关于以下主题的金融文本。
        
        要求：
        1. 内容专业准确，符合金融行业标准
        2. 语言风格：{style_desc}
        3. 文本长度：不超过{max_length}字
        4. 结构清晰，逻辑严密
        5. 包含相关的金融概念和术语
        
        主题：{prompt}
        
        请直接返回生成的文本，不要包含任何解释或说明。
        """
        
        return base_prompt

    def _post_process_text(self, text: str, style: str) -> str:
        """后处理生成的文本"""
        # 清理多余的空白字符
        text = ' '.join(text.split())
        
        # 根据风格调整文本
        if style == "formal":
            # 确保正式语言的完整性
            if not text.endswith(('。', '！', '？', '；', '：')):
                text += '。'
        
        elif style == "casual":
            # 简化语言，确保通俗易懂
            text = text.replace('因此', '所以')
            text = text.replace('然而', '但是')
            text = text.replace('此外', '另外')
        
        elif style == "technical":
            # 确保专业术语的准确性
            # 这里可以添加术语检查和替换逻辑
            pass
        
        elif style == "educational":
            # 确保教育科普的清晰性
            if not text.startswith(('在金融领域', '金融', '投资', '银行', '保险')):
                text = '在金融领域，' + text
        
        return text

    def generate_investment_report(self, company: str, industry: str, 
                                 analysis_type: str = "基本面分析") -> Dict[str, Any]:
        """生成投资分析报告"""
        try:
            prompt = f"""
            请生成一份关于{company}（{industry}行业）的{analysis_type}报告。
            
            报告应包含：
            1. 公司概况
            2. 行业分析
            3. 财务分析
            4. 风险评估
            5. 投资建议
            
            请以专业的投资分析报告格式撰写。
            """
            
            return self.generate_text(prompt, max_length=800, style="formal")
            
        except Exception as e:
            logger.error(f"投资报告生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": "formal",
                "length": 0,
                "message": f"投资报告生成失败: {str(e)}"
            }

    def generate_risk_assessment(self, product_type: str, risk_factors: List[str]) -> Dict[str, Any]:
        """生成风险评估报告"""
        try:
            risk_factors_str = "、".join(risk_factors)
            prompt = f"""
            请生成一份关于{product_type}的风险评估报告。
            
            主要风险因素包括：{risk_factors_str}
            
            报告应包含：
            1. 风险识别
            2. 风险评估
            3. 风险控制措施
            4. 风险监控建议
            
            请以专业的风险评估报告格式撰写。
            """
            
            return self.generate_text(prompt, max_length=600, style="technical")
            
        except Exception as e:
            logger.error(f"风险评估报告生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": "technical",
                "length": 0,
                "message": f"风险评估报告生成失败: {str(e)}"
            }

    def generate_financial_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成财务分析报告"""
        try:
            # 构建财务数据描述
            data_desc = []
            for key, value in financial_data.items():
                data_desc.append(f"{key}: {value}")
            data_desc_str = "，".join(data_desc)
            
            prompt = f"""
            请基于以下财务数据生成财务分析报告：
            {data_desc_str}
            
            报告应包含：
            1. 财务指标分析
            2. 趋势分析
            3. 同业对比
            4. 财务健康度评估
            5. 改进建议
            
            请以专业的财务分析报告格式撰写。
            """
            
            return self.generate_text(prompt, max_length=700, style="formal")
            
        except Exception as e:
            logger.error(f"财务分析报告生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": "formal",
                "length": 0,
                "message": f"财务分析报告生成失败: {str(e)}"
            }

    def generate_market_research(self, market: str, research_focus: str) -> Dict[str, Any]:
        """生成市场研究报告"""
        try:
            prompt = f"""
            请生成一份关于{market}的市场研究报告，重点关注{research_focus}。
            
            报告应包含：
            1. 市场概况
            2. 市场规模和趋势
            3. 竞争格局分析
            4. 机会和挑战
            5. 发展前景预测
            
            请以专业的市场研究报告格式撰写。
            """
            
            return self.generate_text(prompt, max_length=800, style="formal")
            
        except Exception as e:
            logger.error(f"市场研究报告生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": "formal",
                "length": 0,
                "message": f"市场研究报告生成失败: {str(e)}"
            }

    def generate_educational_content(self, topic: str, target_audience: str = "普通投资者") -> Dict[str, Any]:
        """生成金融教育内容"""
        try:
            prompt = f"""
            请为{target_audience}生成关于{topic}的金融教育内容。
            
            要求：
            1. 内容通俗易懂
            2. 包含实际案例
            3. 提供实用建议
            4. 避免过于复杂的专业术语
            
            请以教育科普的方式撰写。
            """
            
            return self.generate_text(prompt, max_length=600, style="educational")
            
        except Exception as e:
            logger.error(f"金融教育内容生成失败: {str(e)}")
            return {
                "generated_text": "",
                "prompt": prompt,
                "style": "educational",
                "length": 0,
                "message": f"金融教育内容生成失败: {str(e)}"
            }

    def get_generation_statistics(self, generated_texts: List[Dict]) -> Dict[str, Any]:
        """获取文本生成统计信息"""
        if not generated_texts:
            return {
                "total_generations": 0,
                "average_length": 0,
                "style_distribution": {},
                "success_rate": 0.0
            }
        
        # 统计信息
        total_generations = len(generated_texts)
        successful_generations = sum(1 for text in generated_texts if text.get('generated_text'))
        total_length = sum(text.get('length', 0) for text in generated_texts)
        
        # 风格分布
        style_dist = {}
        for text in generated_texts:
            style = text.get('style', 'unknown')
            style_dist[style] = style_dist.get(style, 0) + 1
        
        return {
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "failed_generations": total_generations - successful_generations,
            "success_rate": successful_generations / total_generations if total_generations > 0 else 0.0,
            "average_length": total_length / total_generations if total_generations > 0 else 0,
            "style_distribution": style_dist,
            "total_length": total_length
        }
