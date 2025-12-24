# 中考数学残局挑战 - 前端项目

基于 Vue 3 + Vite 构建的数学挑战游戏前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **GSAP** - 专业级动画库
- **Font Awesome** - 图标库

## 项目结构

```
front/
├── src/
│   ├── components/
│   │   └── Home.vue      # 主页面组件
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── index.html            # HTML 入口
├── package.json          # 项目配置
├── vite.config.js        # Vite 配置
├── tailwind.config.js    # Tailwind 配置
└── postcss.config.js     # PostCSS 配置
```

## 安装依赖

```bash
npm install
```

## 开发运行

```bash
npm run dev
```

项目将在 `http://localhost:3000` 启动

## 构建生产版本

```bash
npm run build
```

## 预览生产构建

```bash
npm run preview
```

## 功能特性

- 🎯 三个难度等级选择（初级、中级、高级）
- 📚 三个知识点分类（代数、几何、统计与概率）
- ✨ 流畅的 GSAP 动画效果
- 📱 响应式设计，支持移动端
- 🎨 精美的 UI 设计，采用中国风主题

## 开发说明

项目使用 Vue 3 的 Composition API，所有交互逻辑都在 `Home.vue` 组件中实现。

## 后端对接

### 配置 WebSocket 地址

创建 `.env` 文件（可选）：

```bash
# 使用独立的 WebSocket 服务器（默认端口 8765）
VITE_WS_URL=ws://localhost:8765

# 或使用 ASGI 服务器（默认端口 8000）
# VITE_WS_URL=ws://localhost:8000/ws/
```

### 启动后端

```bash
# 方式一：独立 WebSocket 服务器
cd ../back
python start_websocket_server.py

# 方式二：ASGI 服务器（支持 Django API + WebSocket）
python start_asgi_server.py
```

详细对接说明请查看 `../INTEGRATION.md` 文件。

