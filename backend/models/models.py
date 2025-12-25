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
    solution = Column(Text, nullable=True, comment="标准答案")
    hint_pattern = Column(String(50), nullable=True, comment="规则引擎标识符")

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


class AnswerRecord(Base):
    """学生答题记录表"""

    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_input = Column(Text, nullable=True, comment="学生输入步骤")
    used_hint = Column(Text, nullable=True, comment="使用的提示")
    level = Column(String(20), nullable=True, comment="难度级别")
    tag = Column(String(50), nullable=True, comment="知识点标签")
    time_spent = Column(Integer, nullable=True, comment="答题耗时（秒）")
    hint_count = Column(Integer, default=0, comment="提示使用次数")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    question = relationship("Question", backref="answer_records")


class StudentAnalysis(Base):
    """学生分析数据表"""

    __tablename__ = "student_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), nullable=True, comment="学生ID（可选）")
    abilities = Column(JSON, nullable=True, comment="六维能力评分")
    tag_scores = Column(JSON, nullable=True, comment="知识点评分")
    summary = Column(Text, nullable=True, comment="分析总结")
    created_at = Column(DateTime, default=datetime.utcnow)
