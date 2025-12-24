import os
import logging
from config import settings
from .model_client import ModelClient, ModelType

# 配置日志
logger = logging.getLogger(__name__)


async def get_ai_hint(step_content: str, max_retries: int = 3) -> str:
    """
    调用AI服务获取苏格拉底式提示，支持重试机制
    
    参数:
        step_content: 用户的解题步骤内容
        max_retries: 最大重试次数
        
    返回:
        str: AI生成的提示问题
    """
    import time
    
    # 构建系统提示
    system_prompt = """
    你是一位初中数学老师，使用苏格拉底式提问引导学生思考。
    针对学生的解题步骤，提出一个引导性问题，不要直接给出答案。
    问题应该帮助学生发现可能的错误或优化解题方法。
    保持问题简洁明了，符合初中学生的理解水平。
    """
    
    # 构建用户提示
    user_prompt = f"学生的解题步骤：{step_content}\n请提出一个引导性问题。"
    
    for attempt in range(max_retries):
        try:
            # 根据环境变量选择模型类型
            model_type = ModelType(settings.ai_model_type.lower())
            
            # 创建模型客户端
            client = ModelClient(
                model_type,
                api_key=os.getenv(f"{model_type.value.upper()}_API_KEY"),
                secret_key=os.getenv(f"{model_type.value.upper()}_SECRET_KEY"),
                access_token=os.getenv(f"{model_type.value.upper()}_ACCESS_TOKEN")
            )
            
            # 调用模型生成提示
            hint = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )
            
            return hint
        
        except Exception as e:
            logger.error(f"AI服务错误 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                retry_delay = 2 ** attempt
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"获取AI提示失败: {str(e)}")


async def analyze_solution(solution_steps: list, max_retries: int = 3) -> dict:
    """
    分析完整的解题过程，提供综合评价和建议，支持重试机制
    
    参数:
        solution_steps: 解题步骤列表
        max_retries: 最大重试次数
        
    返回:
        dict: 包含评价和建议的分析结果
    """
    import time
    
    # 构建系统提示
    system_prompt = """
    你是一位初中数学老师，负责分析学生的解题过程。
    请对学生的解题步骤进行以下分析：
    1. 解题思路是否正确
    2. 是否有错误或可以改进的地方
    3. 提供针对性的建议
    4. 评价解题过程的优缺点
    
    保持评价客观、友好，使用学生容易理解的语言。
    """
    
    # 构建用户提示
    solution_text = "\n".join([f"步骤 {i+1}: {step}" for i, step in enumerate(solution_steps)])
    user_prompt = f"学生的解题过程：\n{solution_text}\n请进行分析和评价。"
    
    for attempt in range(max_retries):
        try:
            # 根据环境变量选择模型类型
            model_type = ModelType(settings.ai_model_type.lower())
            
            # 创建模型客户端
            client = ModelClient(
                model_type,
                api_key=os.getenv(f"{model_type.value.upper()}_API_KEY"),
                secret_key=os.getenv(f"{model_type.value.upper()}_SECRET_KEY"),
                access_token=os.getenv(f"{model_type.value.upper()}_ACCESS_TOKEN")
            )
            
            # 调用模型生成分析结果
            analysis = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=settings.ai_temperature,
                max_tokens=200
            )
            
            return {
                "analysis": analysis,
                "solution_steps": solution_steps
            }
        
        except Exception as e:
            logger.error(f"AI分析服务错误 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                retry_delay = 2 ** attempt
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"分析解题过程失败: {str(e)}")
