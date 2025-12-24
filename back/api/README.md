
# 题库系统 API

这是一个基于Django REST Framework的题库系统API，用于管理题目、知识点标签、提示规则和答题记录。

## 数据库表结构

### 题库表 (questions)
- id: 主键，自增
- type: 题型（choice选择、calculation计算、proof证明）
- content: 题目内容（含LaTeX公式）
- difficulty: 难度（1-5）
- solution: 标准答案
- hint_pattern: 规则引擎标识符

### 知识点标签表 (question_tags)
- question_id: 题目ID（外键）
- tag: 标签内容，如"二次函数"、"相似三角形"

### 规则引擎表 (hint_rules)
- id: 主键，自增
- pattern_id: 规则标识
- trigger_keywords: 触发关键词数组（JSON格式）
- hint_text: 提示内容

### 学生答题记录表 (answer_records)
- id: 主键，自增
- question_id: 题目ID（外键）
- student_input: 学生输入步骤
- used_hint: 使用的提示
- created_at: 创建时间

## API端点

### 题目管理 (/api/questions/)
- GET: 获取题目列表
- POST: 创建新题目
- GET /{id}/: 获取特定题目
- PUT /{id}/: 更新题目
- DELETE /{id}/: 删除题目
- POST /{id}/add_tag/: 为题目添加标签
- DELETE /{id}/remove_tag/: 删除题目标签

### 提示规则管理 (/api/hint-rules/)
- GET: 获取规则列表
- POST: 创建新规则
- GET /{id}/: 获取特定规则
- PUT /{id}/: 更新规则
- DELETE /{id}/: 删除规则
- POST /get_hint/: 根据学生输入获取提示

### 答题记录管理 (/api/answer-records/)
- GET: 获取答题记录列表
- POST: 创建新答题记录
- GET /{id}/: 获取特定答题记录
- PUT /{id}/: 更新答题记录
- DELETE /{id}/: 删除答题记录

## 使用示例

### 创建题目
```bash
curl -X POST http://localhost:8000/api/questions/   -H "Content-Type: application/json"   -d '{
    "type": "choice",
    "content": "以下哪个选项是正确的？",
    "difficulty": 3,
    "solution": "选项A",
    "hint_pattern": "math_basic"
  }'
```

### 为题目添加标签
```bash
curl -X POST http://localhost:8000/api/questions/1/add_tag/   -H "Content-Type: application/json"   -d '{
    "tag": "二次函数"
  }'
```

### 创建提示规则
```bash
curl -X POST http://localhost:8000/api/hint-rules/   -H "Content-Type: application/json"   -d '{
    "pattern_id": "math_basic",
    "trigger_keywords": ["公式", "计算", "求解"],
    "hint_text": "请使用二次函数的标准公式进行计算"
  }'
```

### 创建答题记录并获取提示
```bash
curl -X POST http://localhost:8000/api/answer-records/   -H "Content-Type: application/json"   -d '{
    "question": 1,
    "student_input": "我需要使用什么公式来计算？",
    "get_hint": true
  }'
```

## 启动服务

1. 确保已安装Django和Django REST Framework:
```bash
pip install django djangorestframework django-filter
```

2. 运行数据库迁移:
```bash
python api/manage.py makemigrations
python api/manage.py migrate
```

3. 启动开发服务器:
```bash
python api/manage.py runserver 0.0.0.0:8000
```

4. 访问API文档:
打开浏览器访问 http://localhost:8000/api/
