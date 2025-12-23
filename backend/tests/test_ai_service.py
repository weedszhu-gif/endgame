import pytest
from unittest.mock import patch, AsyncMock
from services.ai_service import get_ai_hint, analyze_solution


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_get_ai_hint_success(mock_create):
    """测试AI服务调用成功的情况"""
    # 设置模拟响应
    mock_create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="这是一个测试提示"))
    ]
    
    # 调用函数
    result = await get_ai_hint("测试步骤")
    
    # 验证结果
    assert result == "这是一个测试提示"
    # 验证API调用
    mock_create.assert_called_once()


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_get_ai_hint_failure(mock_create):
    """测试AI服务调用失败的情况"""
    # 设置模拟异常
    mock_create.side_effect = Exception("API调用失败")
    
    # 调用函数并验证异常
    with pytest.raises(Exception) as excinfo:
        await get_ai_hint("测试步骤")
    
    assert "获取AI提示失败" in str(excinfo.value)


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_get_ai_hint_retry(mock_create):
    """测试AI服务重试机制"""
    # 设置模拟响应，前两次失败，第三次成功
    mock_create.side_effect = [
        Exception("第一次失败"),
        Exception("第二次失败"),
        AsyncMock(choices=[
            AsyncMock(message=AsyncMock(content="这是一个测试提示"))
        ])
    ]
    
    # 调用函数
    result = await get_ai_hint("测试步骤", max_retries=3)
    
    # 验证结果
    assert result == "这是一个测试提示"
    # 验证API调用了3次
    assert mock_create.call_count == 3


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_analyze_solution_success(mock_create):
    """测试分析解题过程成功的情况"""
    # 设置模拟响应
    mock_create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="这是一个测试分析"))
    ]
    
    # 调用函数
    result = await analyze_solution(["步骤1", "步骤2", "步骤3"])
    
    # 验证结果
    assert result["analysis"] == "这是一个测试分析"
    assert result["solution_steps"] == ["步骤1", "步骤2", "步骤3"]
    # 验证API调用
    mock_create.assert_called_once()


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_analyze_solution_failure(mock_create):
    """测试分析解题过程失败的情况"""
    # 设置模拟异常
    mock_create.side_effect = Exception("API调用失败")
    
    # 调用函数并验证异常
    with pytest.raises(Exception) as excinfo:
        await analyze_solution(["步骤1", "步骤2", "步骤3"])
    
    assert "分析解题过程失败" in str(excinfo.value)


@pytest.mark.asyncio
@patch('services.ai_service.client.chat.completions.create', new_callable=AsyncMock)
async def test_analyze_solution_retry(mock_create):
    """测试分析解题过程重试机制"""
    # 设置模拟响应，前两次失败，第三次成功
    mock_create.side_effect = [
        Exception("第一次失败"),
        Exception("第二次失败"),
        AsyncMock(choices=[
            AsyncMock(message=AsyncMock(content="这是一个测试分析"))
        ])
    ]
    
    # 调用函数
    result = await analyze_solution(["步骤1", "步骤2", "步骤3"], max_retries=3)
    
    # 验证结果
    assert result["analysis"] == "这是一个测试分析"
    # 验证API调用了3次
    assert mock_create.call_count == 3
