<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-400 via-purple-500 to-purple-600">
    <!-- 顶部导航 -->
    <nav class="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg border-b border-white border-opacity-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <i class="fas fa-brain text-white text-2xl mr-3"></i>
            <span class="text-white text-xl font-bold">数学残局挑战</span>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-white text-sm">
              <i class="fas fa-clock mr-2"></i>
              <span>{{ formatTime(timer) }}</span>
            </div>
            <div class="text-white text-sm">
              <i class="fas fa-question-circle mr-2"></i>
              题目 <span>{{ questionNumber }}</span> / {{ totalQuestions }}
            </div>
          </div>
        </div>
      </div>
    </nav>

    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- 进度条 -->
        <div class="mb-8">
          <div class="bg-white bg-opacity-20 rounded-full h-2 overflow-hidden">
            <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
          </div>
          <div class="text-white text-sm mt-2 text-center">
            完成进度: {{ progress }}%
          </div>
        </div>

        <!-- 主要答题区域 -->
        <div class="question-card p-8 mb-6">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">数学计算题</h2>
            <p class="text-gray-600">
              {{ levelNames[level] || '初级' }} - {{ knowledgeNames[knowledge] || '代数' }}
            </p>
          </div>

          <!-- 题目显示区 -->
          <div class="math-formula mb-8">
            <div class="text-lg text-gray-700 mb-4">题目：</div>
            <div class="text-3xl font-bold text-gray-900">
              $2(x-3)^2 = 18$
            </div>
            <div class="text-lg text-gray-700 mt-4">求 x 的值</div>
          </div>

          <!-- 答题区域 -->
          <div class="space-y-6">
            <div class="relative">
              <label for="answer-input" class="block text-lg font-semibold text-gray-700 mb-3">
                <i class="fas fa-pencil-alt mr-2 text-blue-500"></i>
                您的答案：
              </label>
              <div class="relative">
                <textarea
                  id="answer-input"
                  v-model="userAnswer"
                  class="answer-input w-full p-4 text-lg resize-none focus:outline-none"
                  rows="4"
                  placeholder="请在此输入您的解题步骤和答案..."
                  @input="handleInput"
                  @focus="showHintSection"
                ></textarea>
                <div 
                  v-if="inlineHint" 
                  class="ai-hint absolute top-4 left-4 pointer-events-none whitespace-pre-wrap"
                >
                  {{ inlineHint }}
                </div>
              </div>
            </div>

            <!-- AI提示区域 -->
            <div v-show="showHint" class="hint-container p-4 rounded-lg">
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                  <i class="fas fa-lightbulb text-yellow-500 text-xl"></i>
                </div>
                <div class="flex-1">
                  <h4 class="font-semibold text-gray-800 mb-2">AI 智能提示</h4>
                  <div class="text-gray-700">
                    <div v-if="isThinking" class="typing-indicator">
                      AI正在分析您的解题思路
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <div v-else>{{ detailedHint }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 连接状态显示 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center text-sm">
                <div 
                  :class="[
                    'pulse-dot w-3 h-3 rounded-full mr-2',
                    connectionStatus === 'connected' ? 'bg-green-500' : 
                    connectionStatus === 'connecting' ? 'bg-yellow-500' : 
                    'bg-red-500'
                  ]"
                ></div>
                <span class="text-gray-600">{{ connectionStatusText }}</span>
              </div>
              <div class="text-sm text-gray-500">
                <i class="fas fa-info-circle mr-1"></i>
                AI会根据您的输入实时提供解题提示
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="flex justify-between items-center">
          <button 
            @click="previousQuestion"
            class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-full transition-all duration-300 transform hover:scale-105"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            上一题
          </button>
          
          <div class="flex space-x-4">
            <button 
              @click="skipQuestion"
              class="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-3 rounded-full transition-all duration-300 transform hover:scale-105"
            >
              <i class="fas fa-forward mr-2"></i>
              跳过此题
            </button>
            <button 
              @click="submitAnswer"
              class="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <i class="fas fa-check mr-2"></i>
              提交答案
            </button>
          </div>

          <button 
            @click="nextQuestion"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-full transition-all duration-300 transform hover:scale-105"
          >
            下一题
            <i class="fas fa-arrow-right ml-2"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import wsService from '../services/websocket.js'

const route = useRoute()

// 从路由获取参数
const level = computed(() => route.query.level || 'beginner')
const knowledge = computed(() => route.query.knowledge || 'algebra')

const levelNames = {
  'beginner': '初级',
  'intermediate': '中级',
  'advanced': '高级'
}

const knowledgeNames = {
  'algebra': '代数',
  'geometry': '几何',
  'statistics': '统计与概率'
}

// 当前题目
const currentQuestion = ref('$2(x-3)^2 = 18$')

// 响应式数据
const timer = ref(15 * 60) // 15分钟
const questionNumber = ref(1)
const totalQuestions = ref(10)
const userAnswer = ref('')
const inlineHint = ref('')
const detailedHint = ref('')
const showHint = ref(false)
const isThinking = ref(false)
const connectionStatus = ref('connecting') // 'connecting' | 'connected' | 'error'
const inputTimer = ref(null)
const aiResponseBuffer = ref('') // 用于累积流式响应

// 计算属性
const progress = computed(() => {
  return Math.round((questionNumber.value / totalQuestions.value) * 100)
})

const connectionStatusText = computed(() => {
  switch (connectionStatus.value) {
    case 'connected':
      return 'AI助手已连接'
    case 'connecting':
      return '正在连接AI助手...'
    case 'error':
      return 'AI助手连接失败'
    default:
      return 'AI助手已连接'
  }
})

// 格式化时间
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// WebSocket 连接
const connectWebSocket = async () => {
  try {
    connectionStatus.value = 'connecting'
    
    // 设置事件监听
    wsService.on('open', () => {
      connectionStatus.value = 'connected'
      console.log('WebSocket 连接成功')
      // 显示初始提示
      if (userAnswer.value.trim() === '') {
        inlineHint.value = '提示：这是一个二次方程，考虑开平方根...'
      }
    })
    
    wsService.on('close', () => {
      if (connectionStatus.value === 'connected') {
        connectionStatus.value = 'error'
      }
    })
    
    wsService.on('error', (data) => {
      console.error('WebSocket 错误:', data)
      connectionStatus.value = 'error'
    })
    
    wsService.on('status', (data) => {
      isThinking.value = true
      showHint.value = true
      detailedHint.value = data.message || '正在处理您的请求...'
    })
    
    wsService.on('ai_response_start', () => {
      isThinking.value = false
      aiResponseBuffer.value = ''
      detailedHint.value = ''
    })
    
    wsService.on('ai_response_chunk', (data) => {
      aiResponseBuffer.value += data.content || ''
      // 实时更新详细提示
      detailedHint.value = aiResponseBuffer.value
      showHint.value = true
    })
    
    wsService.on('ai_response_end', () => {
      // 解析 AI 响应，提取内联提示和详细提示
      parseAIResponse(aiResponseBuffer.value)
      aiResponseBuffer.value = ''
    })
    
    // 连接 WebSocket
    await wsService.connect()
  } catch (error) {
    console.error('WebSocket连接失败:', error)
    connectionStatus.value = 'error'
  }
}

// 解析 AI 响应
const parseAIResponse = (response) => {
  // 尝试从 AI 响应中提取提示
  // 如果 AI 返回的是结构化内容，可以解析
  // 否则使用整个响应作为详细提示
  
  // 简单的解析逻辑：查找内联提示和详细提示
  const lines = response.split('\n')
  let inline = ''
  let detailed = response
  
  // 查找简短提示（通常在第一行或包含"提示"的行）
  for (const line of lines) {
    if (line.length < 50 && (line.includes('提示') || line.includes('建议'))) {
      inline = line.trim()
      break
    }
  }
  
  // 如果没有找到简短提示，使用前50个字符
  if (!inline && response.length > 0) {
    inline = response.substring(0, 50) + (response.length > 50 ? '...' : '')
  }
  
  inlineHint.value = inline || 'AI 正在思考...'
  detailedHint.value = detailed || response
}

// 处理输入
const handleInput = () => {
  clearTimeout(inputTimer.value)
  inputTimer.value = setTimeout(() => {
    requestHint()
  }, 800) // 用户停止输入800ms后请求提示
}

// 请求AI提示
const requestHint = () => {
  const input = userAnswer.value.trim()
  if (!wsService.isConnected()) {
    // 如果未连接，使用本地提示作为后备
    if (input) {
      const hints = generateContextualHints(input)
      displayHint(hints.inlineHint, hints.detailedHint)
    }
    return
  }
  
  // 显示思考状态
  isThinking.value = true
  showHint.value = true
  
  // 发送请求到后端
  wsService.sendChatMessage(input, currentQuestion.value)
}

// 生成上下文提示
const generateContextualHints = (input) => {
  const inputLower = input.toLowerCase()
  
  if (inputLower.includes('x') && inputLower.includes('=')) {
    return {
      inlineHint: '很好！你在求解x的值...',
      detailedHint: '✅ 正确的思路！继续完成计算步骤。记住要检查两个解。'
    }
  } else if (inputLower.includes('2') || inputLower.includes('18')) {
    return {
      inlineHint: '需要先简化方程...',
      detailedHint: '💡 提示：首先将方程两边同时除以2，得到 (x-3)² = 9'
    }
  } else if (inputLower.includes('±') || inputLower.includes('正负')) {
    return {
      inlineHint: '注意平方根有正负两个值...',
      detailedHint: '🎯 很好！开平方根确实要考虑正负号。x-3 = ±3'
    }
  } else if (input.length > 0) {
    return {
      inlineHint: '试试从左边开始化简...',
      detailedHint: '🤔 建议先化简左边的表达式。这是一个关于(x-3)的二次方程。'
    }
  } else {
    return {
      inlineHint: '开始解这个二次方程...',
      detailedHint: '📚 这是一个二次方程，建议先化简，然后开平方根求解。'
    }
  }
}

// 显示提示
const displayHint = (inline, detailed) => {
  inlineHint.value = inline
  detailedHint.value = detailed
  isThinking.value = false
  showHint.value = true
}

// 显示提示区域
const showHintSection = () => {
  showHint.value = true
}

// 启动计时器
let timerInterval = null
const startTimer = () => {
  timerInterval = setInterval(() => {
    if (timer.value <= 0) {
      clearInterval(timerInterval)
      handleTimeUp()
      return
    }
    timer.value--
  }, 1000)
}

// 时间到处理
const handleTimeUp = () => {
  alert('时间到！系统将自动提交您的答案。')
  submitAnswer()
}

// 提交答案
const submitAnswer = () => {
  if (!userAnswer.value.trim()) {
    alert('请输入您的答案再提交。')
    return
  }
  
  console.log('提交答案:', userAnswer.value)
  alert('答案已提交！即将进入下一题。')
  nextQuestion()
}

// 跳过题目
const skipQuestion = () => {
  if (confirm('确定要跳过这道题吗？')) {
    nextQuestion()
  }
}

// 下一题
const nextQuestion = () => {
  if (questionNumber.value < totalQuestions.value) {
    questionNumber.value++
    userAnswer.value = ''
    inlineHint.value = ''
    detailedHint.value = ''
    showHint.value = false
    isThinking.value = false
  } else {
    alert('恭喜！您已完成所有题目。')
  }
}

// 上一题
const previousQuestion = () => {
  if (questionNumber.value > 1) {
    questionNumber.value--
    userAnswer.value = ''
    inlineHint.value = ''
    detailedHint.value = ''
    showHint.value = false
    isThinking.value = false
  }
}

// 生命周期
onMounted(() => {
  connectWebSocket()
  startTimer()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  if (inputTimer.value) {
    clearTimeout(inputTimer.value)
  }
  // 断开 WebSocket 连接
  wsService.disconnect()
})
</script>

<style scoped>
        .question-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .question-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        }
        
        .answer-input {
            background: linear-gradient(145deg, #f8faff, #e8ecf7);
            border: 2px solid transparent;
            border-radius: 15px;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .answer-input:focus {
            background: white;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .ai-hint {
            color: #9ca3af;
            font-style: italic;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }
        
        .hint-container {
            background: linear-gradient(145deg, #f0f4ff, #e0e7ff);
            border-left: 4px solid #667eea;
            border-radius: 0 10px 10px 0;
        }
        
        .pulse-dot {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }
        
        .typing-indicator {
            display: inline-flex;
            align-items: center;
        }
        
        .typing-indicator span {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            background-color: #667eea;
            margin: 0 2px;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
            30% { transform: scale(1.2); opacity: 1; }
        }
        
        .progress-bar {
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            height: 8px;
            transition: width 0.3s ease;
        }
        
        .math-formula {
            font-family: 'Noto Serif SC', serif;
            font-size: 1.8rem;
            color: #1f2937;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(145deg, #ffffff, #f8faff);
            border-radius: 15px;
            border: 2px solid #e5e7eb;
        }
    </style>
