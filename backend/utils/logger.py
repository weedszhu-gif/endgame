import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str = None, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 记录器名称，None表示根记录器
        log_file: 日志文件路径，None表示不输出到文件
        level: 日志级别
    
    Returns:
        logging.Logger: 日志记录器
    """
    # 获取记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 文件处理器（如果指定了日志文件）
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 旋转文件处理器，最大10MB，保留5个备份
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(level)
        
        # 格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 添加格式化器到处理器
        console_handler.setFormatter(formatter)
        if log_file:
            file_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        logger.addHandler(console_handler)
        if log_file:
            logger.addHandler(file_handler)
    
    return logger
