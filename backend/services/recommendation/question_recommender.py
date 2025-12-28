"""
题目推荐服务
基于薄弱点推荐训练题目
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models.models import Question, QuestionTag, AnswerRecord
import logging

logger = logging.getLogger(__name__)


def recommend_questions(
    user_id: int,
    weak_points: List[str],
    weak_abilities: List[str],
    db: Session,
    limit: int = 3
) -> List[Question]:
    """
    基于薄弱点推荐题目
    
    Args:
        user_id: 用户ID
        weak_points: 薄弱知识点列表
        weak_abilities: 薄弱能力列表
        db: 数据库会话
        limit: 推荐题目数量
        
    Returns:
        List[Question]: 推荐的题目列表
    """
    # 获取用户已做过的题目ID
    answered_question_ids = db.query(AnswerRecord.question_id).filter(
        AnswerRecord.user_id == user_id
    ).distinct().all()
    answered_question_ids = [qid[0] for qid in answered_question_ids]
    
    # 如果没有薄弱点，推荐中等难度的综合题
    if not weak_points and not weak_abilities:
        recommended = db.query(Question).filter(
            ~Question.id.in_(answered_question_ids),
            Question.difficulty == 3
        ).limit(limit).all()
        return recommended
    
    # 基于薄弱知识点推荐
    recommended_questions = []
    
    # 优先推荐薄弱知识点相关的题目
    for weak_point in weak_points[:2]:  # 最多考虑前2个薄弱点
        questions = db.query(Question).join(QuestionTag).filter(
            QuestionTag.tag == weak_point,
            ~Question.id.in_(answered_question_ids)
        ).limit(limit).all()
        
        for q in questions:
            if q not in recommended_questions:
                recommended_questions.append(q)
                if len(recommended_questions) >= limit:
                    break
        
        if len(recommended_questions) >= limit:
            break
    
    # 如果推荐数量不足，补充中等难度的题目
    if len(recommended_questions) < limit:
        remaining = limit - len(recommended_questions)
        additional = db.query(Question).filter(
            ~Question.id.in_(answered_question_ids),
            Question.id.notin_([q.id for q in recommended_questions]),
            Question.difficulty.in_([2, 3])  # 中等难度
        ).limit(remaining).all()
        recommended_questions.extend(additional)
    
    return recommended_questions[:limit]


def get_endgame_questions(
    question_id: int,
    db: Session
) -> Optional[List[Dict]]:
    """
    获取题目的多种解法（残局模式）
    
    Args:
        question_id: 题目ID
        db: 数据库会话
        
    Returns:
        List[Dict]: 解法列表，每个解法包含方法名、步骤、说明
    """
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        
        if not question:
            return None
        
        # 检查是否是残局模式
        is_endgame = getattr(question, 'is_endgame', 0)
        if not is_endgame:
            return None
        
        # 如果有存储的多种解法，返回它们
        solutions = getattr(question, 'solutions', None)
        if solutions:
            return solutions
        
        # 如果没有存储多种解法，但题目标记为残局模式，返回默认解法
        return [{
            "method": "标准解法",
            "steps": question.solution or "暂无详细步骤",
            "description": "这是题目的标准解法"
        }]
    except Exception as e:
        logger.error(f"获取残局题目失败: {str(e)}", exc_info=True)
        return None

