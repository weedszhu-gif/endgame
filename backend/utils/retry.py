import time
import logging
from functools import wraps
from typing import Callable, Any, TypeVar, Tuple

T = TypeVar('T')


logger = logging.getLogger(__name__)


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 30.0) -> float:
    """
    计算指数退避延迟时间
    
    Args:
        attempt: 当前重试次数（从0开始）
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
    
    Returns:
        float: 延迟时间（秒）
    """
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_func: Callable[[int, float, float], float] = exponential_backoff
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    重试装饰器，用于自动重试失败的函数调用
    
    Args:
        exceptions: 要捕获的异常类型元组
        max_attempts: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        backoff_func: 退避函数，用于计算每次重试的延迟时间
    
    Returns:
        Callable[[Callable[..., T]], Callable[..., T]]: 装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_attempts - 1:
                        delay = backoff_func(attempt, base_delay, max_delay)
                        logger.warning(
                            f"函数 {func.__name__} 调用失败 (尝试 {attempt+1}/{max_attempts}): {str(e)}. "
                            f"等待 {delay:.2f} 秒后重试..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 调用失败 (尝试 {max_attempts}/{max_attempts}): {str(e)}"
                        )
                        raise
        return wrapper
    return decorator
