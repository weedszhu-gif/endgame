import re
from typing import List, Optional


def sanitize_string(text: str) -> str:
    """
    清理字符串，去除特殊字符和多余空格
    
    Args:
        text: 输入字符串
    
    Returns:
        str: 清理后的字符串
    """
    # 去除首尾空格
    text = text.strip()
    
    # 去除多余空格（连续空格替换为单个空格）
    text = re.sub(r'\s+', ' ', text)
    
    # 去除特殊字符（保留中文、英文、数字、常见标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s,.!?;:，。！？；：]', '', text)
    
    return text


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度
    
    Args:
        text: 输入字符串
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        str: 截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    提取字符串中的关键词（简单实现，可扩展）
    
    Args:
        text: 输入字符串
        max_keywords: 最大关键词数量
    
    Returns:
        List[str]: 关键词列表
    """
    # 简单实现，去除常见词和标点，提取长度大于等于2的词
    stop_words = set([
        "的", "了", "和", "是", "在", "有", "我", "你", "他", "她", "它",
        "这", "那", "我们", "你们", "他们", "她们", "它们", "来", "去", "上", "下",
        "大", "小", "多", "少", "好", "坏", "很", "非常", "不", "没", "要", "会"
    ])
    
    # 清理文本
    text = sanitize_string(text)
    
    # 分词（简单的空格分词，中文需要更复杂的分词库）
    words = text.split()
    
    # 过滤关键词
    keywords = []
    for word in words:
        if word not in stop_words and len(word) >= 2 and word not in keywords:
            keywords.append(word)
            if len(keywords) >= max_keywords:
                break
    
    return keywords
