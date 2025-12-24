# Python后端运行示例

## 1. 环境准备

### 1.1 安装Python
确保安装了Python 3.10或更高版本：

```bash
python --version
# 或
python3 --version
```

### 1.2 安装依赖

进入后端目录并安装所需依赖：

```bash
cd backend
pip install -r requirements.txt
# 或使用pip3
pip3 install -r requirements.txt
```

### 1.3 配置环境变量

复制环境变量示例文件并配置：

```bash
cp .env.example .env
```

编辑`.env`文件，添加你的OpenAI API密钥：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 2. 运行后端服务

### 2.1 开发模式

使用Uvicorn运行开发服务器：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或直接运行Python文件：

```bash
python main.py
```

### 2.2 生产模式

使用Gunicorn或其他WSGI服务器运行：

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### 2.3 Docker模式

使用Docker Compose运行整个系统：

```bash
cd ..  # 回到项目根目录
docker-compose up --build
```

## 3. 测试后端服务

### 3.1 访问API文档

FastAPI自动生成API文档，可以通过以下地址访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3.2 测试WebSocket服务

使用WebSocket客户端工具（如wscat）测试：

```bash
# 安装wscat
npm install -g wscat

# 连接WebSocket服务
wscat -c ws://localhost:8000/ws

# 发送消息
> {"type": "step", "content": "设x为书的价格"}

# 接收提示
< {"type": "hint", "content": "你为什么选择这个变量？是否有更简洁的设定方式？"}
```

### 3.3 测试REST API

使用curl测试REST API：

```bash
# 获取提示
curl -X POST http://localhost:8000/api/hint -H "Content-Type: application/json" -d '{"content": "设x为书的价格"}'

# 获取基于本地规则的提示
curl -X POST http://localhost:8000/api/socratic-hint -H "Content-Type: application/json" -d '{"content": "移项"}'

# 获取基于AI的提示
curl -X POST http://localhost:8000/api/ai-hint -H "Content-Type: application/json" -d '{"content": "解方程2x+5=15"}'
```

## 4. 前端集成

### 4.1 修改前端WebSocket连接

更新前端代码中的WebSocket连接地址：

```javascript
// 原代码
// const wsService = new WebSocketService('wss://your-worker.example.com');

// 更新后
const wsService = new WebSocketService('ws://localhost:8000/ws');
```

### 4.2 运行前端

在项目根目录运行前端：

```bash
npm install
npm run dev
```

前端将在 http://localhost:5173 运行。

## 5. 功能测试

### 5.1 测试用例1：代数方程求解

问题：解方程 2x + 5 = 15

1. 前端输入："设x为未知数"
   - 预期提示："你为什么选择这个变量？是否有更简洁的设定方式？"

2. 前端输入："移项：2x = 15 - 5"
   - 预期提示："移项时是否考虑了符号变化？"

3. 前端输入："计算：2x = 10"
   - 预期提示："你确定计算过程正确吗？可以再检查一遍吗？"

### 5.2 测试用例2：几何证明

问题：在△ABC中，AB=AC，证明∠B=∠C

1. 前端输入："作辅助线：作AD⊥BC于D"
   - 预期提示："这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？"

2. 前端输入："证明△ABD≌△ACD"
   - 预期提示："你是如何证明全等的？是否符合相应的判定定理？"

## 6. 扩展功能

### 6.1 添加新的提示规则

在`services/socratic_hint.py`中添加新的规则：

```python
if '新的关键词' in step_text:
    return '新的提示内容'
```

### 6.2 扩展AI功能

在`services/ai_service.py`中扩展AI功能，如添加新的系统提示或使用不同的AI模型。

### 6.3 添加数据持久化

使用SQLAlchemy或其他ORM库添加数据库支持，将学习数据持久化存储。

## 7. 部署到云平台

### 7.1 AWS部署

使用ECS + Fargate部署容器：

```bash
# 构建镜像
docker build -t endgame-backend .

# 推送镜像到ECR
docker tag endgame-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/endgame-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/endgame-backend:latest
```

### 7.2 GCP部署

使用Cloud Run部署：

```bash
gcloud run deploy endgame-backend \
  --image gcr.io/my-project/endgame-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --update-env-vars OPENAI_API_KEY=your_openai_api_key_here
```

### 7.3 Azure部署

使用App Service部署：

```bash
az webapp up --name endgame-backend --resource-group my-resource-group --plan my-app-service-plan --runtime PYTHON:3.10 --sku B1
```

## 8. 故障排除

### 8.1 WebSocket连接失败

- 检查后端服务是否正在运行
- 检查端口是否正确
- 检查防火墙设置
- 确保使用正确的协议（ws:// 而不是 http://）

### 8.2 AI提示获取失败

- 检查OpenAI API密钥是否正确
- 检查网络连接
- 检查OpenAI API的使用限制
- 查看日志以获取详细错误信息

### 8.3 依赖安装失败

- 确保使用正确的Python版本
- 尝试更新pip：`pip install --upgrade pip`
- 检查网络连接

## 9. 性能优化

### 9.1 缓存AI响应

添加缓存层以减少对OpenAI API的调用：

```python
import functools
from cachetools import TTLCache

# 创建缓存，有效期10分钟
cache = TTLCache(maxsize=100, ttl=600)

@functools.lru_cache(maxsize=100)
async def get_ai_hint(step_content: str) -> str:
    # 检查缓存
    if step_content in cache:
        return cache[step_content]
    
    # 调用AI API
    hint = await client.chat.completions.create(...)
    
    # 保存到缓存
    cache[step_content] = hint
    
    return hint
```

### 9.2 异步处理

使用FastAPI的异步功能提高并发性能：

```python
@app.post("/async-hint")
async def get_async_hint(request: StepRequest):
    # 使用异步处理
    hint = await get_ai_hint(request.content)
    return {"hint