from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import enum


# 题目类型枚举
class QuestionType(str, enum.Enum):
    CHOICE = "choice"
    CALCULATION = "calculation"
    PROOF = "proof"


class Question(Base):
    """题库表"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(SQLEnum(QuestionType), nullable=False, comment="题型")
    content = Column(Text, nullable=False, comment="题目内容（含LaTeX公式）")
    difficulty = Column(Integer, default=3, comment="难度1-5")
    solution = Column(Text, nullable=True, comment="标准答案（主要解法）")
    solutions = Column(JSON, nullable=True, comment="多种解法列表（残局模式）")
    hint_pattern = Column(String(50), nullable=True, comment="规则引擎标识符")
    is_endgame = Column(Integer, default=0, comment="是否为残局模式（0否，1是）")

    # 关系
    tags = relationship(
        "QuestionTag", back_populates="question", cascade="all, delete-orphan"
    )


class QuestionTag(Base):
    """知识点标签表"""

    __tablename__ = "question_tags"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag = Column(String(50), primary_key=True, comment='如"二次函数","相似三角形"')

    # 关系
    question = relationship("Question", back_populates="tags")


class HintRule(Base):
    """规则引擎表"""

    __tablename__ = "hint_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pattern_id = Column(String(50), nullable=False, unique=True, comment="规则标识")
    trigger_keywords = Column(JSON, nullable=True, comment="触发关键词数组")
    hint_text = Column(Text, nullable=False, comment="提示内容")


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    nickname = Column(String(50), nullable=True, comment="昵称")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    answer_records = relationship("AnswerRecord", back_populates="user", cascade="all, delete-orphan")


class AnswerRecord(Base):
    """学生答题记录表"""

    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_input = Column(Text, nullable=True, comment="学生输入步骤")
    used_hint = Column(Text, nullable=True, comment="使用的提示")
    level = Column(String(20), nullable=True, comment="难度级别")
    tag = Column(String(50), nullable=True, comment="知识点标签")
    time_spent = Column(Integer, nullable=True, comment="答题耗时（秒）")
    hint_count = Column(Integer, default=0, comment="提示使用次数")
    is_correct = Column(Integer, default=0, comment="是否正确（0未判断，1正确，2错误）")
    solution_method = Column(String(50), nullable=True, comment="使用的解法（残局模式）")
    weak_points = Column(JSON, nullable=True, comment="薄弱点分析")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    question = relationship("Question", backref="answer_records")
    user = relationship("User", back_populates="answer_records")


class StudentAnalysis(Base):
    """学生分析数据表"""

    __tablename__ = "student_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    abilities = Column(JSON, nullable=True, comment="六维能力评分：{计算能力,逻辑推理,空间想象,问题分析,创新思维,综合应用}")
    tag_scores = Column(JSON, nullable=True, comment="知识点评分")
    weak_points = Column(JSON, nullable=True, comment="薄弱点列表")
    recommended_questions = Column(JSON, nullable=True, comment="推荐题目ID列表")
    summary = Column(Text, nullable=True, comment="分析总结")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", backref="analyses")


class HintFeedback(Base):
    """AI提示反馈表"""

    __tablename__ = "hint_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, comment="题目ID")
    student_input = Column(Text, nullable=True, comment="学生输入步骤")
    hint_content = Column(Text, nullable=False, comment="AI提示内容")
    feedback_type = Column(Integer, nullable=False, comment="反馈类型：1=赞，2=踩")
    hint_source = Column(String(20), nullable=True, comment="提示来源：socratic=本地规则，ai=AI生成")
    hint_keyword = Column(String(50), nullable=True, comment="匹配的关键词（如果是本地规则）")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", backref="hint_feedbacks")
    question = relationship("Question", backref="hint_feedbacks")
