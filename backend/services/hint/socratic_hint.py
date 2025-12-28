def generate_socratic_hint(step_content: str, feedback_stats: dict = None) -> tuple:
    """
    基于本地规则生成苏格拉底式提示，考虑历史反馈数据

    参数:
        step_content: 用户的解题步骤内容
        feedback_stats: 历史反馈统计，格式：{keyword: {likes: count, dislikes: count, score: float}}

    返回:
        tuple: (hint_text, matched_keyword) 或 (None, None)
    """
    step_text = step_content.lower()

    # 定义规则列表，包含关键词和对应的提示
    rules = [
        # 第一层：具体提示 - 针对特定操作（更具体的关键词先检查）
        (["配方法", "配方"], "配方过程中是否注意了常数项的处理？"),
        (["因式分解", "分解因式"], "你用了什么因式分解方法？是否有其他分解方式？"),
        (["合并同类项"], "你确定所有同类项都合并了吗？再检查一下系数。"),
        (["系数化为1", "除以"], "为什么要除以这个系数？是否可以乘以它的倒数？"),
        (["辅助线"], "这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？"),
        (["相似", "全等"], "你是如何证明相似/全等的？是否符合相应的判定定理？"),
        (
            ["勾股定理", "毕达哥拉斯"],
            "你确定这个三角形是直角三角形吗？有没有其他方法可以验证？",
        ),
        (["面积", "体积"], "你使用了什么面积/体积公式？是否适用于当前图形？"),
        (["函数", "图像"], "这个函数的定义域和值域是什么？图像有什么特征？"),
        (["不等式", "不等"], "解不等式时是否注意了不等号的方向变化？"),
        # 第二层：验证相关
        (["检验", "验证"], "你是如何验证解的正确性的？是否考虑了所有可能的解？"),
        # 第三层：基础操作
        (
            ["设未知数", "设x为", "假设"],
            "你为什么选择这个变量？是否有更简洁的设定方式？",
        ),
        (["移项"], "移项时是否考虑了符号变化？"),
        (["解方程"], "你用了什么方法解方程？是否有更简便的方法？"),
        (["计算", "算"], "你确定计算过程正确吗？可以再检查一遍吗？"),
    ]

    # 匹配规则，考虑反馈得分
    matched_rules = []
    for keywords, hint_text in rules:
        for keyword in keywords:
            if keyword in step_text:
                # 计算该规则的得分（基于反馈统计）
                score = 0.5  # 默认得分
                if feedback_stats and keyword in feedback_stats:
                    score = feedback_stats[keyword].get("score", 0.5)

                matched_rules.append(
                    {"keyword": keyword, "hint": hint_text, "score": score}
                )
                break  # 每个规则只匹配一次

    if not matched_rules:
        return None, None

    # 如果有多个匹配，选择得分最高的
    best_match = max(matched_rules, key=lambda x: x["score"])
    return best_match["hint"], best_match["keyword"]
