"""
初始化数据库，插入 sql.log 中的数据
"""
import json
from models.base import Base, engine, SessionLocal
from models.models import (
    Question,
    QuestionTag,
    HintRule,
    QuestionType,
    AnswerRecord,
    StudentAnalysis,
)

def init_database():
    """创建数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

def insert_questions():
    """插入题目数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing = db.query(Question).first()
        if existing:
            print("数据库中已有题目数据，跳过插入。")
            return
        
        print("正在插入题目数据...")
        
        # 题目数据（从 sql.log 提取，按照 sql.log 中的顺序）
        questions_data = [
            # 题目1：中考真题 - 二次函数顶点坐标
            {
                'type': QuestionType.CHOICE,
                'content': '已知二次函数 $y=x^2+2x-3$，其顶点坐标为（    ）\nA. (1, -4)  B. (-1, -4)  C. (1, 4)  D. (-1, 4)',
                'difficulty': 3,
                'solution': 'B（顶点公式 $x=-\\frac{b}{2a}$ 计算）',
                'hint_pattern': 'vertex_formula',
                'tags': ['二次函数', '对称轴']
            },
            # 题目2：中考真题 - 解方程
            {
                'type': QuestionType.CALCULATION,
                'content': '解方程：$2(x-3)^2 = 18$',
                'difficulty': 4,
                'solution': '$x=6$ 或 $x=0$（两边开方后移项）',
                'hint_pattern': 'square_root',
                'tags': ['一元一次方程']
            },
            # 题目3：中考真题 - 直角三角形
            {
                'type': QuestionType.PROOF,
                'content': '如图，$\\triangle ABC$中$\\angle C=90^\\circ$，$D$为$AB$中点。求证：$CD = \\frac{1}{2}AB$',
                'difficulty': 5,
                'solution': '连接$CD$，用直角三角形斜边中线定理',
                'hint_pattern': 'right_triangle_theorem',
                'tags': ['等腰三角形', '三线合一']
            },
            # 题目4：初级 - 二次函数对称轴
            {
                'type': QuestionType.CHOICE,
                'content': '二次函数 $y=x^2-4x+3$ 的对称轴是（   ）\nA. $x=1$  B. $x=2$  C. $x=3$  D. $x=4$',
                'difficulty': 1,
                'solution': 'B（对称轴公式 $x=-\\frac{b}{2a}$）',
                'hint_pattern': 'vertex_formula',
                'tags': ['二次函数', '顶点坐标']
            },
            # 题目5：初级 - 解方程
            {
                'type': QuestionType.CALCULATION,
                'content': '解方程：$2(x-3) = 10$',
                'difficulty': 2,
                'solution': '$x=8$（两边除以2后加3）',
                'hint_pattern': 'linear_equation',
                'tags': ['实数运算', '绝对值']
            },
            # 题目6：初级 - 等腰三角形
            {
                'type': QuestionType.PROOF,
                'content': '如图，$\\triangle ABC$中 $AB=AC$，$D$为$BC$中点。求证：$AD \\perp BC$',
                'difficulty': 2,
                'solution': '等腰三角形三线合一性质',
                'hint_pattern': 'isosceles_property',
                'tags': ['平行四边形', '中位线']
            },
            # 题目7：中级 - 抛物线顶点坐标
            {
                'type': QuestionType.CHOICE,
                'content': '抛物线 $y=2x^2+4x-1$ 的顶点坐标为（   ）\nA. (-1,-3)  B. (-1,3)  C. (1,-3)  D. (1,3)',
                'difficulty': 3,
                'solution': 'A（$x=-\\frac{b}{2a}=-1$，代入得$y=-3$）',
                'hint_pattern': 'quadratic_vertex',
                'tags': ['二次函数', '图象性质']
            },
            # 题目8：中级 - 实数运算
            {
                'type': QuestionType.CALCULATION,
                'content': '计算：$\\sqrt{25} + \\left| -3 \\right| \\times 2^2 - \\frac{12}{4}$',
                'difficulty': 3,
                'solution': '$5 + 3\\times4 - 3 = 14$',
                'hint_pattern': 'arithmetic_ops',
                'tags': ['一元二次方程', '韦达定理']
            },
            # 题目9：中级 - 平行四边形
            {
                'type': QuestionType.PROOF,
                'content': '如图，$\\square ABCD$中$E,F$分别为$AB,CD$中点。求证：$EF$平分对角线$AC$',
                'difficulty': 3,
                'solution': '连接AE,CF，利用平行四边形性质',
                'hint_pattern': 'parallelogram_prop',
                'tags': ['圆', '射影定理']
            },
            # 题目10：高级 - 二次函数图象分析
            {
                'type': QuestionType.CHOICE,
                'content': '二次函数 $y=ax^2+bx+c$ 图象如图所示（开口向下，顶点在第二象限），则（   ）\nA. $a>0,b>0,c>0$  B. $a<0,b<0,c<0$  C. $a<0,b>0,c>0$  D. $a<0,b<0,c>0$',
                'difficulty': 4,
                'solution': 'D（开口向下$a<0$，对称轴$>0$得$b<0$，y轴截距$>0$得$c>0$）',
                'hint_pattern': 'quadratic_analysis',
                'tags': ['二次函数', '图象性质']
            },
            # 题目11：高级 - 韦达定理
            {
                'type': QuestionType.CALCULATION,
                'content': '若 $\\alpha,\\beta$ 是方程 $x^2-5x+3=0$ 的两根，求 $\\alpha^2 + \\beta^2$ 的值',
                'difficulty': 5,
                'solution': '$\\alpha+\\beta=5$，$\\alpha\\beta=3$，$\\alpha^2+\\beta^2=(\\alpha+\\beta)^2-2\\alpha\\beta=19$',
                'hint_pattern': 'quadratic_roots',
                'tags': ['一元二次方程', '韦达定理']
            },
            # 题目12：高级 - 圆的性质
            {
                'type': QuestionType.PROOF,
                'content': '如图，$AB$是$\\odot O$直径，$C$在圆上，$CD\\perp AB$于$D$。求证：$CD^2=AD\\cdot DB$',
                'difficulty': 5,
                'solution': '连接AC,BC，用射影定理或相似三角形证明',
                'hint_pattern': 'circle_theorem',
                'tags': ['圆', '射影定理']
            },
        ]
        
        # 插入题目
        for q_data in questions_data:
            tags = q_data.pop('tags', [])
            question = Question(**q_data)
            db.add(question)
            db.flush()  # 获取 question.id
            
            # 插入标签
            for tag in tags:
                question_tag = QuestionTag(question_id=question.id, tag=tag)
                db.add(question_tag)
        
        db.commit()
        print(f"成功插入 {len(questions_data)} 道题目！")
        
    except Exception as e:
        db.rollback()
        print(f"插入题目失败: {e}")
        raise
    finally:
        db.close()

def insert_hint_rules():
    """插入提示规则数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing = db.query(HintRule).first()
        if existing:
            print("数据库中已有提示规则数据，跳过插入。")
            return
        
        print("正在插入提示规则数据...")
        
        # 规则数据（从 sql.log 提取）
        rules_data = [
            {
                'pattern_id': 'vertex_formula',
                'trigger_keywords': ["顶点", "坐标", "对称轴"],
                'hint_text': '提示：二次函数 $y=ax^2+bx+c$ 的顶点坐标公式为 $\\left(-\\frac{b}{2a}, \\frac{4ac-b^2}{4a}\\right)$'
            },
            {
                'pattern_id': 'square_root',
                'trigger_keywords': ["开方", "平方", "根"],
                'hint_text': '注意：方程 $x^2=k$ 的解为 $x=\\pm\\sqrt{k}$，需考虑正负两种情况'
            },
        ]
        
        # 插入规则
        for rule_data in rules_data:
            rule = HintRule(**rule_data)
            db.add(rule)
        
        db.commit()
        print(f"成功插入 {len(rules_data)} 条提示规则！")
        
    except Exception as e:
        db.rollback()
        print(f"插入提示规则失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)
    
    try:
        # 创建表
        init_database()
        
        # 插入题目
        insert_questions()
        
        # 插入规则
        insert_hint_rules()
        
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"初始化失败: {e}")
        raise

if __name__ == "__main__":
    main()

