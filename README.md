# 🎯 数学残局挑战系统

<div align="center">

**AI驱动的苏格拉底式数学学习平台**

[![Vue 3](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**不直接给答案，引导学生思考**

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [项目演示](#-项目演示)

</div>

---

## 📖 项目简介

**数学残局挑战系统**是一个基于AI的智能数学学习平台，采用苏格拉底式教学法，通过引导性问题帮助学生自主思考和解决问题，而不是直接给出答案。

### 🎯 核心理念

- **启发式教学**：不直接给答案，通过提问引导学生思考
- **实时智能辅导**：AI 24小时在线，随时为学生提供个性化指导
- **多维度分析**：六维能力评估 + 知识点评分，精准定位薄弱环节
- **科技向善**：降低教育成本，让优质教育资源普惠化

---

## ✨ 核心特性

### 🧠 混合智能提示系统
- **本地规则引擎**：快速响应（<10ms），覆盖常见解题场景
- **AI大模型集成**：深度理解，处理复杂问题
- **智能降级策略**：规则优先，AI兜底，兼顾速度与智能

### ⚡ 实时流式交互
- **WebSocket双向通信**：毫秒级响应，流畅交互体验
- **流式AI响应**：实时显示AI提示，减少等待时间
- **自动触发机制**：用户停止输入800ms后自动获取提示

### 📊 多维度学习分析
- **六维能力雷达图**：逻辑推理、空间想象、计算能力、问题分析、创新思维、知识应用
- **知识点评分**：精准定位薄弱环节
- **个性化学习建议**：基于数据分析生成针对性建议

### 🎮 自适应难度系统
- **三级难度**：初级（难度1-2）、中级（难度3）、高级（难度4-5）
- **知识点标签**：支持按知识点筛选题目
- **智能匹配**：根据学生水平推荐合适题目

---

## 🛠️ 技术栈

### 前端
- **Vue 3** + Composition API
- **Tailwind CSS** - 现代化UI设计
- **Vue Router** - 路由管理
- **WebSocket** - 实时通信

### 后端
- **FastAPI** - 高性能异步Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **WebSocket** - 实时双向通信

### AI集成
- **多模型支持**：OpenAI、Doubao、Ernie、Qwen、Hunyuan、Claude、Gemini
- **统一接口设计**：策略模式实现模型切换
- **自动重试机制**：指数退避重试，提升服务稳定性

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone <repository-url>
cd endgame
```

### 2. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置AI模型API密钥

# 初始化数据库
python init_db.py

# 启动后端服务
python main.py
# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端设置

```bash
cd front

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 4. 使用 Docker Compose（推荐）

```bash
# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 📁 项目结构

```
endgame/
├── backend/                 # 后端服务
│   ├── api/                # API层
│   │   ├── endpoints/      # RESTful API端点
│   │   └── websocket/      # WebSocket端点
│   ├── models/             # 数据模型
│   ├── services/           # 服务层
│   │   ├── ai/            # AI服务
│   │   ├── hint/           # 提示生成服务
│   │   ├── conversation/   # 对话管理
│   │   └── learning/      # 学习跟踪
│   ├── config/            # 配置管理
│   ├── utils/             # 工具函数
│   ├── tests/             # 测试用例
│   ├── main.py            # 应用入口
│   └── requirements.txt   # Python依赖
│
├── front/                  # 前端应用
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   │   ├── Home.vue   # 首页
│   │   │   ├── Answer.vue # 答题页面
│   │   │   └── Analysis.vue # 分析页面
│   │   ├── services/      # 服务层
│   │   │   └── websocket.js # WebSocket服务
│   │   ├── router/        # 路由配置
│   │   └── main.js        # 入口文件
│   └── package.json       # Node依赖
│
├── plan/                   # 项目规划文档
├── docker-compose.yml     # Docker编排配置
└── README.md              # 项目说明文档
```

---

## 🎬 项目演示

### 核心功能流程

1. **选择难度和知识点**
   - 用户从首页选择难度等级（初级/中级/高级）
   - 选择感兴趣的知识点标签

2. **开始答题**
   - 系统随机匹配一道题目
   - 支持LaTeX公式渲染

3. **实时AI提示**
   - 用户输入解题步骤
   - 系统自动分析并生成引导性问题
   - 流式显示AI提示

4. **提交答案**
   - 保存答题记录
   - 跳转到分析页面

5. **查看分析报告**
   - 六维能力雷达图
   - 知识点评分
   - 个性化学习建议

### 演示截图

> 提示：可以添加项目截图或演示视频链接

---

## 🔧 配置说明

### 后端配置（`.env`）

```env
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

# AI模型API密钥（根据选择的模型配置）
DOUBAO_API_KEY=your_doubao_api_key
OPENAI_API_KEY=your_openai_api_key
# ... 其他模型的密钥

# 数据库配置
DATABASE_URL=sqlite:///./app.db
```

### 前端配置

前端默认连接到 `http://localhost:8000`，如需修改，请编辑 `front/src/services/websocket.js`

---

## 📡 API文档

### RESTful API

启动后端服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### WebSocket API

**连接地址**: `ws://localhost:8000/ws`

**消息格式**:
```json
{
  "type": "step",
  "content": "用户的解题步骤"
}
```

**响应格式**:
```json
{
  "type": "hint",
  "content": "AI生成的引导性问题"
}
```

---

## 🧪 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 测试覆盖

- ✅ AI服务测试
- ✅ 苏格拉底式提示测试
- ✅ WebSocket连接测试

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────┐
│   Vue 3     │  前端界面
│   Frontend  │
└──────┬──────┘
       │ WebSocket / HTTP
       │
┌──────▼──────────────────┐
│   FastAPI Backend        │
│  ┌────────────────────┐  │
│  │  WebSocket Server  │  │
│  └──────────┬─────────┘  │
│             │             │
│  ┌──────────▼─────────┐  │
│  │  Hint Service      │  │
│  │  ┌──────────────┐  │  │
│  │  │本地规则引擎  │  │  │
│  │  └──────────────┘  │  │
│  │  ┌──────────────┐  │  │
│  │  │  AI Service   │  │  │
│  │  └──────────────┘  │  │
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │  RESTful API       │  │
│  └──────────┬─────────┘  │
│             │             │
│  ┌──────────▼─────────┐  │
│  │  SQLAlchemy ORM     │  │
│  └──────────┬─────────┘  │
└─────────────┼─────────────┘
              │
       ┌──────▼──────┐
       │  SQLite DB  │
       └─────────────┘
```

### 核心算法

1. **混合提示生成算法**
   ```
   if 本地规则匹配:
       return 规则提示
   else:
       return AI生成提示
   ```

2. **学习能力评估算法**
   - 基于答题记录计算六维能力得分
   - 知识点评分 = 正确率 × 权重

3. **实时交互优化**
   - 防抖机制：用户停止输入800ms后触发
   - 流式响应：分块传输，实时显示

---

## 🎯 核心优势

### 用户价值
- ✅ **解决痛点**：缺乏即时指导、直接给答案、成本高、缺乏个性化
- ✅ **价值创造**：混合智能、实时交互、多维度分析
- ✅ **市场潜力**：5000万目标用户，3000亿市场规模
- ✅ **人文关怀**：苏格拉底式教学，科技向善

### 技术创新
- ✅ **AI原生度**：基于大模型核心能力构建
- ✅ **技术壁垒**：混合智能架构、实时流式交互
- ✅ **创意独特性**："残局"概念、苏格拉底式AI导师

### 完成度
- ✅ **功能完备**：核心流程完整，无明显Bug
- ✅ **用户体验**：UI美观，交互流畅
- ✅ **代码质量**：结构清晰，易于扩展

---

## 📚 相关文档

- [项目演示PPT大纲](./PPT_OUTLINE.md) - PPT演示大纲
- [详细项目介绍](./PROJECT_PRESENTATION.md) - 完整项目介绍文档
- [前后端对接说明](./INTEGRATION.md) - 前后端集成指南
- [后端README](./backend/README.md) - 后端详细文档

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 开发计划

### 功能扩展
- [ ] 支持更多题型（几何证明、函数图像等）
- [ ] 错题本功能
- [ ] 学习路径推荐
- [ ] 社交功能（学习排行榜）

### 技术优化
- [ ] 多模态输入（手写识别、语音输入）
- [ ] 知识图谱构建
- [ ] 个性化推荐算法优化
- [ ] 分布式部署支持

### 市场拓展
- [ ] 扩展到小学、高中阶段
- [ ] 支持其他学科（物理、化学等）
- [ ] 移动端APP开发
- [ ] 教育机构合作

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 👥 作者

**数学残局挑战系统团队**

- 项目维护者：初中数学残局挑战系统团队
- 技术支持：math-challenge-support@example.com

---

## 🙏 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star ⭐**

Made with ❤️ by 数学残局挑战系统团队

</div>
