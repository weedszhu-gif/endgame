import pytest
from unittest.mock import patch, AsyncMock
from services.ai.ai_service import get_ai_hint, analyze_solution


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate', return_value="这是一个测试提示")
async def test_get_ai_hint_success(mock_generate):
    """测试AI服务调用成功的情况"""
    # 调用函数
    result = await get_ai_hint("测试步骤")
    
    # 验证结果
    assert result == "这是一个测试提示"
    # 验证API调用
    mock_generate.assert_called_once()


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate', side_effect=Exception("API调用失败"))
async def test_get_ai_hint_failure(mock_generate):
    """测试AI服务调用失败的情况"""
    # 调用函数并验证异常
    with pytest.raises(Exception) as excinfo:
        await get_ai_hint("测试步骤")
    
    assert "获取AI提示失败" in str(excinfo.value)


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate')
async def test_get_ai_hint_retry(mock_generate):
    """测试AI服务重试机制"""
    # 设置模拟响应，前两次失败，第三次成功
    mock_generate.side_effect = [
        Exception("第一次失败"),
        Exception("第二次失败"),
        "这是一个测试提示"
    ]
    
    # 调用函数
    result = await get_ai_hint("测试步骤", max_retries=3)
    
    # 验证结果
    assert result == "这是一个测试提示"
    # 验证API调用了3次
    assert mock_generate.call_count == 3


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate', return_value="这是一个测试分析")
async def test_analyze_solution_success(mock_generate):
    """测试分析解题过程成功的情况"""
    # 调用函数
    result = await analyze_solution(["步骤1", "步骤2", "步骤3"])
    
    # 验证结果
    assert result["analysis"] == "这是一个测试分析"
    assert result["solution_steps"] == ["步骤1", "步骤2", "步骤3"]
    # 验证API调用
    mock_generate.assert_called_once()


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate', side_effect=Exception("API调用失败"))
async def test_analyze_solution_failure(mock_generate):
    """测试分析解题过程失败的情况"""
    # 调用函数并验证异常
    with pytest.raises(Exception) as excinfo:
        await analyze_solution(["步骤1", "步骤2", "步骤3"])
    
    assert "分析解题过程失败" in str(excinfo.value)


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate')
async def test_analyze_solution_retry(mock_generate):
    """测试分析解题过程重试机制"""
    # 设置模拟响应，前两次失败，第三次成功
    mock_generate.side_effect = [
        Exception("第一次失败"),
        Exception("第二次失败"),
        "这是一个测试分析"
    ]
    
    # 调用函数
    result = await analyze_solution(["步骤1", "步骤2", "步骤3"], max_retries=3)
    
    # 验证结果
    assert result["analysis"] == "这是一个测试分析"
    # 验证API调用了3次
    assert mock_generate.call_count == 3


@pytest.mark.asyncio
@patch('services.ai.model_client.client.ModelClient.generate', return_value="这是一个针对初中数学题的AI提示")
async def test_middle_school_math_cases(mock_generate):
    """测试AI服务对初中各阶段数学题的处理能力"""
    # 初一数学 - 有理数运算
    hint = await get_ai_hint("计算：(-3) × 4 + (-2)² - 15 ÷ 3")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初一数学 - 一元一次方程
    hint = await get_ai_hint("解方程：3(x - 2) + 1 = x - (2x - 1)")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初一数学 - 几何初步
    hint = await get_ai_hint("已知∠AOB = 90°，OC是∠AOB的平分线，OD是∠BOC的平分线，求∠AOD的度数")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初二数学 - 二元一次方程组
    hint = await get_ai_hint("解方程组：2x + y = 8，x - y = 1")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初二数学 - 三角形全等
    hint = await get_ai_hint("已知AB=CD，BC=DA，求证：∠B=∠D")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初二数学 - 分式方程
    hint = await get_ai_hint("解方程：1/(x-2) + 3 = (x-1)/(x-2)")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 一元二次方程
    hint = await get_ai_hint("用配方法解方程：x² + 6x - 7 = 0")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 一次函数
    hint = await get_ai_hint("已知一次函数的图像经过点A(1, 3)和B(-1, -1)，求解析式")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 二次函数
    hint = await get_ai_hint("已知二次函数y = ax² + bx + c的图像经过点(0, 3)，(1, 4)，(2, 3)，求解析式")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 圆的性质
    hint = await get_ai_hint("已知AB是⊙O的直径，C是⊙O上一点，OD⊥AC于D，若OD=3，求BC的长")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 相似三角形
    hint = await get_ai_hint("在△ABC中，DE∥BC，AD=2，DB=3，DE=4，求BC的长")
    assert isinstance(hint, str)
    assert len(hint) > 0
    
    # 初三数学 - 三角函数
    hint = await get_ai_hint("在Rt△ABC中，∠C=90°，sinA=3/5，BC=6，求AB和AC的长")
    assert isinstance(hint, str)
    assert len(hint) > 0
