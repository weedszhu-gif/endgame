from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# 导入服务层
from services.hint.socratic_hint import generate_socratic_hint
from services.ai.ai_service import get_ai_hint

# 导入数据库模型和依赖
from models.base import get_db
from models.models import Question, QuestionTag, AnswerRecord, StudentAnalysis

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
    question_id: int
    student_input: str
    level: Optional[str] = None
    tag: Optional[str] = None
    time_spent: Optional[int] = None
    hint_count: int = 0


class AnswerRecordResponse(BaseModel):
    id: int
    question_id: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/answer-records", response_model=AnswerRecordResponse)
def create_answer_record(record: AnswerRecordRequest, db: Session = Depends(get_db)):
    """
    创建答题记录
    """
    try:
        db_record = AnswerRecord(
            question_id=record.question_id,
            student_input=record.student_input,
            level=record.level,
            tag=record.tag,
            time_spent=record.time_spent,
            hint_count=record.hint_count,
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return AnswerRecordResponse(
            id=db_record.id,
            question_id=db_record.question_id,
            created_at=db_record.created_at.isoformat(),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存答题记录失败: {str(e)}")


# 分析数据相关模型
class AnalysisResponse(BaseModel):
    abilities: dict
    tag_scores: dict
    summary: str


@router.get("/analysis", response_model=AnalysisResponse)
def get_analysis(question_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    获取学习分析数据

    - **question_id**: 题目ID（可选）
    """
    try:
        # 这里可以根据实际答题记录计算分析数据
        # 目前返回示例数据

        # 获取该题目的标签
        tags = []
        if question_id:
            q_tags = (
                db.query(QuestionTag.tag)
                .filter(QuestionTag.question_id == question_id)
                .all()
            )
            tags = [tag[0] for tag in q_tags]

        # 生成示例分析数据
        abilities = {
            "逻辑推理": 75,
            "空间想象": 60,
            "计算能力": 80,
            "问题分析": 70,
            "创新思维": 65,
            "知识应用": 72,
        }

        tag_scores = {}
        for tag in tags:
            # 可以根据历史答题记录计算实际分数
            tag_scores[tag] = 65

        summary = f"根据您的答题表现，建议加强空间想象和创新思维能力的训练。"
        if tags:
            summary += f"在知识点方面，建议重点复习{', '.join(tags)}相关内容。"

        # 保存分析数据
        analysis = StudentAnalysis(
            abilities=abilities, tag_scores=tag_scores, summary=summary
        )
        db.add(analysis)
        db.commit()

        return AnalysisResponse(
            abilities=abilities, tag_scores=tag_scores, summary=summary
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")
