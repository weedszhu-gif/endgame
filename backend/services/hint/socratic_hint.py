def generate_socratic_hint(step_content: str) -> str:
    """
    基于本地规则生成苏格拉底式提示
    
    参数:
        step_content: 用户的解题步骤内容
        
    返回:
        str: 生成的提示问题，如果没有匹配的规则则返回None
    """
    step_text = step_content.lower()
    
    # 第一层：具体提示 - 针对特定操作（更具体的关键词先检查）
    if '配方法' in step_text or '配方' in step_text:
        return '配方过程中是否注意了常数项的处理？'
    
    if '因式分解' in step_text or '分解因式' in step_text:
        return '你用了什么因式分解方法？是否有其他分解方式？'
    
    if '合并同类项' in step_text:
        return '你确定所有同类项都合并了吗？再检查一下系数。'
    
    if '系数化为1' in step_text or '除以' in step_text:
        return '为什么要除以这个系数？是否可以乘以它的倒数？'
    
    if '辅助线' in step_text or ('作' in step_text and '线' in step_text):
        return '这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？'
    
    if '相似' in step_text or '全等' in step_text:
        return '你是如何证明相似/全等的？是否符合相应的判定定理？'
    
    if '勾股定理' in step_text or '毕达哥拉斯' in step_text:
        return '你确定这个三角形是直角三角形吗？有没有其他方法可以验证？'
    
    if '面积' in step_text or '体积' in step_text:
        return '你使用了什么面积/体积公式？是否适用于当前图形？'
    
    if '函数' in step_text or '图像' in step_text:
        return '这个函数的定义域和值域是什么？图像有什么特征？'
    
    if '不等式' in step_text or '不等' in step_text:
        return '解不等式时是否注意了不等号的方向变化？'
    
    # 第二层：验证相关 - 针对验证操作
    if '检验' in step_text or '验证' in step_text:
        return '你是如何验证解的正确性的？是否考虑了所有可能的解？'
    
    # 第三层：基础操作 - 针对常见操作
    if '设未知数' in step_text or '设x为' in step_text or '假设' in step_text:
        return '你为什么选择这个变量？是否有更简洁的设定方式？'
    
    if '移项' in step_text:
        return '移项时是否考虑了符号变化？'
    
    if '解方程' in step_text:
        return '你用了什么方法解方程？是否有更简便的方法？'
    
    if '计算' in step_text or '算' in step_text:
        return '你确定计算过程正确吗？可以再检查一遍吗？'
    
    # 如果没有匹配的规则，返回None
    return None
