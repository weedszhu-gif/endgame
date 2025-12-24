# 前后端对接说明

本文档说明如何将前端和后端项目对接起来。

## 项目结构

```
endgame/
├── front/          # Vue 3 前端项目
└── back/           # Python 后端项目（WebSocket 服务器）
```

## 后端启动

### 方式一：使用独立的 WebSocket 服务器（推荐用于开发）

```bash
cd back
python start_websocket_server.py
```

默认配置：
- 监听地址：`0.0.0.0`
- 端口：`8765`
- WebSocket 地址：`ws://localhost:8765`

自定义配置：
```bash
python start_websocket_server.py --host 127.0.0.1 --port 8765
```

### 方式二：使用 ASGI 服务器（支持 Django API + WebSocket）

```bash
cd back
python start_asgi_server.py
```

默认配置：
- 监听地址：`0.0.0.0`
- 端口：`8000`
- WebSocket 地址：`ws://localhost:8000/ws/`
- Django API 地址：`http://localhost:8000/api/`

开发模式（自动重载）：
```bash
python start_asgi_server.py --reload
```

## 前端配置

### 1. 安装依赖

```bash
cd front
npm install
```

### 2. 配置 WebSocket 地址

创建 `.env` 文件（可选，不创建则使用默认值）：

```bash
# 使用独立的 WebSocket 服务器（方式一）
VITE_WS_URL=ws://localhost:8765

# 或使用 ASGI 服务器（方式二）
# VITE_WS_URL=ws://localhost:8000/ws/
```

### 3. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动。

## 使用流程

1. **启动后端服务器**
   ```bash
   cd back
   python start_websocket_server.py
   ```

2. **启动前端服务器**
   ```bash
   cd front
   npm run dev
   ```

3. **访问前端页面**
   - 打开浏览器访问 `http://localhost:3000`
   - 选择难度和知识点
   - 进入答题页面
   - 在输入框中输入解题步骤
   - AI 会自动提供提示

## WebSocket 通信协议

### 客户端发送消息

#### 请求 AI 提示
```json
{
  "type": "chat",
  "message": "你是一个数学解题助手。请根据学生的解题步骤，给出适当的提示..."
}
```

#### 重置会话
```json
{
  "type": "reset"
}
```

#### 获取历史记录
```json
{
  "type": "history"
}
```

### 服务器响应消息

#### 系统消息
```json
{
  "type": "system",
  "message": "连接成功！您可以开始对话了。"
}
```

#### 状态消息
```json
{
  "type": "status",
  "message": "正在处理您的请求..."
}
```

#### AI 响应开始
```json
{
  "type": "ai_response_start",
  "message": "AI回复开始"
}
```

#### AI 响应内容块（流式）
```json
{
  "type": "ai_response_chunk",
  "content": "这是AI回复的一部分内容"
}
```

#### AI 响应结束
```json
{
  "type": "ai_response_end",
  "message": "AI回复结束"
}
```

#### 错误消息
```json
{
  "type": "error",
  "message": "错误信息"
}
```

## 功能说明

### 前端功能

1. **自动连接**：页面加载时自动连接 WebSocket
2. **自动重连**：连接断开时自动尝试重连（最多 5 次）
3. **流式响应**：实时显示 AI 回复内容
4. **智能提示**：根据用户输入自动请求 AI 提示（停止输入 800ms 后）
5. **连接状态**：显示当前 WebSocket 连接状态

### 后端功能

1. **多客户端支持**：支持多个客户端同时连接
2. **会话管理**：每个客户端维护独立的会话历史
3. **流式响应**：支持流式返回 AI 回复，提升用户体验
4. **错误处理**：完善的错误处理和日志记录

## 故障排除

### 前端无法连接后端

1. **检查后端是否启动**
   ```bash
   # 检查端口是否被占用
   lsof -i :8765  # 独立服务器
   lsof -i :8000  # ASGI 服务器
   ```

2. **检查 WebSocket 地址配置**
   - 确认 `.env` 文件中的 `VITE_WS_URL` 配置正确
   - 确认后端服务器监听的地址和端口

3. **检查防火墙设置**
   - 确保防火墙允许相应端口的连接

### WebSocket 连接失败

1. **查看后端日志**
   - 后端服务器会输出详细的连接日志

2. **查看浏览器控制台**
   - 打开浏览器开发者工具，查看 Console 和 Network 标签

3. **检查网络连接**
   - 确认前后端在同一网络环境
   - 如果使用不同机器，确保 IP 地址配置正确

### AI 响应异常

1. **检查后端配置**
   - 确认 `back/plugins/mlops.py` 中的 AI 模型配置正确
   - 查看后端日志中的错误信息

2. **检查提示词格式**
   - 确认发送给 AI 的提示词格式正确

## 开发建议

1. **开发环境**：使用独立的 WebSocket 服务器（方式一），启动更快
2. **生产环境**：使用 ASGI 服务器（方式二），支持更多功能
3. **调试**：使用浏览器开发者工具和服务器日志进行调试
4. **测试**：使用 `back/websocket_client.html` 测试后端 WebSocket 功能

## 下一步

- [ ] 添加用户认证
- [ ] 添加题目管理 API
- [ ] 添加答题记录存储
- [ ] 优化 AI 提示词
- [ ] 添加更多交互功能

