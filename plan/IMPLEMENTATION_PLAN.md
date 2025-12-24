# 初中数学残局挑战系统 - 实现方案

## 1. 项目概述

本项目旨在实现一个类似象棋残局挑战的初中数学学习系统，重点功能包括苏格拉底式提问引导、学习过程跟踪和AI辅助分析。系统将支持键盘输入公式，提供实时提示，并生成学习报告。

## 2. 技术栈选择

| 组件 | 选型 | 优势 |
|------|------|------|
| 前端框架 | Preact (3KB) | 轻量、快速，兼容React生态 |
| 构建工具 | Vite | 快速的开发体验和构建速度 |
| 公式处理 | MathLive + KaTeX | 支持LaTeX公式输入和渲染 |
| 状态管理 | Zustand (1KB) | 简单、轻量的状态管理方案 |
| PDF生成 | react-pdf | 前端生成PDF报告 |
| 通信协议 | WebSocket | 实时双向通信 |
| 后端服务 | Cloudflare Workers | 无服务器、高可用、低延迟 |
| AI引擎 | GPT-4 Turbo | 强大的数学推理和自然语言处理能力 |

## 3. 项目结构

```
endgame/
├── src/
│   ├── components/          # React组件
│   │   ├── MathEditor.jsx   # MathLive公式编辑器
│   │   ├── VirtualKeyboard.jsx  # 虚拟符号键盘
│   │   ├── SocraticHint.jsx     # 苏格拉底式提问组件
│   │   ├── LearningTracker.jsx  # 学习跟踪组件
│   │   └── ReportGenerator.jsx  # 报告生成组件
│   ├── stores/             # Zustand状态管理
│   │   └── learningStore.js     # 学习数据存储
│   ├── utils/              # 工具函数
│   │   ├── socraticHint.js      # 苏格拉底式提问逻辑
│   │   ├── formulaParser.js     # 公式解析工具
│   │   └── pdfGenerator.js      # PDF生成工具
│   ├── services/           # 服务层
│   │   └── websocket.js         # WebSocket通信服务
│   ├── data/               # 数据
│   │   └── questions.json       # 预置题库
│   ├── App.jsx             # 主应用组件
│   └── main.jsx            # 应用入口
├── public/                 # 静态资源
├── server/                 # 后端代码
│   └── worker.js           # Cloudflare Workers后端
├── package.json
└── vite.config.js
```

## 4. 核心功能实现

### 4.1 基础框架搭建

**功能描述**：创建Preact项目，集成MathLive公式编辑器，添加虚拟键盘。

**实现步骤**：
1. 使用Vite创建Preact项目：`npm create vite@latest . -- --template preact`
2. 安装MathLive和KaTeX：`npm install mathlive katex`
3. 创建MathEditor组件，集成MathLive：
   ```jsx
   import { useRef, useEffect } from 'preact/hooks';
   import 'mathlive/dist/mathlive.min.css';
   import { MathfieldElement } from 'mathlive';
   
   export function MathEditor({ onInput, initialValue }) {
     const mathfieldRef = useRef(null);
     
     useEffect(() => {
       if (mathfieldRef.current) {
         const mathfield = new MathfieldElement();
         mathfieldRef.current.appendChild(mathfield);
         
         if (initialValue) {
           mathfield.value = initialValue;
         }
         
         mathfield.addEventListener('input', (e) => {
           onInput(e.target.value);
         });
         
         return () => {
           mathfield.remove();
         };
       }
     }, []);
     
     return <div ref={mathfieldRef} />;
   }
   ```
4. 创建VirtualKeyboard组件，仅包含±×÷=√∠≈∵∴符号：
   ```jsx
   export function VirtualKeyboard({ onSymbolClick }) {
     const symbols = ['±', '×', '÷', '=', '√', '∠', '≈', '∵', '∴'];
     
     return (
       <div className="virtual-keyboard">
         {symbols.map(symbol => (
           <button 
             key={symbol} 
             onClick={() => onSymbolClick(symbol)}
             className="key"
           >
             {symbol}
           </button>
         ))}
       </div>
     );
   }
   ```

### 4.2 苏格拉底提问引擎

**功能描述**：实现socraticHint函数，输入用户步骤，返回提示问题（最多3层）。

**实现思路**：
1. 采用规则式if-else逻辑，避免复杂的AI推理
2. 针对代数题的常见解题步骤设计提示规则
3. 支持最多3层提示，逐步引导用户思考

**核心代码**：
```javascript
export function socraticHint(userStep, currentProblem) {
  const stepText = userStep.toLowerCase();
  
  // 第一层：基础提示
  if (stepText.includes('设未知数') || stepText.includes('设x为')) {
    return '你为什么选择这个变量？是否有更简洁的设定方式？';
  }
  
  if (stepText.includes('移项')) {
    return '移项时是否考虑了符号变化？';
  }
  
  if (stepText.includes('解方程')) {
    return '你用了什么方法解方程？是否有更简便的方法？';
  }
  
  // 第二层：进阶提示
  if (stepText.includes('合并同类项')) {
    return '你确定所有同类项都合并了吗？再检查一下系数。';
  }
  
  if (stepText.includes('系数化为1')) {
    return '为什么要除以这个系数？是否可以乘以它的倒数？';
  }
  
  // 第三层：深度提示
  if (stepText.includes('检验') || stepText.includes('验证')) {
    return '你是如何验证解的正确性的？是否考虑了所有可能的解？';
  }
  
  if (stepText.includes('辅助线')) {
    return '这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？';
  }
  
  return null; // 无需提示
}
```

### 4.3 学习跟踪与报告

**功能描述**：记录步骤耗时、错误类型、提示触发次数，并生成PDF报告。

**实现思路**：
1. 使用Zustand创建学习数据存储
2. 记录每次用户操作的时间戳和详细信息
3. 使用react-pdf生成单页PDF报告

**核心代码**：

```javascript
// Zustand状态管理
import { create } from 'zustand';

export const useLearningStore = create((set) => ({
  // 当前问题
  currentProblem: null,
  
  // 学习过程数据
  learningData: {
    startTime: null,
    endTime: null,
    steps: [], // { stepText, timestamp, hintUsed, errorType }
    hintCount: 0,
    errorCount: 0,
    timePerStep: []
  },
  
  // 设置当前问题
  setCurrentProblem: (problem) => set({ currentProblem: problem }),
  
  // 开始学习
  startLearning: () => set({
    learningData: {
      ...store.getState().learningData,
      startTime: Date.now()
    }
  }),
  
  // 记录步骤
  addStep: (stepText, hintUsed = false, errorType = null) => set((state) => {
    const prevSteps = state.learningData.steps;
    const prevStepTime = prevSteps.length > 0 ? prevSteps[prevSteps.length - 1].timestamp : state.learningData.startTime;
    const stepTime = Date.now() - prevStepTime;
    
    return {
      learningData: {
        ...state.learningData,
        steps: [
          ...prevSteps,
          { stepText, timestamp: Date.now(), hintUsed, errorType }
        ],
        hintCount: hintUsed ? state.learningData.hintCount + 1 : state.learningData.hintCount,
        errorCount: errorType ? state.learningData.errorCount + 1 : state.learningData.errorCount,
        timePerStep: [...state.learningData.timePerStep, stepTime]
      }
    };
  }),
  
  // 结束学习
  endLearning: () => set((state) => ({
    learningData: {
      ...state.learningData,
      endTime: Date.now()
    }
  }))
}));
```

**PDF报告生成**：

```jsx
// ReportGenerator.jsx
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: { padding: 20 },
  title: { fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  section: { marginBottom: 15 },
  sectionTitle: { fontSize: 14, fontWeight: 'bold', marginBottom: 5 },
  text: { fontSize: 12, marginBottom: 2 }
});

const ReportDocument = ({ learningData }) => {
  // 分析错误类型
  const errorTypes = learningData.steps
    .filter(step => step.errorType)
    .map(step => step.errorType)
    .slice(0, 3); // 取前3个错误点
  
  // 计算平均步骤时间
  const avgStepTime = learningData.timePerStep.reduce((a, b) => a + b, 0) / learningData.timePerStep.length || 0;
  
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <Text style={styles.title}>学习总结报告</Text>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>学习概况</Text>
          <Text style={styles.text}>总耗时: {(learningData.endTime - learningData.startTime) / 1000} 秒</Text>
          <Text style={styles.text}>平均每步耗时: {avgStepTime.toFixed(1)} 秒</Text>
          <Text style={styles.text}>提示使用次数: {learningData.hintCount}</Text>
          <Text style={styles.text}>错误次数: {learningData.errorCount}</Text>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>常见错误点</Text>
          {errorTypes.length > 0 ? (
            errorTypes.map((error, index) => (
              <Text key={index} style={styles.text}>{index + 1}. {error}</Text>
            ))
          ) : (
            <Text style={styles.text}>无明显错误</Text>
          )}
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>推荐练习</Text>
          <Text style={styles.text}>1. 尝试解类似的方程问题，注意符号变化</Text>
        </View>
      </Page>
    </Document>
  );
};

export const ReportGenerator = ({ learningData }) => (
  <PDFDownloadLink document={<ReportDocument learningData={learningData} />} fileName="learning-report.pdf">
    {({ loading }) => loading ? '生成报告中...' : '下载学习报告'}
  </PDFDownloadLink>
);
```

### 4.4 AI集成与通信

**功能描述**：通过WebSocket连接GPT-4 Turbo，实现实时AI辅助。

**实现思路**：
1. 前端通过WebSocket连接Cloudflare Workers
2. Cloudflare Workers作为代理，连接OpenAI API
3. 当用户提交步骤时，发送到后端进行分析并返回提示

**核心代码**：

```javascript
// 前端WebSocket服务
// websocket.js
export class WebSocketService {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.callbacks = {};
  }
  
  connect() {
    this.socket = new WebSocket(this.url);
    
    this.socket.onopen = () => {
      console.log('WebSocket连接已建立');
      if (this.callbacks.onOpen) {
        this.callbacks.onOpen();
      }
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (this.callbacks.onMessage) {
        this.callbacks.onMessage(data);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket连接已关闭');
      if (this.callbacks.onClose) {
        this.callbacks.onClose();
      }
    };
  }
  
  on(event, callback) {
    this.callbacks[event] = callback;
  }
  
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket未连接');
    }
  }
  
  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// 使用示例
// const wsService = new WebSocketService('wss://your-worker.example.com');
// wsService.connect();
// wsService.on('message', (data) => console.log('收到消息:', data));
// wsService.send({ type: 'step', content: '设x为书的价格' });
```

```javascript
// 后端Cloudflare Workers代码
// worker.js
import { OpenAI } from 'openai';

// 配置OpenAI客户端
const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
  baseURL: 'https://api.openai.com/v1'
});

// 处理WebSocket连接
addEventListener('fetch', (event) => {
  if (event.request.headers.get('Upgrade') === 'websocket') {
    handleWebSocket(event);
  } else {
    event.respondWith(new Response('Not found', { status: 404 }));
  }
});

async function handleWebSocket(event) {
  const { 0: client, 1: server } = Object.values(new WebSocketPair());
  
  server.accept();
  
  server.addEventListener('message', async (message) => {
    try {
      const data = JSON.parse(message.data);
      
      if (data.type === 'step') {
        // 调用socraticHint函数或GPT-4 Turbo
        const hint = generateSocraticHint(data.content);
        
        // 如果本地规则没有合适的提示，调用GPT-4 Turbo
        if (!hint) {
          const gptResponse = await openai.chat.completions.create({
            model: 'gpt-4-turbo',
            messages: [
              {
                role: 'system',
                content: '你是一位初中数学老师，使用苏格拉底式提问引导学生思考。针对学生的解题步骤，提出一个引导性问题，不要直接给出答案。'
              },
              {
                role: 'user',
                content: `学生的解题步骤：${data.content}\n请提出一个引导性问题。`
              }
            ],
            max_tokens: 100
          });
          
          server.send(JSON.stringify({
            type: 'hint',
            content: gptResponse.choices[0].message.content
          }));
        } else {
          server.send(JSON.stringify({
            type: 'hint',
            content: hint
          }));
        }
      }
    } catch (error) {
      console.error('Error:', error);
      server.send(JSON.stringify({
        type: 'error',
        content: '发生错误，请稍后再试。'
      }));
    }
  });
  
  server.addEventListener('close', () => {
    console.log('WebSocket连接已关闭');
  });
  
  event.respondWith(new Response(null, {
    status: 101,
    webSocket: client
  }));
}

// 本地苏格拉底式提问规则
function generateSocraticHint(stepContent) {
  // 实现与前端相同的规则
  // ...
  return null;
}
```

## 5. 开发计划

### Day 1: 基础框架搭建
- 创建Vite + Preact项目
- 集成MathLive公式编辑器
- 实现虚拟符号键盘（仅保留±×÷=√∠≈∵∴符号）
- 完成可输入公式的界面

### Day 2: 苏格拉底提问引擎
- 实现socraticHint函数
- 创建实时提示组件
- 测试提问逻辑
- 完成实时提问系统

### Day 3: 学习跟踪与报告
- 实现Zustand学习数据存储
- 记录步骤耗时、错误类型、提示触发次数
- 集成react-pdf生成PDF报告
- 完成学习总结PDF生成器

### Day 4: AI集成与通信
- 搭建WebSocket服务
- 连接GPT-4 Turbo
- 实现用户步骤提交与AI响应逻辑
- 完成全栈联调Demo

### Day 5: 测试与优化
- 运行3个测试用例：
  1. 代数方程求解
  2. 几何证明
  3. 错误处理
- 修复Bug并优化性能
- 代码压缩与部署
- 完成可部署的MVP

## 6. 测试用例

### 测试用例1: 代数方程求解
问题：解方程 2x + 5 = 15
预期用户步骤：
1. 设x为未知数
2. 移项：2x = 15 - 5
3. 计算：2x = 10
4. 系数化为1：x = 5
5. 检验：2×5 + 5 = 15

### 测试用例2: 几何证明
问题：在△ABC中，AB=AC，证明∠B=∠C
预期用户步骤：
1. 作辅助线：作AD⊥BC于D
2. 证明△ABD≌△ACD
3. 得出∠B=∠C

### 测试用例3: 错误处理
问题：解方程 3x - 2 = 7x + 6
预期错误：
1. 移项时符号错误
2. 合并同类项错误
3. 系数化为1时错误

## 7. 部署与优化

### 部署方案
- 前端：Cloudflare Pages
- 后端：Cloudflare Workers
- 静态资源：Cloudflare CDN

### 性能优化
- 使用Preact和Zustand减少JS体积
- 懒加载非核心组件
- 优化MathLive渲染性能
- 压缩和缓存静态资源
- 使用Cloudflare的边缘网络加速

### 扩展性考虑
- 预留OCR手写识别接口
- 支持更多题型（几何、统计等）
- 增加多解法对比功能
- 实现用户认证和进度保存
- 添加竞技模式和排行榜

## 8. 结论

本方案详细描述了初中数学残局挑战系统的实现思路和技术细节，严格按照5天开发周期设计。系统将采用轻量、高效的技术栈，实现核心功能包括公式输入、苏格拉底式提问、学习跟踪和AI辅助分析。通过合理的模块化设计和优化，确保系统的性能和可扩展性。