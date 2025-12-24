from datetime import datetime
from typing import List, Dict, Optional

class LearningTracker:
    """
    学习跟踪器，用于记录用户的学习过程数据
    """
    
    def __init__(self):
        self.learning_sessions: Dict[str, dict] = {}
    
    def start_session(self, user_id: str, problem_id: str, problem_content: str) -> str:
        """
        开始一个新的学习会话
        
        参数:
            user_id: 用户ID
            problem_id: 问题ID
            problem_content: 问题内容
            
        返回:
            str: 会话ID
        """
        session_id = f"{user_id}_{problem_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.learning_sessions[session_id] = {
            "user_id": user_id,
            "problem_id": problem_id,
            "problem_content": problem_content,
            "start_time": datetime.now(),
            "end_time": None,
            "steps": [],
            "hint_count": 0,
            "error_count": 0,
            "total_time": 0
        }
        return session_id
    
    def add_step(self, session_id: str, step_content: str, hint_used: bool = False, error_type: Optional[str] = None) -> dict:
        """
        添加解题步骤
        
        参数:
            session_id: 会话ID
            step_content: 步骤内容
            hint_used: 是否使用了提示
            error_type: 错误类型（如果有）
            
        返回:
            dict: 更新后的会话数据
        """
        if session_id not in self.learning_sessions:
            raise ValueError(f"会话ID不存在: {session_id}")
        
        session = self.learning_sessions[session_id]
        
        # 计算步骤耗时
        current_time = datetime.now()
        if session["steps"]:
            prev_step_time = session["steps"][-1]["timestamp"]
            step_time = (current_time - prev_step_time).total_seconds()
        else:
            step_time = (current_time - session["start_time"]).total_seconds()
        
        # 添加步骤
        step = {
            "content": step_content,
            "timestamp": current_time,
            "time_spent": step_time,
            "hint_used": hint_used,
            "error_type": error_type
        }
        
        session["steps"].append(step)
        
        # 更新统计数据
        if hint_used:
            session["hint_count"] += 1
        
        if error_type:
            session["error_count"] += 1
        
        return session
    
    def end_session(self, session_id: str) -> dict:
        """
        结束学习会话
        
        参数:
            session_id: 会话ID
            
        返回:
            dict: 完整的会话数据
        """
        if session_id not in self.learning_sessions:
            raise ValueError(f"会话ID不存在: {session_id}")
        
        session = self.learning_sessions[session_id]
        session["end_time"] = datetime.now()
        session["total_time"] = (session["end_time"] - session["start_time"]).total_seconds()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        获取会话数据
        
        参数:
            session_id: 会话ID
            
        返回:
            dict: 会话数据，如果不存在则返回None
        """
        return self.learning_sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[dict]:
        """
        获取用户的所有会话
        
        参数:
            user_id: 用户ID
            
        返回:
            List[dict]: 用户的所有会话数据
        """
        return [session for session in self.learning_sessions.values() if session["user_id"] == user_id]
    
    def generate_report(self, session_id: str) -> dict:
        """
        生成学习报告
        
        参数:
            session_id: 会话ID
            
        返回:
            dict: 学习报告
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话ID不存在: {session_id}")
        
        # 分析错误类型
        error_types = {}
        for step in session["steps"]:
            if step["error_type"]:
                error_types[step["error_type"]] = error_types.get(step["error_type"], 0) + 1
        
        # 计算平均步骤时间
        if session["steps"]:
            avg_step_time = sum(step["time_spent"] for step in session["steps"]) / len(session["steps"])
        else:
            avg_step_time = 0
        
        # 生成报告
        report = {
            "user_id": session["user_id"],
            "problem_id": session["problem_id"],
            "problem_content": session["problem_content"],
            "start_time": session["start_time"].isoformat(),
            "end_time": session["end_time"].isoformat() if session["end_time"] else None,
            "total_time": session["total_time"],
            "step_count": len(session["steps"]),
            "hint_count": session["hint_count"],
            "error_count": session["error_count"],
            "avg_step_time": avg_step_time,
            "error_types": error_types,
            "steps": session["steps"]
        }
        
        return report

# 创建全局学习跟踪器实例
learning_tracker = LearningTracker()
