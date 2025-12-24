import pytest
from unittest.mock import MagicMock, patch
import sys

# 创建一个mock的openai模块
mock_openai_module = MagicMock()
mock_client = MagicMock()
mock_openai_module.OpenAI.return_value = mock_client

# 将mock模块添加到sys.modules中，这样当其他模块导入openai时，会得到这个mock版本
sys.modules['openai'] = mock_openai_module

# 现在导入需要测试的函数
from services.hint.socratic_hint import generate_socratic_hint


def test_generate_socratic_hint_basic_cases():
    """测试基本提示生成情况"""
    # 测试设未知数
    assert generate_socratic_hint("设未知数x") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    assert generate_socratic_hint("设x为苹果的数量") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    assert generate_socratic_hint("假设x是速度") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    
    # 测试移项
    assert generate_socratic_hint("移项得到2x = 4") == "移项时是否考虑了符号变化？"
    
    # 测试解方程
    assert generate_socratic_hint("解方程2x + 3 = 7") == "你用了什么方法解方程？是否有更简便的方法？"
    
    # 测试计算
    assert generate_socratic_hint("计算3 + 5 = 8") == "你确定计算过程正确吗？可以再检查一遍吗？"
    assert generate_socratic_hint("算一下这个表达式的值") == "你确定计算过程正确吗？可以再检查一遍吗？"


def test_generate_socratic_hint_advanced_cases():
    """测试进阶提示生成情况"""
    # 测试合并同类项
    assert generate_socratic_hint("合并同类项得到3x + 2y = 10") == "你确定所有同类项都合并了吗？再检查一下系数。"
    
    # 测试系数化为1
    assert generate_socratic_hint("系数化为1得到x = 2") == "为什么要除以这个系数？是否可以乘以它的倒数？"
    assert generate_socratic_hint("除以2得到x = 3") == "为什么要除以这个系数？是否可以乘以它的倒数？"
    
    # 测试因式分解
    assert generate_socratic_hint("因式分解得到(x+2)(x-3)=0") == "你用了什么因式分解方法？是否有其他分解方式？"
    assert generate_socratic_hint("分解因式x² - 4") == "你用了什么因式分解方法？是否有其他分解方式？"
    
    # 测试配方
    assert generate_socratic_hint("配方得到(x+1)² = 4") == "配方过程中是否注意了常数项的处理？"
    assert generate_socratic_hint("用配方法解方程") == "配方过程中是否注意了常数项的处理？"


def test_generate_socratic_hint_depth_cases():
    """测试深度提示生成情况"""
    # 测试检验
    assert generate_socratic_hint("检验x=2是否为方程的解") == "你是如何验证解的正确性的？是否考虑了所有可能的解？"
    assert generate_socratic_hint("验证计算结果") == "你是如何验证解的正确性的？是否考虑了所有可能的解？"
    
    # 测试辅助线
    assert generate_socratic_hint("作辅助线连接AB") == "这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？"
    
    # 测试相似/全等
    assert generate_socratic_hint("证明三角形ABC相似于三角形DEF") == "你是如何证明相似/全等的？是否符合相应的判定定理？"
    assert generate_socratic_hint("三角形全等") == "你是如何证明相似/全等的？是否符合相应的判定定理？"
    
    # 测试勾股定理
    assert generate_socratic_hint("根据勾股定理，a² + b² = c²") == "你确定这个三角形是直角三角形吗？有没有其他方法可以验证？"
    assert generate_socratic_hint("使用毕达哥拉斯定理计算") == "你确定这个三角形是直角三角形吗？有没有其他方法可以验证？"
    
    # 测试面积/体积
    assert generate_socratic_hint("计算长方形的面积") == "你使用了什么面积/体积公式？是否适用于当前图形？"
    assert generate_socratic_hint("计算圆柱的体积") == "你使用了什么面积/体积公式？是否适用于当前图形？"
    
    # 测试函数/图像
    assert generate_socratic_hint("画出函数y = 2x + 1的图像") == "这个函数的定义域和值域是什么？图像有什么特征？"
    
    # 测试不等式
    assert generate_socratic_hint("解不等式2x + 3 > 7") == "解不等式时是否注意了不等号的方向变化？"
    assert generate_socratic_hint("不等关系成立") == "解不等式时是否注意了不等号的方向变化？"


def test_generate_socratic_hint_no_match():
    """测试没有匹配规则的情况"""
    # 没有匹配的规则，应该返回None
    assert generate_socratic_hint("这是一个没有匹配规则的句子") is None
    assert generate_socratic_hint("随机文本") is None
    assert generate_socratic_hint("123456") is None


def test_generate_socratic_hint_case_insensitive():
    """测试不区分大小写的匹配"""
    # 测试不同大小写的情况
    assert generate_socratic_hint("设未知数X") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    assert generate_socratic_hint("移项得到结果") == "移项时是否考虑了符号变化？"
    assert generate_socratic_hint("解方程") == "你用了什么方法解方程？是否有更简便的方法？"
    assert generate_socratic_hint("计算结果") == "你确定计算过程正确吗？可以再检查一遍吗？"


def test_generate_socratic_hint_multiple_keywords():
    """测试多个关键词的情况（应该只匹配第一个）"""
    # 多个关键词，应该匹配第一个出现的规则
    assert generate_socratic_hint("设未知数x，然后移项") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    assert generate_socratic_hint("解方程，然后计算结果") == "你用了什么方法解方程？是否有更简便的方法？"


def test_generate_socratic_hint_middle_school_cases():
    """测试初中各阶段数学题的提示生成"""
    # 初一数学 - 有理数运算
    assert generate_socratic_hint("计算") == "你确定计算过程正确吗？可以再检查一遍吗？"
    assert generate_socratic_hint("算") == "你确定计算过程正确吗？可以再检查一遍吗？"
    
    # 初一数学 - 一元一次方程
    assert generate_socratic_hint("移项") == "移项时是否考虑了符号变化？"
    assert generate_socratic_hint("解方程") == "你用了什么方法解方程？是否有更简便的方法？"
    assert generate_socratic_hint("设未知数") == "你为什么选择这个变量？是否有更简洁的设定方式？"
    
    # 初二数学 - 二元一次方程组
    assert generate_socratic_hint("解方程") == "你用了什么方法解方程？是否有更简便的方法？"
    
    # 初二数学 - 三角形全等
    assert generate_socratic_hint("全等") == "你是如何证明相似/全等的？是否符合相应的判定定理？"
    assert generate_socratic_hint("相似") == "你是如何证明相似/全等的？是否符合相应的判定定理？"
    
    # 初二数学 - 分式方程
    assert generate_socratic_hint("解方程") == "你用了什么方法解方程？是否有更简便的方法？"
    assert generate_socratic_hint("检验") == "你是如何验证解的正确性的？是否考虑了所有可能的解？"
    
    # 初三数学 - 一元二次方程
    assert generate_socratic_hint("用配方法解方程") == "配方过程中是否注意了常数项的处理？"
    assert generate_socratic_hint("因式分解") == "你用了什么因式分解方法？是否有其他分解方式？"
    
    # 初三数学 - 函数
    assert generate_socratic_hint("函数") == "这个函数的定义域和值域是什么？图像有什么特征？"
    assert generate_socratic_hint("图像") == "这个函数的定义域和值域是什么？图像有什么特征？"
    
    # 初三数学 - 几何
    assert generate_socratic_hint("面积") == "你使用了什么面积/体积公式？是否适用于当前图形？"
    assert generate_socratic_hint("体积") == "你使用了什么面积/体积公式？是否适用于当前图形？"
    assert generate_socratic_hint("勾股定理") == "你确定这个三角形是直角三角形吗？有没有其他方法可以验证？"
    
    # 初三数学 - 不等式
    assert generate_socratic_hint("不等式") == "解不等式时是否注意了不等号的方向变化？"
    
    # 通用操作
    assert generate_socratic_hint("计算") == "你确定计算过程正确吗？可以再检查一遍吗？"
    assert generate_socratic_hint("验证") == "你是如何验证解的正确性的？是否考虑了所有可能的解？"



