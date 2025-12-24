from datetime import datetime, timedelta
from typing import Optional


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象，None表示当前时间
        format_str: 格式化字符串
    
    Returns:
        str: 格式化后的日期时间字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def get_timestamp() -> int:
    """
    获取当前时间戳（秒）
    
    Returns:
        int: 当前时间戳
    """
    return int(datetime.now().timestamp())


def calculate_time_diff(start_time: datetime, end_time: Optional[datetime] = None, unit: str = "seconds") -> float:
    """
    计算时间差
    
    Args:
        start_time: 开始时间
        end_time: 结束时间，None表示当前时间
        unit: 时间单位，可选值：seconds, minutes, hours, days
    
    Returns:
        float: 时间差
    """
    if end_time is None:
        end_time = datetime.now()
    
    diff = end_time - start_time
    
    if unit == "seconds":
        return diff.total_seconds()
    elif unit == "minutes":
        return diff.total_seconds() / 60
    elif unit == "hours":
        return diff.total_seconds() / 3600
    elif unit == "days":
        return diff.total_seconds() / 86400
    else:
        raise ValueError(f"不支持的时间单位: {unit}")
