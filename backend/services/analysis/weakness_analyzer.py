"""
薄弱点分析服务
分析学生的答题记录，生成六维能力图和薄弱点
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.models import AnswerRecord, Question, QuestionTag
import logging

logger = logging.getLogger(__name__)

# 六维能力定义
ABILITY_DIMENSIONS = {
    "计算能力": "计算能力",
    "逻辑推理": "逻辑推理",
    "空间想象": "空间想象",
    "问题分析": "问题分析",
    "创新思维": "创新思维",
    "综合应用": "综合应用"
}

# 题型到能力的映射
TYPE_TO_ABILITIES = {
    "choice": ["逻辑推理", "问题分析"],
    "calculation": ["计算能力", "问题分析"],
    "proof": ["逻辑推理", "空间想象", "创新思维", "综合应用"]
}

# 知识点到能力的映射（示例）
TAG_TO_ABILITIES = {
    "二次函数": ["计算能力", "逻辑推理", "综合应用"],
    "相似三角形": ["空间想象", "逻辑推理"],
    "一元二次方程": ["计算能力", "问题分析"],
    "圆": ["空间想象", "逻辑推理", "综合应用"],
    "韦达定理": ["计算能力", "逻辑推理"],
    "射影定理": ["空间想象", "逻辑推理", "创新思维"]
}


def analyze_weakness(user_id: int, db: Session) -> Dict:
    """
    分析用户的薄弱点
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        dict: 包含六维能力评分、知识点评分、薄弱点列表
    """
    # 获取用户的所有答题记录
    records = db.query(AnswerRecord).filter(
        AnswerRecord.user_id == user_id
    ).all()
    
    if not records:
        return {
            "abilities": {dim: 0 for dim in ABILITY_DIMENSIONS.keys()},
            "tag_scores": {},
            "weak_points": []
        }
    
    # 初始化能力评分
    ability_scores = {dim: [] for dim in ABILITY_DIMENSIONS.keys()}
    tag_scores = {}
    
    # 分析每条记录
    for record in records:
        question = record.question
        if not question:
            logger.warning(f"答题记录 {record.id} 没有关联题目")
            continue
        
        # 计算该题的能力得分（基于正确性、耗时、提示次数）
        score = calculate_question_score(record)
        logger.debug(f"记录 {record.id} 得分: {score}")
        
        # 根据题型分配能力
        # 处理枚举类型：可能是枚举对象、枚举值或字符串
        if hasattr(question.type, 'value'):
            question_type = question.type.value
        elif hasattr(question.type, 'name'):
            # 如果是枚举名称，转换为小写值
            type_name = question.type.name
            type_mapping = {
                'CHOICE': 'choice',
                'CALCULATION': 'calculation',
                'PROOF': 'proof'
            }
            question_type = type_mapping.get(type_name, str(question.type).lower())
        else:
            question_type = str(question.type).lower()
        
        abilities = TYPE_TO_ABILITIES.get(question_type, ["综合应用"])
        logger.debug(f"题目 {question.id} 类型: {question_type}, 能力: {abilities}")
        
        for ability in abilities:
            ability_scores[ability].append(score)
        
        # 统计知识点评分
        tags = [tag.tag for tag in question.tags]
        logger.debug(f"题目 {question.id} 标签: {tags}")
        if not tags:
            logger.warning(f"题目 {question.id} 没有标签")
        
        for tag in tags:
            if tag not in tag_scores:
                tag_scores[tag] = []
            tag_scores[tag].append(score)
    
    # 计算平均分
    ability_averages = {}
    for ability, scores in ability_scores.items():
        if scores:
            ability_averages[ability] = sum(scores) / len(scores)
        else:
            ability_averages[ability] = 0
    
    logger.info(f"用户 {user_id} 能力评分: {ability_averages}")
    
    # 计算知识点评分
    tag_averages = {}
    for tag, scores in tag_scores.items():
        if scores:
            tag_averages[tag] = sum(scores) / len(scores)
    
    logger.info(f"用户 {user_id} 知识点评分: {tag_averages}")
    
    # 识别薄弱点（得分低于60的知识点）
    weak_points = [
        tag for tag, score in tag_averages.items() if score < 60
    ]
    
    # 识别薄弱能力（得分低于60的能力）
    weak_abilities = [
        ability for ability, score in ability_averages.items() if score < 60
    ]
    
    return {
        "abilities": ability_averages,
        "tag_scores": tag_averages,
        "weak_points": weak_points,
        "weak_abilities": weak_abilities
    }


def calculate_question_score(record: AnswerRecord) -> float:
    """
    计算单题的得分（0-100）
    
    基于：
    - 正确性（40%）
    - 耗时（30%）
    - 提示次数（30%）
    """
    score = 0.0
    
    # 正确性得分
    if record.is_correct == 1:
        score += 40
    elif record.is_correct == 2:
        score += 0
    else:
        # 未判断，根据其他因素估算
        score += 20
    
    # 耗时得分（假设理想时间为60秒，超过300秒得分降低）
    if record.time_spent:
        if record.time_spent <= 60:
            time_score = 30
        elif record.time_spent <= 120:
            time_score = 25
        elif record.time_spent <= 300:
            time_score = 15
        else:
            time_score = 5
        score += time_score
    else:
        score += 15  # 默认中等得分
    
    # 提示次数得分（0次提示满分，每多一次扣5分）
    hint_score = max(0, 30 - record.hint_count * 5)
    score += hint_score
    
    return min(100, max(0, score))

