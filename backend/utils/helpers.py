import re
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

def sanitize_text(text: str) -> str:
    """清理和标准化文本"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除特殊字符（保留中文、英文、数字和基本标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\[\]{}""''\-]', '', text)
    
    return text

def generate_request_id() -> str:
    """生成唯一的请求ID"""
    timestamp = datetime.now().isoformat()
    random_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"req_{timestamp}_{random_suffix}"

def validate_financial_text(text: str) -> Dict[str, Any]:
    """验证金融文本的有效性"""
    result = {
        "is_valid": True,
        "issues": [],
        "suggestions": []
    }
    
    if not text or len(text.strip()) < 3:
        result["is_valid"] = False
        result["issues"].append("文本长度过短")
    
    if len(text) > 10000:
        result["is_valid"] = False
        result["issues"].append("文本长度超过限制")
    
    # 检查是否包含金融相关词汇
    financial_keywords = ["投资", "股票", "基金", "债券", "期货", "期权", "银行", "保险", "证券"]
    has_financial_content = any(keyword in text for keyword in financial_keywords)
    
    if not has_financial_content:
        result["suggestions"].append("建议输入包含金融相关内容的文本")
    
    return result

def format_response(data: Any, success: bool = True, message: str = "", request_id: str = "") -> Dict[str, Any]:
    """格式化API响应"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if request_id:
        response["request_id"] = request_id
    
    return response

def extract_financial_entities(text: str) -> List[Dict[str, str]]:
    """提取文本中可能的金融实体"""
    entities = []
    
    # 简单的正则表达式匹配
    patterns = {
        "company": r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:公司|集团|银行|保险|证券))',
        "stock_code": r'([0-9]{6})',
        "currency": r'([¥$€£])\s*([0-9,]+(?:\.[0-9]{2})?)',
        "percentage": r'([0-9]+(?:\.[0-9]+)?)\s*%',
        "date": r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
    }
    
    for entity_type, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            entities.append({
                "type": entity_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
    
    return entities

def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（简单的Jaccard相似度）"""
    if not text1 or not text2:
        return 0.0
    
    # 分词（简单的按空格和标点分割）
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 and not words2:
        return 1.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def rate_limit_key(request: Any) -> str:
    """生成限流键"""
    # 这里可以根据需要实现更复杂的限流逻辑
    return f"rate_limit:{request.client.host if hasattr(request, 'client') else 'unknown'}"

def log_api_call(endpoint: str, method: str, duration: float, status_code: int, user_agent: str = ""):
    """记录API调用日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "duration": duration,
        "status_code": status_code,
        "user_agent": user_agent
    }
    
    # 这里可以集成到日志系统
    print(f"API Call: {json.dumps(log_entry, ensure_ascii=False)}")
