import os
import logging
from config import settings
from .model_client import ModelClient, ModelType

# 配置日志
logger = logging.getLogger(__name__)


async def get_ai_hint(
    step_content: str, conversation_history: list = None, max_retries: int = 3
) -> str:
    """
    调用AI服务获取苏格拉底式提示，支持重试机制和对话历史

    参数:
        step_content: 用户的解题步骤内容
        conversation_history: 对话历史列表，格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        max_retries: 最大重试次数

    返回:
        str: AI生成的提示问题
    """
    import time
    import random

    # 构建系统提示
    system_prompt = """
    你是一位初中数学老师，使用苏格拉底式提问引导学生思考。
    针对学生的解题步骤，提出一个引导性问题，不要直接给出答案。
    问题应该帮助学生发现可能的错误或优化解题方法。
    保持问题简洁明了，符合初中学生的理解水平。
    注意：每次回答应该有所不同，从不同角度引导学生思考。
    """

    # 构建用户提示
    user_prompt = f"学生的解题步骤：{step_content}\n请提出一个引导性问题。"

    # 构建消息列表，包含对话历史
    messages = []

    # 首先添加系统提示（如果有）
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # 如果有对话历史，添加到消息列表
    if conversation_history:
        # 转换对话历史格式（确保格式正确）
        for msg in conversation_history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                # 确保 role 符合模型要求（user/assistant/system）
                role = msg["role"]
                if role == "ai":
                    role = "assistant"
                # 跳过已有的 system 消息，避免重复
                if role != "system":
                    messages.append({"role": role, "content": msg["content"]})

    # 添加当前用户消息
    messages.append({"role": "user", "content": user_prompt})
    logger.info(f"messages: {messages}")
    for attempt in range(max_retries):
        try:
            # 根据环境变量选择模型类型
            model_type = ModelType(settings.ai_model_type.lower())

            # 创建模型客户端
            client = ModelClient(
                model_type,
                api_key=os.getenv(f"{model_type.value.upper()}_API_KEY"),
                secret_key=os.getenv(f"{model_type.value.upper()}_SECRET_KEY"),
                access_token=os.getenv(f"{model_type.value.upper()}_ACCESS_TOKEN"),
            )

            # 动态调整 temperature，增加随机性，确保每次返回不同
            # 基础 temperature + 随机波动（0.1-0.3），但不超过 1.0
            base_temp = settings.ai_temperature
            random_variation = random.uniform(0.1, 0.3)
            dynamic_temperature = min(base_temp + random_variation, 1.0)

            # 调用模型生成提示，传入对话历史
            # 如果 messages 包含系统提示和历史记录，直接传递 messages
            # 否则使用 prompt 和 system_prompt
            if len(messages) > 1:  # 有系统提示或历史记录
                hint = client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=dynamic_temperature,
                    max_tokens=settings.ai_max_tokens,
                    messages=messages,
                )
            else:
                # 没有历史记录，使用简单方式
                hint = client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=dynamic_temperature,
                    max_tokens=settings.ai_max_tokens,
                )

            return hint
        except Exception as e:
            logger.error(f"AI服务错误 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                retry_delay = 2**attempt
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"获取AI提示失败: {str(e)}")

    # 如果所有重试都失败，返回默认提示
    return "请继续思考，尝试从不同角度分析问题。"


async def evaluate_answer(
    question_content: str,
    question_solution: str,
    student_answer: str,
    max_retries: int = 3,
) -> dict:
    """
    使用AI评估学生答案是否正确

    参数:
        question_content: 题目内容
        question_solution: 标准答案/解法
        student_answer: 学生答案
        max_retries: 最大重试次数

    返回:
        dict: 包含 is_correct (1=正确, 2=错误) 和 feedback (反馈信息)
    """
    import time
    import random

    # 构建系统提示
    system_prompt = """
    你是一位专业的数学老师，负责评估学生的答案是否正确。
    
    评估标准：
    1. 如果学生的答案在数学上正确（即使表达方式不同），应判定为正确
    2. 如果学生的答案有明显错误或逻辑错误，应判定为错误
    3. 如果学生的答案不完整但部分正确，应判定为错误
    4. 对于选择题，答案必须完全匹配
    5. 对于计算题，允许不同的解题方法，只要最终答案正确即可
    6. 对于证明题，需要逻辑完整且正确
    
    请以JSON格式返回结果：
    {
        "is_correct": 1 或 2,  // 1表示正确，2表示错误
        "feedback": "简短的反馈说明"
    }
    """

    # 构建用户提示
    user_prompt = f"""请评估以下学生答案是否正确：

题目：{question_content}

标准答案/解法：{question_solution}

学生答案：{student_answer}

请以JSON格式返回评估结果，格式如下：
{{
    "is_correct": 1 或 2,
    "feedback": "反馈说明"
}}"""

    try:
        from .model_client import ModelClient, ModelType

        # 创建模型客户端（使用与get_ai_hint相同的逻辑）
        model_type = ModelType(settings.ai_model_type.lower())

        client = ModelClient(model_type)

        # 调用AI模型
        response = client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # 降低温度以获得更一致的判断
            max_tokens=500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # 解析JSON响应
        import json
        import re

        # 尝试提取JSON
        json_match = re.search(r'\{[^{}]*"is_correct"[^{}]*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # 如果没有找到JSON，尝试解析整个响应
            result = json.loads(response)

        # 验证结果
        is_correct = result.get("is_correct", 0)
        if is_correct not in [1, 2]:
            # 如果AI返回的值不在预期范围内，尝试从feedback推断
            feedback = result.get("feedback", "").lower()
            if any(
                word in feedback for word in ["正确", "对", "yes", "correct", "right"]
            ):
                is_correct = 1
            elif any(
                word in feedback for word in ["错误", "错", "no", "incorrect", "wrong"]
            ):
                is_correct = 2
            else:
                is_correct = 2  # 默认判定为错误

        return {"is_correct": is_correct, "feedback": result.get("feedback", "已评估")}

    except json.JSONDecodeError as e:
        logger.warning(f"AI返回的JSON格式错误: {e}, 响应内容: {response}")
        # 尝试从文本中推断
        response_lower = response.lower()
        if any(
            word in response_lower for word in ["正确", "对", "yes", "correct", "right"]
        ):
            return {"is_correct": 1, "feedback": "答案正确"}
        else:
            return {"is_correct": 2, "feedback": "答案错误"}
    except Exception as e:
        logger.error(f"AI评估答案失败: {str(e)}", exc_info=True)
        # 发生错误时，返回未判断状态
        return {"is_correct": 0, "feedback": f"评估失败: {str(e)}"}


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
    solution_text = "\n".join(
        [f"步骤 {i+1}: {step}" for i, step in enumerate(solution_steps)]
    )
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
                access_token=os.getenv(f"{model_type.value.upper()}_ACCESS_TOKEN"),
            )

            # 调用模型生成分析结果
            analysis = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=settings.ai_temperature,
                max_tokens=200,
            )

            return {"analysis": analysis, "solution_steps": solution_steps}

        except Exception as e:
            logger.error(f"AI分析服务错误 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                retry_delay = 2**attempt
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"分析解题过程失败: {str(e)}")
