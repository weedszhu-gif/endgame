from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models import User, Problem, LearningSession, SessionStep, Hint
from datetime import datetime


class StorageService:
    """存储服务，封装数据库操作"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # 用户相关操作
    def create_user(self, user_id: str, username: str, email: str) -> User:
        """创建用户"""
        user = User(
            id=user_id,
            username=username,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    # 问题相关操作
    def create_problem(self, problem_id: str, content: str, type: str, difficulty: str) -> Problem:
        """创建问题"""
        problem = Problem(
            id=problem_id,
            content=content,
            type=type,
            difficulty=difficulty
        )
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return problem
    
    def get_problem(self, problem_id: str) -> Optional[Problem]:
        """获取问题"""
        return self.db.query(Problem).filter(Problem.id == problem_id).first()
    
    # 学习会话相关操作
    def create_learning_session(self, session_id: str, user_id: str, problem_id: str, problem_content: str) -> LearningSession:
        """创建学习会话"""
        session = LearningSession(
            id=session_id,
            user_id=user_id,
            problem_id=problem_id,
            problem_content=problem_content
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_learning_session(self, session_id: str) -> Optional[LearningSession]:
        """获取学习会话"""
        return self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
    
    def end_learning_session(self, session_id: str) -> Optional[LearningSession]:
        """结束学习会话"""
        session = self.get_learning_session(session_id)
        if session:
            session.end_time = datetime.utcnow()
            session.total_time = int((session.end_time - session.start_time).total_seconds())
            session.completed = True
            self.db.commit()
            self.db.refresh(session)
        return session
    
    # 会话步骤相关操作
    def create_session_step(self, session_id: str, step_number: int, content: str, time_spent: int, hint_used: bool = False, error_type: Optional[str] = None) -> SessionStep:
        """创建会话步骤"""
        step = SessionStep(
            session_id=session_id,
            step_number=step_number,
            content=content,
            time_spent=time_spent,
            hint_used=hint_used,
            error_type=error_type
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        # 更新会话的提示次数和错误次数
        session = self.get_learning_session(session_id)
        if session:
            if hint_used:
                session.hint_count += 1
            if error_type:
                session.error_count += 1
            self.db.commit()
        
        return step
    
    # 提示相关操作
    def create_hint(self, session_id: str, content: str, type: str, step_id: Optional[int] = None) -> Hint:
        """创建提示"""
        hint = Hint(
            session_id=session_id,
            content=content,
            type=type,
            step_id=step_id
        )
        self.db.add(hint)
        self.db.commit()
        self.db.refresh(hint)
        return hint
    
    # 批量操作
    def get_user_learning_sessions(self, user_id: str) -> List[LearningSession]:
        """获取用户的所有学习会话"""
        return self.db.query(LearningSession).filter(LearningSession.user_id == user_id).all()
    
    def get_session_steps(self, session_id: str) -> List[SessionStep]:
        """获取会话的所有步骤"""
        return self.db.query(SessionStep).filter(SessionStep.session_id == session_id).order_by(SessionStep.step_number).all()
    
    def get_session_hints(self, session_id: str) -> List[Hint]:
        """获取会话的所有提示"""
        return self.db.query(Hint).filter(Hint.session_id == session_id).all()
