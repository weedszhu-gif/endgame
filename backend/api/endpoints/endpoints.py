from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 导入服务层
from services.hint.socratic_hint import generate_socratic_hint
from services.ai.ai_service import get_ai_hint

# 导入数据库模型和依赖
from models.base import get_db
from models.models import (
    Question,
    QuestionTag,
    AnswerRecord,
    StudentAnalysis,
    User,
    HintFeedback,
    HintFeedback,
)

router = APIRouter(prefix="/api", tags=["math-challenge"])


# 请求和响应模型
class StepRequest(BaseModel):
    content: str
    use_ai: bool = False


class HintResponse(BaseModel):
    type: str = "hint"
    content: str


class HealthResponse(BaseModel):
    status: str
    message: str


@router.post("/hint", response_model=HintResponse)
async def get_hint(request: StepRequest):
    """
    获取解题提示

    - **content**: 解题步骤内容
    - **use_ai**: 是否直接使用AI（默认False，先尝试本地规则）
    """
    try:
        if request.use_ai:
            # 直接使用AI
            hint = await get_ai_hint(request.content)
        else:
            # 先尝试本地规则
            hint = generate_socratic_hint(request.content)
            if not hint:
                # 本地规则没有匹配时，使用AI
                hint = await get_ai_hint(request.content)

        return HintResponse(content=hint)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")


@router.post("/socratic-hint", response_model=HintResponse)
def get_socratic_hint(request: StepRequest):
    """
    获取基于本地规则的苏格拉底式提示

    - **content**: 解题步骤内容
    """
    try:
        hint = generate_socratic_hint(request.content)
        if not hint:
            raise HTTPException(status_code=404, detail="没有找到匹配的提示规则")

        return HintResponse(content=hint)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")


@router.post("/ai-hint", response_model=HintResponse)
async def get_ai_hint_endpoint(request: StepRequest):
    """
    获取基于AI的提示

    - **content**: 解题步骤内容
    """
    try:
        hint = await get_ai_hint(request.content)
        return HintResponse(content=hint)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI提示失败: {str(e)}")


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    健康检查
    """
    return HealthResponse(status="ok", message="API服务正常运行")


# 题目相关模型
class QuestionResponse(BaseModel):
    id: int
    type: str
    content: str
    difficulty: int
    solution: Optional[str] = None
    hint_pattern: Optional[str] = None
    tags: List[str] = []

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int


@router.get("/questions", response_model=QuestionListResponse)
def get_questions(
    difficulty: Optional[int] = None,
    tags: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    获取题目列表

    - **difficulty**: 难度等级 (1-5)，对应：1-2初级，3中级，4-5高级
    - **tags**: 知识点标签，多个用逗号分隔
    - **limit**: 返回数量限制
    """
    try:
        query = db.query(Question)

        # 根据难度筛选
        if difficulty is not None:
            if difficulty == 1:  # 初级：难度1-2
                query = query.filter(Question.difficulty.in_([1, 2]))
            elif difficulty == 2:  # 中级：难度3
                query = query.filter(Question.difficulty == 3)
            elif difficulty == 3:  # 高级：难度4-5
                query = query.filter(Question.difficulty.in_([4, 5]))

        # 根据知识点标签筛选
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            # 查找包含这些标签的题目ID
            question_ids = (
                db.query(QuestionTag.question_id)
                .filter(QuestionTag.tag.in_(tag_list))
                .distinct()
                .all()
            )
            question_ids = [qid[0] for qid in question_ids]
            query = query.filter(Question.id.in_(question_ids))

        # 获取题目
        questions = query.limit(limit).all()

        # 构建响应
        result = []
        for q in questions:
            # 获取题目的所有标签
            q_tags = (
                db.query(QuestionTag.tag).filter(QuestionTag.question_id == q.id).all()
            )
            tags_list = [tag[0] for tag in q_tags]

            result.append(
                QuestionResponse(
                    id=q.id,
                    type=q.type.value if hasattr(q.type, "value") else str(q.type),
                    content=q.content,
                    difficulty=q.difficulty,
                    solution=q.solution,
                    hint_pattern=q.hint_pattern,
                    tags=tags_list,
                )
            )

        return QuestionListResponse(questions=result, total=len(result))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个题目
    """
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")

        # 获取题目的所有标签
        q_tags = (
            db.query(QuestionTag.tag)
            .filter(QuestionTag.question_id == question.id)
            .all()
        )
        tags_list = [tag[0] for tag in q_tags]

        return QuestionResponse(
            id=question.id,
            type=(
                question.type.value
                if hasattr(question.type, "value")
                else str(question.type)
            ),
            content=question.content,
            difficulty=question.difficulty,
            solution=question.solution,
            hint_pattern=question.hint_pattern,
            tags=tags_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.get("/tags", response_model=List[str])
def get_all_tags(db: Session = Depends(get_db)):
    """
    获取所有知识点标签
    """
    try:
        tags = db.query(QuestionTag.tag).distinct().all()
        return [tag[0] for tag in tags]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")


# 答题记录相关模型
class AnswerRecordRequest(BaseModel):
    user_id: Optional[int] = None
    question_id: int
    student_input: str
    level: Optional[str] = None
    tag: Optional[str] = None
    time_spent: Optional[int] = None
    hint_count: int = 0
    is_correct: Optional[int] = 0
    solution_method: Optional[str] = None


class AnswerRecordResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    question_id: int
    student_input: Optional[str] = None
    time_spent: Optional[int] = None
    hint_count: int = 0
    is_correct: Optional[int] = 0
    created_at: str
    question_content: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/answer-records", response_model=AnswerRecordResponse)
async def create_answer_record(
    record: AnswerRecordRequest, db: Session = Depends(get_db)
):
    """
    创建答题记录，并使用AI自动判断答案是否正确
    """
    try:
        # 获取题目信息
        question = db.query(Question).filter(Question.id == record.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")

        question_content = question.content if question else None
        question_solution = question.solution if question else None

        # 如果未提供is_correct或为0，使用AI自动判断
        is_correct = record.is_correct
        if is_correct is None or is_correct == 0:
            try:
                from services.ai.ai_service import evaluate_answer

                evaluation = await evaluate_answer(
                    question_content=question_content or "",
                    question_solution=question_solution or "",
                    student_answer=record.student_input or "",
                )
                is_correct = evaluation.get("is_correct", 0)
                logger.info(
                    f"AI评估结果: is_correct={is_correct}, feedback={evaluation.get('feedback')}"
                )
            except Exception as e:
                logger.error(f"AI评估答案失败: {str(e)}", exc_info=True)
                # AI评估失败时，保持未判断状态
                is_correct = 0

        db_record = AnswerRecord(
            user_id=record.user_id,
            question_id=record.question_id,
            student_input=record.student_input,
            level=record.level,
            tag=record.tag,
            time_spent=record.time_spent,
            hint_count=record.hint_count,
            is_correct=is_correct,
            solution_method=record.solution_method,
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return AnswerRecordResponse(
            id=db_record.id,
            user_id=db_record.user_id,
            question_id=db_record.question_id,
            student_input=db_record.student_input,
            time_spent=db_record.time_spent,
            hint_count=db_record.hint_count,
            is_correct=db_record.is_correct,
            created_at=db_record.created_at.isoformat(),
            question_content=question_content,
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"保存答题记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"保存答题记录失败: {str(e)}")


@router.get("/answer-records", response_model=List[AnswerRecordResponse])
def get_answer_records(
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    获取答题记录列表

    - **user_id**: 用户ID（可选）
    - **question_id**: 题目ID（可选）
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    try:
        query = db.query(AnswerRecord)

        if user_id:
            query = query.filter(AnswerRecord.user_id == user_id)
        if question_id:
            query = query.filter(AnswerRecord.question_id == question_id)

        records = (
            query.order_by(AnswerRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for record in records:
            question = (
                db.query(Question).filter(Question.id == record.question_id).first()
            )
            result.append(
                AnswerRecordResponse(
                    id=record.id,
                    user_id=record.user_id,
                    question_id=record.question_id,
                    student_input=record.student_input,
                    time_spent=record.time_spent,
                    hint_count=record.hint_count,
                    is_correct=record.is_correct,
                    created_at=record.created_at.isoformat(),
                    question_content=question.content if question else None,
                )
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取答题记录失败: {str(e)}")


# 分析数据相关模型
class AnalysisResponse(BaseModel):
    abilities: dict
    tag_scores: dict
    weak_points: List[str]
    weak_abilities: List[str]
    summary: str
    recommended_questions: List[dict] = []


@router.get("/analysis", response_model=AnalysisResponse)
def get_analysis_by_question(
    question_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    获取学习分析数据（兼容旧版本，支持question_id或user_id）

    - **question_id**: 题目ID（可选，用于单题分析）
    - **user_id**: 用户ID（可选，用于用户整体分析）
    """
    # 如果提供了user_id，使用用户分析
    if user_id:
        return get_user_analysis(user_id, db)

    # 如果提供了question_id，返回基于题目的分析
    if question_id:
        try:
            # 获取该题目的标签
            tags = []
            q_tags = (
                db.query(QuestionTag.tag)
                .filter(QuestionTag.question_id == question_id)
                .all()
            )
            tags = [tag[0] for tag in q_tags]

            # 生成示例分析数据（基于题目标签）
            abilities = {
                "计算能力": 75,
                "逻辑推理": 70,
                "空间想象": 65,
                "问题分析": 72,
                "创新思维": 68,
                "综合应用": 70,
            }

            tag_scores = {}
            for tag in tags:
                tag_scores[tag] = 65

            summary = f"根据您对本题的答题表现，建议加强相关能力的训练。"
            if tags:
                summary += f"在知识点方面，建议重点复习{', '.join(tags)}相关内容。"

            return AnalysisResponse(
                abilities=abilities,
                tag_scores=tag_scores,
                weak_points=[],
                weak_abilities=[],
                summary=summary,
                recommended_questions=[],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")

    # 如果没有提供参数，返回默认数据
    return AnalysisResponse(
        abilities={
            "计算能力": 75,
            "逻辑推理": 70,
            "空间想象": 65,
            "问题分析": 72,
            "创新思维": 68,
            "综合应用": 70,
        },
        tag_scores={},
        weak_points=[],
        weak_abilities=[],
        summary="请提供question_id或user_id以获取详细分析。",
        recommended_questions=[],
    )


@router.get("/analysis/{user_id}", response_model=AnalysisResponse)
def get_user_analysis(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的学习分析数据（包含六维能力图和薄弱点）

    - **user_id**: 用户ID
    """
    from services.analysis.weakness_analyzer import analyze_weakness
    from services.recommendation.question_recommender import recommend_questions

    try:
        # 分析薄弱点
        analysis = analyze_weakness(user_id, db)

        # 推荐题目
        recommended = recommend_questions(
            user_id=user_id,
            weak_points=analysis["weak_points"],
            weak_abilities=analysis.get("weak_abilities", []),
            db=db,
            limit=3,
        )

        # 格式化推荐题目
        recommended_list = []
        for q in recommended:
            tags = [tag.tag for tag in q.tags]
            recommended_list.append(
                {
                    "id": q.id,
                    "content": q.content,
                    "difficulty": q.difficulty,
                    "type": q.type.value if hasattr(q.type, "value") else str(q.type),
                    "tags": tags,
                }
            )

        # 生成总结
        summary = generate_analysis_summary(analysis)

        return AnalysisResponse(
            abilities=analysis["abilities"],
            tag_scores=analysis["tag_scores"],
            weak_points=analysis["weak_points"],
            weak_abilities=analysis.get("weak_abilities", []),
            summary=summary,
            recommended_questions=recommended_list,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")


def generate_analysis_summary(analysis: dict) -> str:
    """生成分析总结"""
    abilities = analysis["abilities"]
    weak_points = analysis["weak_points"]
    weak_abilities = analysis.get("weak_abilities", [])
    tag_scores = analysis.get("tag_scores", {})

    summary_parts = []

    # 检查是否有数据
    has_data = any(score > 0 for score in abilities.values()) or len(tag_scores) > 0

    if not has_data:
        return "您还没有答题记录。请先完成一些题目，系统才能为您生成个性化的学习分析报告。建议从基础题目开始，逐步提升难度。"

    # 能力总结
    non_zero_abilities = {k: v for k, v in abilities.items() if v > 0}
    if non_zero_abilities:
        top_ability = max(non_zero_abilities.items(), key=lambda x: x[1])
        summary_parts.append(
            f"您的{top_ability[0]}表现最佳，得分{top_ability[1]:.1f}分。"
        )

    if weak_abilities:
        summary_parts.append(f"需要加强的能力：{', '.join(weak_abilities)}。")
    elif non_zero_abilities:
        # 找出得分最低的能力
        if non_zero_abilities:
            min_ability = min(non_zero_abilities.items(), key=lambda x: x[1])
            if min_ability[1] < 70:
                summary_parts.append(
                    f"建议重点提升{min_ability[0]}，当前得分{min_ability[1]:.1f}分。"
                )

    # 知识点总结
    if weak_points:
        summary_parts.append(f"薄弱知识点：{', '.join(weak_points[:3])}。")
        summary_parts.append("建议针对这些知识点进行专项训练。")
    elif tag_scores:
        # 找出得分最低的知识点
        min_tag = min(tag_scores.items(), key=lambda x: x[1])
        if min_tag[1] < 70:
            summary_parts.append(
                f"建议重点复习{min_tag[0]}，当前掌握度{min_tag[1]:.1f}%。"
            )
        else:
            summary_parts.append("您的知识点掌握较为均衡，继续保持！")

    if not summary_parts:
        summary_parts.append("请继续完成更多题目，系统将为您提供更详细的分析。")

    return " ".join(summary_parts)


@router.get("/questions/{question_id}/solutions")
def get_question_solutions(question_id: int, db: Session = Depends(get_db)):
    """
    获取题目的多种解法（残局模式）

    - **question_id**: 题目ID
    """
    from services.recommendation.question_recommender import get_endgame_questions

    try:
        # 先检查题目是否存在
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"题目 {question_id} 不存在")

        # 获取残局模式的解法
        solutions = get_endgame_questions(question_id, db)

        if solutions is None:
            # 如果不是残局模式，返回标准解法
            return [
                {
                    "method": "标准解法",
                    "steps": question.solution or "暂无详细步骤",
                    "description": "这是题目的标准解法",
                }
            ]

        # 返回多种解法
        return solutions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取解法失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取解法失败: {str(e)}")


# 用户相关模型和端点
class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    获取所有用户列表
    """
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                created_at=user.created_at.isoformat() if user.created_at else "",
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


# 提示反馈相关模型和端点
class HintFeedbackRequest(BaseModel):
    user_id: Optional[int] = None
    question_id: int
    student_input: Optional[str] = None
    hint_content: str
    feedback_type: int  # 1=赞，2=踩
    hint_source: Optional[str] = None  # socratic 或 ai
    hint_keyword: Optional[str] = None  # 匹配的关键词


class HintFeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    question_id: int
    hint_content: str
    feedback_type: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/hint-feedback", response_model=HintFeedbackResponse)
def create_hint_feedback(feedback: HintFeedbackRequest, db: Session = Depends(get_db)):
    """
    创建AI提示反馈（赞/踩）
    """
    try:
        db_feedback = HintFeedback(
            user_id=feedback.user_id,
            question_id=feedback.question_id,
            student_input=feedback.student_input,
            hint_content=feedback.hint_content,
            feedback_type=feedback.feedback_type,
            hint_source=feedback.hint_source,
            hint_keyword=feedback.hint_keyword,
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        return HintFeedbackResponse(
            id=db_feedback.id,
            user_id=db_feedback.user_id,
            question_id=db_feedback.question_id,
            hint_content=db_feedback.hint_content,
            feedback_type=db_feedback.feedback_type,
            created_at=db_feedback.created_at.isoformat(),
        )
    except Exception as e:
        db.rollback()
        logger.error(f"保存提示反馈失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"保存提示反馈失败: {str(e)}")


@router.get("/hint-feedback/stats")
def get_hint_feedback_stats(
    hint_keyword: Optional[str] = None,
    hint_source: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    获取提示反馈统计，用于优化提示生成
    返回格式：{keyword: {likes: count, dislikes: count, score: float}}
    """
    try:
        from sqlalchemy import func, case

        query = db.query(HintFeedback)

        if hint_keyword:
            query = query.filter(HintFeedback.hint_keyword == hint_keyword)
        if hint_source:
            query = query.filter(HintFeedback.hint_source == hint_source)

        # 统计每个关键词的赞/踩数量
        stats_query = (
            db.query(
                HintFeedback.hint_keyword,
                func.sum(
                    case((HintFeedback.feedback_type == 1, 1), else_=0)
                ).label("likes"),
                func.sum(
                    case((HintFeedback.feedback_type == 2, 1), else_=0)
                ).label("dislikes"),
                func.count(HintFeedback.id).label("total"),
            )
            .filter(HintFeedback.hint_keyword.isnot(None))
            .group_by(HintFeedback.hint_keyword)
            .limit(limit)
            .all()
        )

        stats = {}
        for row in stats_query:
            keyword = row.hint_keyword
            likes = row.likes or 0
            dislikes = row.dislikes or 0
            total = row.total or 0
            score = likes / total if total > 0 else 0.5

            stats[keyword] = {
                "likes": likes,
                "dislikes": dislikes,
                "total": total,
                "score": score,
            }

        return stats
    except Exception as e:
        logger.error(f"获取提示反馈统计失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取提示反馈统计失败: {str(e)}")
