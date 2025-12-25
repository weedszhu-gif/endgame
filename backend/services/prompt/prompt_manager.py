import os
from typing import Dict, Optional


class PromptManager:
    """提示词管理器，用于管理系统提示词"""
    
    def __init__(self):
        """初始化提示词管理器"""
        self.prompts: Dict[str, str] = {
            "socratic_hint": self._load_prompt(
                "socratic_hint",
                """
                你是一位初中数学老师，使用苏格拉底式提问引导学生思考。
                针对学生的解题步骤，提出一个引导性问题，不要直接给出答案。
                问题应该帮助学生发现可能的错误或优化解题方法。
                保持问题简洁明了，符合初中学生的理解水平。
                """
            ),
            "solution_analysis": self._load_prompt(
                "solution_analysis",
                """
                你是一位初中数学老师，负责分析学生的解题过程。
                请对学生的解题步骤进行以下分析：
                1. 解题思路是否正确
                2. 是否有错误或可以改进的地方
                3. 提供针对性的建议
                4. 评价解题过程的优缺点
                
                保持评价客观、友好，使用学生容易理解的语言。
                """
            ),
            "math_explanation": self._load_prompt(
                "math_explanation",
                """
                你是一位初中数学老师，使用简单易懂的语言解释数学概念。
                针对学生的问题，提供清晰、详细的解释，避免使用复杂术语。
                可以使用例子帮助学生理解。
                """
            )
        }
    
    def _load_prompt(self, name: str, default: str) -> str:
        """
        从文件或环境变量加载提示词
        
        Args:
            name: 提示词名称
            default: 默认提示词
            
        Returns:
            str: 加载的提示词
        """
        # 优先从环境变量加载
        env_var = f"PROMPT_{name.upper()}"
        if env_var in os.environ:
            return os.environ[env_var]
        
        # 其次从文件加载
        file_path = f"services/prompt/templates/{name}.txt"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        
        # 返回默认值
        return default
    
    def get_prompt(self, name: str) -> Optional[str]:
        """
        获取指定名称的提示词
        
        Args:
            name: 提示词名称
            
        Returns:
            str: 提示词，如果不存在则返回None
        """
        return self.prompts.get(name)
    
    def set_prompt(self, name: str, content: str) -> None:
        """
        设置指定名称的提示词
        
        Args:
            name: 提示词名称
            content: 提示词内容
        """
        self.prompts[name] = content
    
    def save_prompt(self, name: str, content: str) -> None:
        """
        保存提示词到文件
        
        Args:
            name: 提示词名称
            content: 提示词内容
        """
        file_path = f"services/prompt/templates/{name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 更新内存中的提示词
        self.prompts[name] = content
    
    def list_prompts(self) -> list:
        """
        列出所有提示词名称
        
        Returns:
            list: 提示词名称列表
        """
        return list(self.prompts.keys())
