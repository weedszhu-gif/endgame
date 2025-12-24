from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    learning_sessions = relationship("LearningSession", back_populates="user")


class Problem(Base):
    """数学问题模型"""
    __tablename__ = "problems"
    
    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(String, index=True)  # 问题类型：algebra, geometry, etc.
    difficulty = Column(String, index=True)  # 难度：easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    learning_sessions = relationship("LearningSession", back_populates="problem")


class LearningSession(Base):
    """学习会话模型"""
    __tablename__ = "learning_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    problem_content = Column(Text, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    total_time = Column(Integer, nullable=True)  # 总时间（秒）
    hint_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="learning_sessions")
    problem = relationship("Problem", back_populates="learning_sessions")
    steps = relationship("SessionStep", back_populates="session", cascade="all, delete-orphan")
    hints = relationship("Hint", back_populates="session", cascade="all, delete-orphan")


class SessionStep(Base):
    """会话步骤模型"""
    __tablename__ = "session_steps"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("learning_sessions.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    time_spent = Column(Integer, nullable=False)  # 步骤耗时（秒）
    hint_used = Column(Boolean, default=False)
    error_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("LearningSession", back_populates="steps")
    hint = relationship("Hint", back_populates="step", uselist=False)


class Hint(Base):
    """提示模型"""
    __tablename__ = "hints"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("learning_sessions.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("session_steps.id"), nullable=True)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 提示类型：local, ai
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("LearningSession", back_populates="hints")
    step = relationship("SessionStep", back_populates="hint")
