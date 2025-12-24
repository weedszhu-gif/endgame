# 初中数学残局挑战系统 - Python后端方案

## 1. 技术栈选型

| 类别 | 技术 | 版本 | 优势 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.104+ | 高性能、自动生成API文档、支持异步、原生WebSocket支持 |
| 语言 | Python | 3.10+ | AI生态友好、丰富的数学库支持、开发效率高 |
| WebSocket | FastAPI WebSockets | 内置 | 与框架无缝集成、异步支持 |
| AI集成 | OpenAI Python SDK | 1.0+ | 官方支持、最新功能、稳定可靠 |
| 环境管理 | python-dotenv | 1.0+ | 安全管理环境变量 |
| 数学处理 | SymPy | 1.12+ | 符号计算、代数运算、数学公式处理 |
| 开发服务器 | Uvicorn | 0.24+ | 高性能ASGI服务器、自动重载 |
| 部署 | Docker | 最新 | 容器化部署、环境一致性 |

## 2. 项目结构

```
backend/
├── api/                  # API路由模块
│   ├── __init__.py       # 包初始化
│   ├── websocket.py      # WebSocket端点实现
│   └── endpoints.py      # REST API端点（可选）
├── services/             # 业务逻辑层
│   ├── __init__.py       # 包初始化
│   ├── socratic_hint.py  # 苏格拉底式提问逻辑
│   ├── ai_service.py     # AI服务集成
│   └── learning_tracker.py  # 学习跟踪服务
├── utils/                # 工具函数
│   ├── __init__.py       # 包初始化
│   ├── formula_parser.py # 数学公式解析工具
│   └── error_analyzer.py # 错误分析工具
├── models/               # 数据模型
│   ├── __init__.py       # 包初始化
│   ├── user.py           # 用户模型
│   └── learning_data.py  # 学习数据模型
├── main.py               # 应用入口
├── requirements.txt      # 依赖配置
├── .env.example          # 环境变量示例
└── Dockerfile            # Docker配置
```

## 3. 核心功能设计

### 3.1 WebSocket通信模块

**功能**：处理前端与后端的实时通信，支持发送解题步骤和接收AI提示。

**主要端点**：
- `/ws` - WebSocket连接端点

**消息格式**：
- 前端发送：`{"type": "step", "content": "解题步骤内容"}`
- 后端响应：`{"type": "hint", "content": "苏格拉底式提示"}`

### 3.2 AI服务集成模块

**功能**：调用OpenAI API获取AI辅助提示，实现高级数学推理。

**主要功能**：
- 构建系统提示，指导AI生成苏格拉底式提问
- 处理用户输入，生成AI请求
- 解析AI响应，提取有效提示

### 3.3 苏格拉底式提问模块

**功能**：基于本地规则生成苏格拉底式提示，减少对AI的依赖。

**主要规则**：
- 基础提示：针对常见操作（设未知数、移项、解方程）
- 进阶提示：针对复杂操作（合并同类项、系数化为1）
- 深度提示：针对验证和解法优化（检验、辅助线）

### 3.4 学习跟踪模块

**功能**：记录用户的学习过程数据，用于生成学习报告。

**跟踪数据**：
- 解题步骤
- 步骤耗时
- 错误类型
- 提示使用次数

## 4. API设计

### 4.1 WebSocket API

```python
# 连接端点
ws://localhost:8000/ws

# 消息示例
# 客户端发送
{
  "type": "step",
  "content": "设x为书的价格"
}

# 服务器响应
{
  "type": "hint",
  "content": "你为什么选择这个变量？是否有更简洁的设定方式？"
}
```

### 4.2 REST API（可选扩展）

| 端点 | 方法 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/problems` | GET | 获取问题列表 | 无 | 问题列表JSON |
| `/api/problems/{id}` | GET | 获取单个问题 | 无 | 问题详情JSON |
| `/api/reports` | POST | 生成学习报告 | 学习数据JSON | 报告URL |
| `/api/learning-data` | POST | 保存学习数据 | 学习数据JSON | 成功状态 |

## 5. 依赖管理

```txt
# requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
python-dotenv>=1.0.0
openai>=1.0.0
sympy>=1.12.0
pydantic>=2.4.0
```

## 6. 环境变量配置

```env
# .env.example
# OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key

# 后端服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# AI模型配置
AI_MODEL=gpt-4-turbo
AI_TEMPERATURE=0.7
```

## 7. 开发与运行

### 7.1 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 Docker运行

```bash
# 构建镜像
docker build -t endgame-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env endgame-backend
```

## 8. 集成与测试

### 8.1 与前端集成

前端需要更新WebSocket连接地址：

```javascript
// 原代码
// const wsService = new WebSocketService('wss://your-worker.example.com');

// 更新后
const wsService = new WebSocketService('ws://localhost:8000/ws');
```

### 8.2 测试用例

1. **基础功能测试**：
   - 连接WebSocket
   - 发送解题步骤
   - 验证提示返回

2. **AI集成测试**：
   - 测试本地规则提示
   - 测试AI提示
   - 测试错误处理

3. **性能测试**：
   - 并发连接测试
   - 响应时间测试

## 9. 扩展功能

基于Python的后端可以轻松扩展以下功能：

1. **本地AI模型**：集成开源LLM模型（如Llama 2）实现本地化部署
2. **高级数学处理**：使用SymPy实现数学公式验证和正确性检查
3. **个性化学习**：基于用户历史数据提供个性化提示
4. **多语言支持**：利用Python的自然语言处理库支持多语言
5. **数据分析**：使用Pandas进行学习数据的深入分析

## 10. 部署方案

### 10.1 容器化部署

使用Docker和docker-compose实现一键部署：

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 10.2 云平台部署

推荐使用以下云平台部署：

- **AWS**: ECS + Fargate或Lambda + API Gateway
- **GCP**: Cloud Run
- **Azure**: App Service
- **Vercel**: Serverless Functions（如果使用FastAPI）
- **Render**: Web Services

## 11. 监控与维护

- 使用FastAPI的自动生成文档（`/docs`和`/redoc`）进行API监控
- 配置日志记录，监控系统运行状态
- 使用环境变量管理敏感信息，确保安全性

## 12. 总结

本方案基于Python和FastAPI框架，提供了一个高性能、易扩展、AI友好的后端解决方案。通过使用Python的强大生态系统，可以更好地支持AI功能，并为未来的功能扩展提供更大的灵活性。