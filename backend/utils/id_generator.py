import uuid
from datetime import datetime


def generate_uuid() -> str:
    """
    生成唯一UUID
    
    Returns:
        str: 唯一UUID字符串
    """
    return str(uuid.uuid4())


def generate_session_id(user_id: str, problem_id: str) -> str:
    """
    生成会话ID，格式：user_id_problem_id_timestamp
    
    Args:
        user_id: 用户ID
        problem_id: 问题ID
    
    Returns:
        str: 会话ID字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{user_id}_{problem_id}_{timestamp}"
