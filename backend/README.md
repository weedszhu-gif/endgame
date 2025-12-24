# 初中数学残局挑战系统 - Backend 模块

## 1. 项目说明

### 1.1 项目概述
初中数学残局挑战系统是一个AI辅助的初中数学学习系统，提供实时的解题指导和苏格拉底式提示。该系统通过先进的AI技术，模拟教师的教学方式，引导学生自主思考和解决问题，而不是直接给出答案。

### 1.2 技术栈
- **后端框架**: FastAPI
- **WebSocket**: 基于FastAPI的WebSocket支持
- **AI模型**: 支持多种LLM提供商（OpenAI、Doubao、Ernie、Qwen、Hunyuan、Claude、Gemini）
- **数据库**: SQLAlchemy + SQLite
- **测试框架**: pytest + pytest-asyncio
- **环境配置**: python-dotenv

### 1.3 目录结构
```
backend/
├── config/              # 应用配置
│   ├── __init__.py
│   └── settings.py      # 配置类定义
├── models/             # 数据模型
│   ├── __init__.py
│   ├── base.py          # 数据库基础设置
│   └── models.py        # 业务模型定义
├── api/                # API层
│   ├── __init__.py
│   ├── endpoints/       # HTTP API端点
│   │   ├── __init__.py
│   │   └── endpoints.py  # 具体API实现
│   └── websocket/       # WebSocket端点
│       ├── __init__.py
│       └── websocket.py  # WebSocket实现
├── services/           # 服务层
│   ├── __init__.py
│   ├── ai/              # AI服务
│   │   ├── __init__.py
│   │   ├── ai_service.py      # AI业务逻辑
│   │   └── model_client/      # 大模型客户端
│   │       ├── __init__.py
│   │       ├── client.py       # 统一客户端
│   │       ├── strategies.py   # 各模型策略
│   │       └── types.py        # 类型定义
│   ├── hint/            # 提示生成服务
│   │   ├── __init__.py
│   │   └── socratic_hint.py     # 苏格拉底式提示生成
│   ├── conversation/    # 对话管理
│   │   ├── __init__.py
│   │   ├── connection_manager.py  # WebSocket连接管理
│   │   └── conversation_history.py  # 对话历史管理
│   ├── learning/        # 学习跟踪
│   │   ├── __init__.py
│   │   └── learning_tracker.py  # 学习跟踪服务
│   └── prompt/          # Prompt管理
│       ├── __init__.py
│       └── prompt_manager.py    # 提示词管理
├── storage/            # 数据存储服务
│   ├── __init__.py
│   └── storage_service.py  # 存储服务实现
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── id_generator.py   # ID生成工具
│   ├── logger.py         # 日志工具
│   ├── retry.py          # 重试装饰器
│   ├── string_utils.py   # 字符串处理
│   └── time_utils.py     # 时间处理
├── tests/              # 测试用例
│   ├── __init__.py
│   ├── test_ai_service.py        # AI服务测试
│   ├── test_socratic_hint.py     # 提示生成测试
│   ├── test_websocket.py         # WebSocket测试
│   └── test_cases.md             # 测试用例文档
├── .env                # 环境变量配置
├── .env.example        # 环境变量示例
├── Dockerfile          # Docker配置
├── main.py             # 应用入口
├── requirements.txt     # 依赖列表
└── README.md           # 项目说明文档
```

### 1.4 核心功能模块

#### 1.4.1 AI服务模块
- 统一的ModelClient，支持多种LLM提供商
- 苏格拉底式提示生成
- 解题过程分析
- 指数退避重试机制

#### 1.4.2 WebSocket通信模块
- 实时双向通信
- 连接管理和心跳机制
- 消息类型处理
- 错误处理

#### 1.4.3 对话管理模块
- 对话历史记录
- 上下文管理
- 会话状态跟踪

#### 1.4.4 学习跟踪模块
- 学习会话管理
- 解题步骤记录
- 提示使用统计
- 错误类型分析

### 1.5 环境配置

#### 1.5.1 环境变量
创建`.env`文件，根据`.env.example`配置以下环境变量：

```
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS配置
ALLOW_ORIGINS=*

# AI模型配置
AI_MODEL_TYPE=doubao  # 可选: openai, doubao, ernie, qwen, hunyuan, claude, gemini
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=100

# AI模型API密钥
OPENAI_API_KEY=your_openai_api_key
DOUBAO_API_KEY=your_doubao_api_key
ERNIE_ACCESS_TOKEN=your_ernie_access_token
QWEN_API_KEY=your_qwen_api_key
HUNYUAN_SECRET_ID=your_hunyuan_secret_id
HUNYUAN_SECRET_KEY=your_hunyuan_secret_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key

# 数据库配置
DATABASE_URL=sqlite:///./app.db
```

### 1.6 安装和运行

#### 1.6.1 安装依赖
```bash
# 使用国内pip源安装依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 1.6.2 运行开发服务器
```bash
# 直接运行
python main.py

# 使用uvicorn运行
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 1.6.3 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## 2. 测试说明

### 2.1 测试框架
- **pytest**: 核心测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-mock**: Mock支持
- **httpx**: HTTP客户端测试

### 2.2 测试用例
测试用例覆盖以下功能：

#### 2.2.1 AI服务测试
- 成功场景测试
- 失败场景测试
- 重试机制测试
- 解题分析测试
- 初中数学题处理能力测试

#### 2.2.2 苏格拉底式提示生成测试
- 基础提示测试
- 进阶提示测试
- 深度提示测试
- 无匹配规则测试
- 不区分大小写测试
- 多关键词测试
- 初中数学题提示测试

#### 2.2.3 WebSocket测试
- 连接测试
- 步骤消息测试
- 错误报告测试
- 无效消息测试
- 未知消息类型测试
- 缺少内容测试
- 健康检查测试
- 根路径测试

### 2.3 运行测试

#### 2.3.1 运行所有测试
```bash
python -m pytest tests/ -v
```

#### 2.3.2 运行特定模块测试
```bash
# 运行AI服务测试
python -m pytest tests/test_ai_service.py -v

# 运行苏格拉底式提示测试
python -m pytest tests/test_socratic_hint.py -v

# 运行WebSocket测试
python -m pytest tests/test_websocket.py -v
```

#### 2.3.3 运行测试并生成报告
```bash
# 生成HTML报告
python -m pytest tests/ --html=report.html

# 生成JUnit XML报告
python -m pytest tests/ --junitxml=report.xml
```

### 2.4 测试用例文档
详细的测试用例请参考 `tests/test_cases.md` 文件，包含了初中数学各阶段的解题例子和预期结果。

## 3. 前端接入文档

### 3.1 API接口说明

#### 3.1.1 HTTP API

##### 3.1.1.1 获取提示
- **URL**: `/api/hint`
- **方法**: POST
- **请求体**:
  ```json
  {
    "content": "解题步骤内容",
    "use_ai": false  // 可选，是否直接使用AI
  }
  ```
- **响应**:
  ```json
  {
    "type": "hint",
    "content": "生成的提示内容"
  }
  ```

##### 3.1.1.2 获取苏格拉底式提示
- **URL**: `/api/socratic-hint`
- **方法**: POST
- **请求体**:
  ```json
  {
    "content": "解题步骤内容"
  }
  ```
- **响应**:
  ```json
  {
    "type": "hint",
    "content": "生成的提示内容"
  }
  ```

##### 3.1.1.3 获取AI提示
- **URL**: `/api/ai-hint`
- **方法**: POST
- **请求体**:
  ```json
  {
    "content": "解题步骤内容"
  }
  ```
- **响应**:
  ```json
  {
    "type": "hint",
    "content": "生成的提示内容"
  }
  ```

##### 3.1.1.4 健康检查
- **URL**: `/api/health`
- **方法**: GET
- **响应**:
  ```json
  {
    "status": "ok",
    "message": "API服务正常运行"
  }
  ```

### 3.2 WebSocket通信

#### 3.2.1 连接建立
```javascript
// JavaScript示例
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('WebSocket连接已建立');
};
```

#### 3.2.2 消息类型

##### 3.2.2.1 心跳消息
- **发送**:
  ```json
  {"type": "ping"}
  ```
- **响应**:
  ```json
  {"type": "pong"}
  ```

##### 3.2.2.2 步骤消息
- **发送**:
  ```json
  {"type": "step", "content": "解题步骤内容"}
  ```
- **响应**:
  ```json
  {"type": "hint", "content": "生成的提示内容"}
  ```

##### 3.2.2.3 错误报告消息
- **发送**:
  ```json
  {"type": "error_report", "content": "错误内容"}
  ```
- **响应**:
  ```json
  {"type": "acknowledge", "content": "错误报告已接收"}
  ```

##### 3.2.2.4 错误消息
- **接收**:
  ```json
  {"type": "error", "content": "错误信息"}
  ```

### 3.3 错误处理

#### 3.3.1 HTTP错误
| 状态码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

#### 3.3.2 WebSocket错误
- 连接断开: 客户端应实现重连机制
- 消息格式错误: 服务器会返回error消息
- 未知消息类型: 服务器会返回error消息

### 3.4 最佳实践

#### 3.4.1 连接管理
- 实现心跳机制，定期发送ping消息
- 实现重连机制，处理连接断开情况
- 合理设置连接超时时间

#### 3.4.2 消息处理
- 验证服务器返回的消息格式
- 实现消息队列，处理并发消息
- 对敏感信息进行加密处理

#### 3.4.3 性能优化
- 合理设置AI请求频率，避免频繁调用
- 实现本地缓存，减少重复请求
- 对大文件进行分片传输

#### 3.4.4 安全性
- 验证服务器证书
- 实现身份认证和授权
- 对敏感数据进行加密

### 3.5 前端示例代码

#### 3.5.1 WebSocket连接示例
```javascript
class MathChallengeClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.callbacks = {};
    
    this.connect();
  }
  
  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
      this.connected = true;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket连接已关闭');
      this.connected = false;
      this.stopHeartbeat();
      this.reconnect();
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }
  
  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }
  
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.connected) {
        this.sendPing();
      }
    }, 30000);
  }
  
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  sendPing() {
    this.send({ type: 'ping' });
  }
  
  sendStep(content) {
    this.send({ type: 'step', content });
  }
  
  sendErrorReport(content) {
    this.send({ type: 'error_report', content });
  }
  
  send(message) {
    if (this.connected) {
      this.ws.send(JSON.stringify(message));
    }
  }
  
  handleMessage(message) {
    switch (message.type) {
      case 'pong':
        console.log('收到心跳响应');
        break;
      case 'hint':
        this.onHint(message.content);
        break;
      case 'error':
        this.onError(message.content);
        break;
      case 'acknowledge':
        this.onAcknowledge(message.content);
        break;
      default:
        console.warn('未知消息类型:', message.type);
    }
  }
  
  // 回调函数
  onHint(content) {
    console.log('收到提示:', content);
  }
  
  onError(content) {
    console.error('收到错误:', content);
  }
  
  onAcknowledge(content) {
    console.log('收到确认:', content);
  }
  
  // 关闭连接
  close() {
    this.stopHeartbeat();
    if (this.connected) {
      this.ws.close();
    }
  }
}

// 使用示例
const client = new MathChallengeClient('ws://localhost:8000/ws');

// 发送解题步骤
client.sendStep('设未知数x');

// 处理提示
client.onHint = (content) => {
  console.log('AI提示:', content);
  // 显示提示给用户
};
```

#### 3.5.2 HTTP API示例
```javascript
// 使用fetch API调用HTTP API
async function getMathHint(stepContent, useAi = false) {
  try {
    const response = await fetch('http://localhost:8000/api/hint', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: stepContent,
        use_ai: useAi
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP错误! 状态: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取提示失败:', error);
    throw error;
  }
}

// 使用示例
getMathHint('设未知数x')
  .then(data => {
    console.log('提示内容:', data.content);
    // 显示提示给用户
  })
  .catch(error => {
    console.error('错误:', error);
  });
```

## 4. 部署说明

### 4.1 开发环境部署
- 安装Python 3.10+和pip
- 安装依赖: `pip install -r requirements.txt`
- 配置环境变量: 复制`.env.example`为`.env`并配置
- 运行开发服务器: `python main.py`

### 4.2 生产环境部署

#### 4.2.1 使用Docker部署
```bash
# 构建Docker镜像
docker build -t math-challenge-backend .

# 运行Docker容器
docker run -d -p 8000:8000 --env-file .env math-challenge-backend
```

#### 4.2.2 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket配置
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 5. 监控和维护

### 5.1 日志管理
- 系统日志: 记录系统运行状态和错误信息
- API访问日志: 记录API调用情况
- AI服务日志: 记录AI服务调用情况

### 5.2 性能监控
- 监控API响应时间
- 监控AI服务调用频率和响应时间
- 监控WebSocket连接数和消息频率

### 5.3 常见问题排查
- 检查环境变量配置
- 检查日志文件
- 检查数据库连接
- 检查AI模型API密钥

## 6. 开发指南

### 6.1 代码规范
- 使用PEP 8规范
- 函数和类文档字符串
- 类型注解
- 单元测试覆盖

### 6.2 贡献流程
1. Fork仓库
2. 创建特性分支
3. 提交代码
4. 运行测试
5. 提交Pull Request

### 6.3 版本管理
- 使用语义化版本号
- 定期发布更新
- 维护CHANGELOG

## 7. 联系方式

- 项目维护者: 初中数学残局挑战系统团队
- 技术支持: math-challenge-support@example.com
- 文档地址: http://localhost:8000/docs

## 8. 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

感谢您使用初中数学残局挑战系统！
