import ollama
import logging
from typing import List, Dict, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrService:
    """
    金融拼写纠正服务
    纠正金融术语的拼写错误，支持多种纠正策略
    """
    
    def __init__(self):
        """初始化金融拼写纠正服务"""
        # 常见金融术语拼写错误
        self.common_typos = {
            # 投资相关
            "投姿": "投资",
            "股票": "股票",  # 正确拼写
            "债券": "债券",  # 正确拼写
            "基金": "基金",  # 正确拼写
            "期货": "期货",  # 正确拼写
            "期权": "期权",  # 正确拼写
            "收益率": "收益率",  # 正确拼写
            "风险": "风险",  # 正确拼写
            
            # 银行相关
            "银行": "银行",  # 正确拼写
            "存款": "存款",  # 正确拼写
            "贷款": "贷款",  # 正确拼写
            "利率": "利率",  # 正确拼写
            "汇率": "汇率",  # 正确拼写
            "账户": "账户",  # 正确拼写
            "信用卡": "信用卡",  # 正确拼写
            
            # 保险相关
            "保险": "保险",  # 正确拼写
            "理赔": "理赔",  # 正确拼写
            "保费": "保费",  # 正确拼写
            "保单": "保单",  # 正确拼写
            "受益人": "受益人",  # 正确拼写
            
            # 证券相关
            "证券": "证券",  # 正确拼写
            "交易所": "交易所",  # 正确拼写
            "经纪人": "经纪人",  # 正确拼写
            "分析师": "分析师",  # 正确拼写
            
            # 会计相关
            "会计": "会计",  # 正确拼写
            "财务报表": "财务报表",  # 正确拼写
            "资产负债表": "资产负债表",  # 正确拼写
            "利润表": "利润表",  # 正确拼写
            "现金流量表": "现金流量表",  # 正确拼写
            
            # 税务相关
            "税务": "税务",  # 正确拼写
            "税率": "税率",  # 正确拼写
            "税收": "税收",  # 正确拼写
            "申报": "申报",  # 正确拼写
            "减免": "减免",  # 正确拼写
        }
        
        # 金融术语模式
        self.financial_patterns = [
            r'投[资姿]',           # 投资
            r'[银银]行',           # 银行
            r'[保保]险',           # 保险
            r'[证证]券',           # 证券
            r'[基基]金',           # 基金
            r'[股股]票',           # 股票
            r'[债债]券',           # 债券
            r'[期期]货',           # 期货
            r'[期期]权',           # 期权
            r'[汇汇]率',           # 汇率
            r'[利利]率',           # 利率
            r'[收收]益率',         # 收益率
            r'[风风]险',           # 风险
            r'[会会]计',           # 会计
            r'[税税]务',           # 税务
            r'[监监]管',           # 监管
        ]
        
        # 金融术语类别
        self.financial_categories = [
            "投资", "银行", "保险", "证券", "衍生品", 
            "风险管理", "会计", "税务", "监管", "市场"
        ]

    def correct_text(self, text: str, llm_options: Dict[str, str] = None) -> Dict[str, Any]:
        """
        纠正金融文本中的拼写错误
        
        Args:
            text: 输入文本
            llm_options: 大语言模型配置
            
        Returns:
            纠正结果
        """
        try:
            # 使用规则匹配进行初步纠正
            rule_corrections = self._correct_by_rules(text)
            
            # 使用LLM进行智能纠正
            llm_corrections = self._correct_by_llm(text, llm_options)
            
            # 合并纠正结果
            all_corrections = self._merge_corrections(rule_corrections, llm_corrections)
            
            # 应用纠正
            corrected_text = self._apply_corrections(text, all_corrections)
            
            # 计算纠正统计
            correction_stats = self._calculate_correction_stats(all_corrections)
            
            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "corrections": all_corrections,
                "correction_count": len(all_corrections),
                "correction_stats": correction_stats,
                "message": "拼写纠正完成"
            }
            
        except Exception as e:
            logger.error(f"拼写纠正失败: {str(e)}")
            return {
                "original_text": text,
                "corrected_text": text,
                "corrections": [],
                "correction_count": 0,
                "correction_stats": {},
                "message": f"拼写纠正失败: {str(e)}"
            }

    def _correct_by_rules(self, text: str) -> List[Dict]:
        """使用规则进行拼写纠正"""
        corrections = []
        
        # 检查常见拼写错误
        for typo, correct in self.common_typos.items():
            if typo in text:
                start_pos = text.find(typo)
                corrections.append({
                    "original": typo,
                    "corrected": correct,
                    "start": start_pos,
                    "end": start_pos + len(typo),
                    "type": "common_typo",
                    "confidence": 0.9,
                    "method": "rule_based"
                })
        
        # 使用正则表达式检查模式
        for pattern in self.financial_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                matched_text = match.group()
                # 这里应该有一个映射来找到正确的拼写
                # 暂时使用匹配的文本作为正确拼写
                corrections.append({
                    "original": matched_text,
                    "corrected": matched_text,  # 应该映射到正确拼写
                    "start": match.start(),
                    "end": match.end(),
                    "type": "pattern_match",
                    "confidence": 0.7,
                    "method": "rule_based"
                })
        
        return corrections

    def _correct_by_llm(self, text: str, llm_options: Dict[str, str] = None) -> List[Dict]:
        """使用大语言模型进行拼写纠正"""
        try:
            if not llm_options:
                llm_options = {"provider": "ollama", "model": "qwen2.5:7b"}
            
            provider = llm_options.get("provider", "ollama")
            model = llm_options.get("model", "qwen2.5:7b")
            
            if provider == "ollama":
                return self._correct_with_ollama(text, model)
            else:
                logger.warning(f"不支持的LLM提供商: {provider}")
                return []
                
        except Exception as e:
            logger.error(f"LLM拼写纠正失败: {str(e)}")
            return []

    def _correct_with_ollama(self, text: str, model: str) -> List[Dict]:
        """使用Ollama进行拼写纠正"""
        try:
            prompt = f"""
            请检查以下金融文本中的拼写错误，并提供纠正建议。
            
            文本: {text}
            
            请以JSON格式返回结果，格式如下:
            {{
                "corrections": [
                    {{
                        "original": "原始文本",
                        "corrected": "纠正后文本",
                        "start": 起始位置,
                        "end": 结束位置,
                        "type": "错误类型",
                        "confidence": 置信度(0-1),
                        "explanation": "纠正说明"
                    }}
                ]
            }}
            
            只返回JSON，不要其他内容。如果没有拼写错误，返回空的corrections数组。
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
                corrections = result.get('corrections', [])
                
                # 添加方法标识
                for correction in corrections:
                    correction['method'] = 'llm_based'
                
                return corrections
                
            except json.JSONDecodeError:
                logger.warning("Ollama返回的不是有效JSON格式")
                return []
                
        except Exception as e:
            logger.error(f"Ollama拼写纠正失败: {str(e)}")
            return []

    def _merge_corrections(self, rule_corrections: List[Dict], 
                          llm_corrections: List[Dict]) -> List[Dict]:
        """合并和去重纠正结果"""
        all_corrections = []
        seen_corrections = set()
        
        # 添加规则纠正结果
        for correction in rule_corrections:
            key = (correction['start'], correction['end'], correction['original'])
            if key not in seen_corrections:
                all_corrections.append(correction)
                seen_corrections.add(key)
        
        # 添加LLM纠正结果
        for correction in llm_corrections:
            key = (correction['start'], correction['end'], correction['original'])
            if key not in seen_corrections:
                all_corrections.append(correction)
                seen_corrections.add(key)
        
        # 按起始位置排序
        all_corrections.sort(key=lambda x: x['start'])
        
        return all_corrections

    def _apply_corrections(self, text: str, corrections: List[Dict]) -> str:
        """应用纠正到原文本"""
        if not corrections:
            return text
        
        # 从后往前应用纠正，避免位置偏移
        corrected_text = text
        for correction in reversed(corrections):
            start = correction['start']
            end = correction['end']
            original = correction['original']
            corrected = correction['corrected']
            
            # 验证位置和文本匹配
            if (start < len(corrected_text) and 
                end <= len(corrected_text) and 
                corrected_text[start:end] == original):
                corrected_text = corrected_text[:start] + corrected + corrected_text[end:]
        
        return corrected_text

    def _calculate_correction_stats(self, corrections: List[Dict]) -> Dict[str, Any]:
        """计算纠正统计信息"""
        if not corrections:
            return {
                "total_corrections": 0,
                "type_distribution": {},
                "method_distribution": {},
                "confidence_distribution": {}
            }
        
        # 类型分布
        type_dist = {}
        for correction in corrections:
            correction_type = correction.get('type', 'unknown')
            type_dist[correction_type] = type_dist.get(correction_type, 0) + 1
        
        # 方法分布
        method_dist = {}
        for correction in corrections:
            method = correction.get('method', 'unknown')
            method_dist[method] = method_dist.get(method, 0) + 1
        
        # 置信度分布
        confidence_dist = {"high": 0, "medium": 0, "low": 0}
        for correction in corrections:
            conf = correction.get('confidence', 0)
            if conf >= 0.8:
                confidence_dist["high"] += 1
            elif conf >= 0.6:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1
        
        return {
            "total_corrections": len(corrections),
            "type_distribution": type_dist,
            "method_distribution": method_dist,
            "confidence_distribution": confidence_dist
        }

    def suggest_corrections(self, word: str) -> List[str]:
        """为单个词提供纠正建议"""
        suggestions = []
        
        # 检查常见拼写错误
        if word in self.common_typos:
            suggestions.append(self.common_typos[word])
        
        # 使用编辑距离算法找到相似词
        # 这里简化实现，实际应该使用更复杂的算法
        for correct_word in self.common_typos.values():
            if self._calculate_similarity(word, correct_word) > 0.7:
                suggestions.append(correct_word)
        
        return list(set(suggestions))

    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """计算两个词的相似度（简化实现）"""
        if word1 == word2:
            return 1.0
        
        # 计算编辑距离
        len1, len2 = len(word1), len(word2)
        if len1 == 0:
            return 0.0
        if len2 == 0:
            return 0.0
        
        # 简单的相似度计算
        common_chars = sum(1 for c in word1 if c in word2)
        max_len = max(len1, len2)
        
        return common_chars / max_len

    def validate_correction(self, original: str, corrected: str) -> Dict[str, Any]:
        """验证纠正的合理性"""
        # 检查长度变化
        length_change = len(corrected) - len(original)
        
        # 检查字符变化
        char_changes = sum(1 for i, c in enumerate(original) 
                          if i >= len(corrected) or c != corrected[i])
        
        # 计算合理性分数
        if original == corrected:
            validity_score = 1.0
        elif length_change == 0 and char_changes <= 2:
            validity_score = 0.8
        elif abs(length_change) <= 1 and char_changes <= 3:
            validity_score = 0.6
        else:
            validity_score = 0.3
        
        return {
            "original": original,
            "corrected": corrected,
            "length_change": length_change,
            "char_changes": char_changes,
            "validity_score": validity_score,
            "is_reasonable": validity_score >= 0.6,
            "suggestions": self.suggest_corrections(original)
        }
