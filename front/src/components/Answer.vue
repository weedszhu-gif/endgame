<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-400 via-purple-500 to-purple-600">
    <!-- 页面标题栏 -->
    <div class="page-header bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg border-b border-white border-opacity-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="goHome"
              class="text-white hover:text-yellow-200 transition-colors"
              title="返回主页"
            >
              <i class="fas fa-home text-xl"></i>
            </button>
            <div class="flex items-center">
              <i class="fas fa-brain text-white text-2xl mr-3"></i>
              <span class="text-white text-xl font-bold">数学残局挑战</span>
            </div>
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
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">

        <!-- 主要答题区域 -->
        <div class="question-card p-8 mb-6">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">数学计算题</h2>
            <p class="text-gray-600">
              {{ levelNames[level] || '初级' }}
              <span v-if="questionTags.length > 0" class="ml-2">
                - {{ questionTags.join('、') }}
              </span>
            </p>
          </div>

          <!-- 题目显示区 -->
          <div class="question-display mb-8" v-if="currentQuestion">
            <div class="text-lg text-gray-700 mb-4 font-semibold">题目：</div>
            <div class="question-content" ref="questionDisplay" v-html="renderedQuestion || currentQuestion">
            </div>
          </div>
          <div v-else class="text-center py-8">
            <div class="text-gray-500">正在加载题目...</div>
          </div>

          <!-- 答题区域 -->
          <div class="space-y-6">
            <div class="relative">
              <label for="answer-input" class="block text-lg font-semibold text-gray-700 mb-3" @click="focusMathField">
                <i class="fas fa-pencil-alt mr-2 text-blue-500"></i>
                您的答案：
              </label>
              <!-- MathLive 公式编辑器 -->
              <div class="mathlive-container">
                <div class="math-field-container" @click="focusMathField">
                  <math-field
                id="answer-input"
                    ref="mathField"
                    default-mode="math"
                    :readonly="false"
                    tabindex="0"
                    placeholder="请在此输入您的解题步骤和答案...（支持回车换行、空格，Alt+1输入∵，Alt+2输入∴）"
                  ></math-field>
                </div>
              </div>
              <!-- 虚拟键盘切换按钮 -->
              <div class="keyboard-toggle-container">
                <button
                  @click="toggleKeyboard"
                  class="keyboard-toggle-btn"
                  :class="{ active: showKeyboard }"
                  title="打开/关闭数学符号键盘"
                >
                  <i class="fas fa-keyboard mr-2"></i>
                  {{ showKeyboard ? '关闭键盘' : '打开键盘' }}
                </button>
              </div>
              <!-- 弹出式虚拟键盘 -->
              <VirtualKeyboard 
                :visible="showKeyboard"
                @update:visible="showKeyboard = $event"
                @symbol-click="insertSymbol" 
              />
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
                    <div v-else>
                      <div class="hint-content" v-html="renderedHint"></div>
                      <!-- 反馈按钮 -->
                      <div v-if="currentHintMetadata" class="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200">
                        <span class="text-sm text-gray-600">这个提示对您有帮助吗？</span>
                        <button
                          @click="submitFeedback(1)"
                          class="px-3 py-1 text-sm rounded-lg transition-colors"
                          :class="hintFeedback === 1 ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-green-100'"
                          title="赞"
                        >
                          <i class="fas fa-thumbs-up"></i> 赞
                        </button>
                        <button
                          @click="submitFeedback(2)"
                          class="px-3 py-1 text-sm rounded-lg transition-colors"
                          :class="hintFeedback === 2 ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-red-100'"
                          title="踩"
                        >
                          <i class="fas fa-thumbs-down"></i> 踩
                        </button>
                      </div>
                    </div>
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
        <div class="flex justify-center items-center space-x-4">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import wsService from '../services/websocket.js'
import VirtualKeyboard from './VirtualKeyboard.vue'
import katex from 'katex'
import 'katex/dist/katex.css'
import { useUser } from '../composables/useUser'

const route = useRoute()
const router = useRouter()
const { currentUser } = useUser()

// 从路由获取参数
const level = computed(() => route.query.level || 'beginner')
const selectedTag = computed(() => route.query.tag || '')
const questionIdFromRoute = computed(() => {
  // 支持 questionId 和 question_id 两种参数名
  return route.query.questionId || route.query.question_id || null
})

const levelNames = {
  'beginner': '初级',
  'intermediate': '中级',
  'advanced': '高级'
}

// 难度映射到数据库难度值
const difficultyMap = {
  'beginner': 1,    // 初级：难度1-2
  'intermediate': 2, // 中级：难度3
  'advanced': 3     // 高级：难度4-5
}

// 返回主页
const goHome = () => {
  router.push('/')
}

// 当前题目
const currentQuestion = ref(null)
const currentQuestionId = ref(null)
const questionTags = ref([])
const questionSolution = ref('')

// 响应式数据
const timer = ref(15 * 60) // 15分钟
const questionNumber = ref(1)
const totalQuestions = ref(1) // 仅保留1道题目做测试
const userAnswer = ref('')
const detailedHint = ref('')
const showHint = ref(false)
const isThinking = ref(false)
const connectionStatus = ref('connecting') // 'connecting' | 'connected' | 'error'
const inputTimer = ref(null)
const aiResponseBuffer = ref('') // 用于累积流式响应
const mathField = ref(null)
const questionDisplay = ref(null)
const renderedQuestion = ref('')
const showKeyboard = ref(false)
const hintCount = ref(0) // 提示使用次数
const currentHintMetadata = ref(null) // 当前提示的元数据（用于反馈）
const hintFeedback = ref(0) // 当前提示的反馈状态：0=未反馈，1=赞，2=踩

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

// 渲染 AI 提示中的数学公式
const renderedHint = computed(() => {
  return renderMathContent(detailedHint.value)
})

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
        detailedHint.value = '📚 请开始输入您的解题步骤，我会根据您的输入提供相应的提示'
        showHint.value = true
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
      // 如果AI返回了有效提示，增加提示次数
      if (aiResponseBuffer.value && aiResponseBuffer.value.trim() && !aiResponseBuffer.value.includes('请开始输入')) {
        hintCount.value++
      }
      aiResponseBuffer.value = ''
    })
    
    // 监听 hint 消息（后端直接返回的提示）
    wsService.on('hint', (data) => {
      isThinking.value = false
      detailedHint.value = data.content || '暂无提示'
      showHint.value = true
      // 保存提示元数据（用于反馈）
      currentHintMetadata.value = data.metadata || null
      hintFeedback.value = 0 // 重置反馈状态
      // 增加提示次数（只有当提示内容不为空且不是初始提示时才计数）
      if (data.content && data.content.trim() && !data.content.includes('请开始输入')) {
        hintCount.value++
      }
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
  // 将所有 AI 响应都放到详细提示区域
  detailedHint.value = response || 'AI 正在思考...'
}

// 处理 MathLive 输入
const handleMathInput = (event) => {
  if (mathField.value) {
    userAnswer.value = mathField.value.getValue()
  }
  clearTimeout(inputTimer.value)
  inputTimer.value = setTimeout(() => {
    requestHint()
  }, 800) // 用户停止输入800ms后请求提示
}

// 切换虚拟键盘显示
const toggleKeyboard = () => {
  showKeyboard.value = !showKeyboard.value
}

// 聚焦到 MathLive 编辑器
const focusMathField = () => {
  if (mathField.value) {
    try {
      // 直接聚焦
      mathField.value.focus()
      
      // 使用 requestAnimationFrame 确保 DOM 已更新后再次聚焦
      requestAnimationFrame(() => {
        if (mathField.value) {
          try {
            mathField.value.focus()
          } catch (e) {
            console.warn('requestAnimationFrame 聚焦失败:', e)
          }
        }
      })
    } catch (error) {
      console.warn('聚焦 MathLive 编辑器失败:', error)
    }
  } else {
    // 如果 ref 还没有准备好，延迟重试
    setTimeout(() => {
      if (mathField.value) {
        focusMathField()
      }
    }, 100)
  }
}

// 插入符号到 MathLive 编辑器（支持更多符号和功能）
const insertSymbol = (item) => {
  if (!mathField.value) return
  
  try {
    // 处理功能键
    if (item && item.type === 'action') {
      handleAction(item.action)
      return
    }
    
    // 处理符号（兼容旧格式和新格式）
    const symbol = item?.symbol || item
    const symbolMap = {
      // 基础运算符
      '±': '\\pm ',
      '×': '\\times ',
      '÷': '\\div ',
      '·': '\\cdot ',
      '=': '=',
      '+': '+',
      '-': '-',
      '*': '\\times ',
      '/': '\\div ',
      
      // 关系符号
      '≠': '\\neq ',
      '≈': '\\approx ',
      '≤': '\\leq ',
      '≥': '\\geq ',
      '<': '<',
      '>': '>',
      '≪': '\\ll ',
      '≫': '\\gg ',
      '≡': '\\equiv ',
      '∝': '\\propto ',
      '∈': '\\in ',
      
      // 函数和特殊符号
      '√': '\\sqrt',
      '∛': '\\sqrt[3]',
      '∑': '\\sum ',
      '∏': '\\prod ',
      '∫': '\\int ',
      '∂': '\\partial ',
      '∠': '\\angle ',
      '°': '^\\circ ',
      'π': '\\pi ',
      '∞': '\\infty ',
      '∵': '\\because ',
      '∴': '\\therefore ',
      
      // 希腊字母
      'α': '\\alpha ',
      'β': '\\beta ',
      'γ': '\\gamma ',
      'δ': '\\delta ',
      'ε': '\\epsilon ',
      'θ': '\\theta ',
      'λ': '\\lambda ',
      'μ': '\\mu ',
      'ρ': '\\rho ',
      'σ': '\\sigma ',
      'φ': '\\phi ',
      'ω': '\\omega ',
      
      // 函数
      'sin': '\\sin ',
      'cos': '\\cos ',
      'tan': '\\tan ',
      'log': '\\log ',
      'ln': '\\ln ',
      'lim': '\\lim '
    }
    
    const latexCommand = symbolMap[symbol] || symbol
    
    // 特殊处理
    if (symbol === '√') {
      mathField.value.insert('\\sqrt{')
      setTimeout(() => {
        if (mathField.value) {
          mathField.value.executeCommand('moveToNextChar')
        }
      }, 10)
    } else if (symbol === '∛') {
      mathField.value.insert('\\sqrt[3]{')
      setTimeout(() => {
        if (mathField.value) {
          mathField.value.executeCommand('moveToNextChar')
        }
      }, 10)
    } else if (symbol === '^') {
      // 处理 ^ 符号，插入上标结构 ^{}
      mathField.value.insert('^{}')
      setTimeout(() => {
        if (mathField.value) {
          mathField.value.executeCommand('moveToNextChar')
        }
      }, 10)
    } else {
      mathField.value.insert(latexCommand)
    }
    
    // 聚焦并更新
    mathField.value.focus()
    userAnswer.value = mathField.value.getValue()
    handleMathInput()
    
  } catch (error) {
    console.error('插入符号失败:', error)
  }
}

// 处理功能键
const handleAction = (action) => {
  if (!mathField.value) return
  
  try {
    switch (action) {
      case 'newline':
        // 换行（在 MathLive 中，换行用 \\）
        mathField.value.insert('\\\\')
        userAnswer.value = mathField.value.getValue()
        handleMathInput()
        break
      
      case 'backspace':
        // 退格
        mathField.value.executeCommand('deleteBackward')
        userAnswer.value = mathField.value.getValue()
        handleMathInput()
        break
      
      case 'space':
        // 空格（MathLive 支持直接输入空格）
        mathField.value.insert(' ')
        userAnswer.value = mathField.value.getValue()
        handleMathInput()
        break
      
      case 'clear':
        // 清空
        mathField.value.setValue('')
        userAnswer.value = ''
        break
      
      case 'left':
        // 左移光标
        mathField.value.executeCommand('moveToPreviousChar')
        break
      
      case 'right':
        // 右移光标
        mathField.value.executeCommand('moveToNextChar')
        break
      
      case 'fraction':
        // 分数
        mathField.value.insert('\\frac{}{}')
        setTimeout(() => {
          if (mathField.value) {
            mathField.value.executeCommand('moveToPreviousChar')
          }
        }, 10)
        break
      
      case 'power':
        // 次方（x^y 形式）
        // 插入 x^{y} 模板，用户可以直接编辑底数和指数
        mathField.value.insert('x^{y}')
        // 将光标定位在 x 之后，方便用户直接输入底数
        setTimeout(() => {
          if (mathField.value) {
            try {
              // 尝试将光标移到 x 之后（在 ^ 之前）
              // 由于 MathLive 的内部结构，我们使用 moveToNextChar 来移动
              mathField.value.executeCommand('moveToMathFieldStart')
              // 向右移动，跳过 x，到达 ^ 之前
              mathField.value.executeCommand('moveToNextChar')
            } catch (e) {
              console.warn('移动光标失败:', e)
            }
          }
        }, 50)
        break
      
      case 'superscript':
        // 上标
        mathField.value.insert('^{}')
        setTimeout(() => {
          if (mathField.value) {
            mathField.value.executeCommand('moveToNextChar')
          }
        }, 10)
        break
      
      case 'subscript':
        // 下标
        mathField.value.insert('_{}')
        setTimeout(() => {
          if (mathField.value) {
            mathField.value.executeCommand('moveToNextChar')
          }
        }, 10)
        break
    }
    
    mathField.value.focus()
    userAnswer.value = mathField.value.getValue()
    handleMathInput()
    
  } catch (error) {
    console.error('执行功能键失败:', error)
  }
}

// 处理输入（保留作为后备）
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
      const hint = generateContextualHints(input)
      displayHint(hint)
    }
    return
  }
  
  // 显示思考状态
  isThinking.value = true
  showHint.value = true
  
  // 发送请求到后端
  if (currentQuestion.value) {
    wsService.sendChatMessage(input, currentQuestion.value)
  }
}

// 通用提示规则配置（参考后端 socratic_hint.py）
const hintRules = [
  // 第一层：具体操作提示
  {
    keywords: ['配方法', '配方'],
    hint: '💡 配方过程中是否注意了常数项的处理？'
  },
  {
    keywords: ['因式分解', '分解因式'],
    hint: '💡 你用了什么因式分解方法？是否有其他分解方式？'
  },
  {
    keywords: ['合并同类项'],
    hint: '💡 你确定所有同类项都合并了吗？再检查一下系数。'
  },
  {
    keywords: ['系数化为1', '除以'],
    hint: '💡 为什么要除以这个系数？是否可以乘以它的倒数？'
  },
  {
    keywords: ['辅助线', '作线'],
    hint: '💡 这条辅助线如何帮助你证明结论？是否还有其他可能的辅助线？'
  },
  {
    keywords: ['相似', '全等'],
    hint: '💡 你是如何证明相似/全等的？是否符合相应的判定定理？'
  },
  {
    keywords: ['勾股定理', '毕达哥拉斯'],
    hint: '💡 你确定这个三角形是直角三角形吗？有没有其他方法可以验证？'
  },
  {
    keywords: ['面积', '体积'],
    hint: '💡 你使用了什么面积/体积公式？是否适用于当前图形？'
  },
  {
    keywords: ['函数', '图像'],
    hint: '💡 这个函数的定义域和值域是什么？图像有什么特征？'
  },
  {
    keywords: ['不等式', '不等'],
    hint: '💡 解不等式时是否注意了不等号的方向变化？'
  },
  {
    keywords: ['顶点', '坐标', '对称轴'],
    hint: '💡 提示：二次函数 $y=ax^2+bx+c$ 的顶点坐标公式为 $\\left(-\\frac{b}{2a}, \\frac{4ac-b^2}{4a}\\right)$'
  },
  {
    keywords: ['开方', '平方', '根', '√'],
    hint: '💡 注意：方程 $x^2=k$ 的解为 $x=\\pm\\sqrt{k}$，需考虑正负两种情况'
  },
  {
    keywords: ['移项'],
    hint: '💡 移项时是否考虑了符号变化？'
  },
  {
    keywords: ['解方程'],
    hint: '💡 你用了什么方法解方程？是否有更简便的方法？'
  },
  {
    keywords: ['检验', '验证'],
    hint: '💡 你是如何验证解的正确性的？是否考虑了所有可能的解？'
  },
  {
    keywords: ['设未知数', '设x', '假设'],
    hint: '💡 你为什么选择这个变量？是否有更简洁的设定方式？'
  },
  {
    keywords: ['计算', '算'],
    hint: '💡 你确定计算过程正确吗？可以再检查一遍吗？'
  },
  // 第二层：通用数学概念
  {
    keywords: ['二次', '二次方程', 'quadratic'],
    hint: '💡 二次方程通常可以通过因式分解、配方法或公式法求解。'
  },
  {
    keywords: ['一次', '一次方程', 'linear'],
    hint: '💡 一次方程可以通过移项和合并同类项来求解。'
  },
  {
    keywords: ['三角形', 'triangle'],
    hint: '💡 考虑三角形的性质和定理，如内角和、外角、相似性等。'
  },
  {
    keywords: ['圆', 'circle'],
    hint: '💡 考虑圆的性质，如圆心角、圆周角、切线等。'
  },
  {
    keywords: ['平行四边形', 'parallelogram'],
    hint: '💡 利用平行四边形的性质：对边平行且相等，对角线互相平分。'
  }
]

// 生成通用上下文提示（作为 WebSocket 未连接时的后备方案）
const generateContextualHints = (input) => {
  if (!input || input.trim().length === 0) {
    return '📚 请开始输入您的解题步骤，我会根据您的输入提供相应的提示。'
  }
  
  const inputLower = input.toLowerCase()
  
  // 按优先级匹配规则（更具体的规则优先）
  for (const rule of hintRules) {
    const matched = rule.keywords.some(keyword => {
      // 支持部分匹配和完整匹配
      return inputLower.includes(keyword.toLowerCase())
    })
    
    if (matched) {
      return rule.hint
    }
  }
  
  // 如果没有匹配到具体规则，提供通用提示
  if (inputLower.includes('=')) {
    return '✅ 你正在解方程，继续完成计算步骤。记得检查解的正确性。'
  } else if (inputLower.includes('x') || inputLower.includes('y')) {
    return '💡 你使用了变量，考虑如何建立方程或关系式。'
  } else if (input.length > 10) {
    return '💡 你已经输入了一些步骤，继续思考下一步该怎么做。'
  } else {
    return '💡 请继续输入您的解题思路，我会根据您的步骤提供相应的提示。'
  }
}

// 显示提示
const displayHint = (hint) => {
  detailedHint.value = hint
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
const submitAnswer = async () => {
  if (!userAnswer.value.trim()) {
    alert('请输入您的答案再提交。')
    return
  }
  
  try {
    // 保存答题记录到后端
    const response = await fetch('http://localhost:8000/api/answer-records', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: currentUser.value?.id || null,
        question_id: currentQuestionId.value,
        student_input: userAnswer.value,
        level: level.value,
        tag: selectedTag.value,
        time_spent: 15 * 60 - timer.value,
        hint_count: hintCount.value
      })
    })
    
    if (!response.ok) {
      throw new Error('保存答题记录失败')
    }
    
    // 跳转到分析页面
    router.push({
      path: '/analysis',
      query: {
        question_id: currentQuestionId.value,
        level: level.value,
        tag: selectedTag.value
      }
    })
  } catch (error) {
    console.error('提交答案失败:', error)
    alert('提交失败，请重试。')
  }
}

// 跳过题目
const skipQuestion = () => {
  if (confirm('确定要跳过这道题吗？')) {
    goHome()
  }
}

// 提交提示反馈（赞/踩）
const submitFeedback = async (feedbackType) => {
  if (!currentHintMetadata.value) {
    return
  }
  
  // 如果已经反馈过，先取消之前的反馈
  if (hintFeedback.value === feedbackType) {
    hintFeedback.value = 0
    return
  }
  
  hintFeedback.value = feedbackType
  
  try {
    const response = await fetch('http://localhost:8000/api/hint-feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: currentUser.value?.id || null,
        question_id: currentQuestionId.value || currentHintMetadata.value.question_id,
        student_input: userAnswer.value,
        hint_content: detailedHint.value,
        feedback_type: feedbackType,
        hint_source: currentHintMetadata.value.source || null,
        hint_keyword: currentHintMetadata.value.keyword || null,
      })
    })
    
    if (!response.ok) {
      throw new Error('提交反馈失败')
    }
    
    console.log('反馈提交成功')
  } catch (error) {
    console.error('提交反馈失败:', error)
    hintFeedback.value = 0 // 恢复状态
  }
}

// 使用 KaTeX 渲染数学公式
const renderMathContent = (content) => {
  if (!content) return ''
  
  try {
    // 先提取所有公式，用占位符替换，避免转义时破坏公式和中文
    const formulaPlaceholders = []
    let placeholderIndex = 0
    
    // 处理块级公式 $$...$$
    let processed = content.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
      const placeholder = `__BLOCK_FORMULA_${placeholderIndex}__`
      formulaPlaceholders.push({ type: 'block', formula: formula.trim(), placeholder })
      placeholderIndex++
      return placeholder
    })
    
    // 处理行内公式 $...$（避免嵌套的 $，只匹配数学表达式）
    processed = processed.replace(/(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)/g, (match, formula) => {
      // 只处理看起来像数学公式的内容（包含字母、数字、运算符等）
      if (/[a-zA-Z0-9+\-*/^_=<>()\[\]{}\\]/.test(formula)) {
        const placeholder = `__INLINE_FORMULA_${placeholderIndex}__`
        formulaPlaceholders.push({ type: 'inline', formula: formula.trim(), placeholder })
        placeholderIndex++
        return placeholder
      }
      return match // 如果不是公式，保持原样
    })
    
    // 转义 HTML 特殊字符（保护占位符和中文）
    let rendered = processed
      .replace(/&(?!__[A-Z_]+_\d+__|amp;|lt;|gt;)/g, '&amp;')
      .replace(/<(?!__[A-Z_]+_\d+__|br|span|div)/g, '&lt;')
      .replace(/(?<!__[A-Z_]+_\d+__)>/g, '&gt;')
    
    // 恢复公式并渲染
    formulaPlaceholders.forEach(({ type, formula, placeholder }) => {
      try {
        const formulaHtml = katex.renderToString(formula, { 
          displayMode: type === 'block', 
          throwOnError: false,
          strict: false
        })
        rendered = rendered.replace(placeholder, formulaHtml)
      } catch (e) {
        console.warn(`KaTeX 渲染${type === 'block' ? '块级' : '行内'}公式失败:`, formula, e)
        const errorDisplay = type === 'block' ? `$$${formula}$$` : `$${formula}$`
        rendered = rendered.replace(placeholder, `<span class="math-error">${errorDisplay}</span>`)
      }
    })
    
    // 处理换行，保持格式
    rendered = rendered.replace(/\n/g, '<br>')
    
    return rendered
  } catch (e) {
    console.error('渲染数学公式失败:', e)
    // 如果渲染失败，至少显示原始内容（只转义 HTML 标签，保护中文）
    return content
      .replace(/&(?![a-zA-Z]+;)/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')
  }
}

// 格式化数学内容（处理LaTeX）- 保留作为后备
const formatMathContent = (content) => {
  return renderMathContent(content)
}

// 从API获取题目
const fetchQuestion = async () => {
  try {
    // 重置提示次数
    hintCount.value = 0
    
    // 如果路由参数中指定了题目ID，直接获取该题目
    if (questionIdFromRoute.value) {
      const questionId = parseInt(questionIdFromRoute.value)
      const response = await fetch(`http://localhost:8000/api/questions/${questionId}`)
      
      if (response.ok) {
        const question = await response.json()
        currentQuestion.value = question.content
        currentQuestionId.value = question.id
        questionTags.value = question.tags || []
        questionSolution.value = question.solution || ''
        
        // 立即渲染题目中的数学公式
        renderedQuestion.value = renderMathContent(currentQuestion.value)
        return
      } else {
        console.warn(`题目 ${questionId} 不存在，将使用随机题目`)
      }
    }
    
    // 如果没有指定题目ID或获取失败，使用原来的逻辑（根据难度和标签随机选择）
    const difficulty = difficultyMap[level.value] || 1
    let apiUrl = `http://localhost:8000/api/questions?difficulty=${difficulty}&limit=100`
    
    // 如果选择了标签，添加标签过滤
    if (selectedTag.value) {
      apiUrl += `&tags=${encodeURIComponent(selectedTag.value)}`
    }
    
    const response = await fetch(apiUrl)
    if (!response.ok) {
      throw new Error('获取题目失败')
    }
    
    const data = await response.json()
    if (data.questions && data.questions.length > 0) {
      // 随机选择一道题目
      const randomIndex = Math.floor(Math.random() * data.questions.length)
      const question = data.questions[randomIndex]
      currentQuestion.value = question.content
      currentQuestionId.value = question.id
      questionTags.value = question.tags || []
      questionSolution.value = question.solution || ''
      
      // 立即渲染题目中的数学公式
      renderedQuestion.value = renderMathContent(currentQuestion.value)
    } else {
      // 如果没有题目，使用默认题目
      currentQuestion.value = '$2(x-3)^2 = 18$\n求 x 的值'
      questionTags.value = []
      renderedQuestion.value = renderMathContent(currentQuestion.value)
    }
  } catch (error) {
    console.error('获取题目失败:', error)
    // 使用默认题目作为后备
    currentQuestion.value = '$2(x-3)^2 = 18$\n求 x 的值'
    questionTags.value = []
    renderedQuestion.value = renderMathContent(currentQuestion.value)
  }
}

// 监听题目变化，自动渲染
watch(currentQuestion, (newQuestion) => {
  if (newQuestion) {
    renderedQuestion.value = renderMathContent(newQuestion)
  }
}, { immediate: true })

// 监听 userAnswer 变化，同步到 MathLive（仅用于外部更新，避免循环）
let isUpdatingFromMathField = false
watch(userAnswer, (newValue) => {
  if (!isUpdatingFromMathField && mathField.value) {
    const currentValue = mathField.value.getValue()
    if (currentValue !== newValue) {
      try {
        mathField.value.setValue(newValue || '', { suppressChangeNotifications: true })
      } catch (error) {
        console.warn('更新 MathLive 值失败:', error)
      }
    }
  }
})

// 监听路由参数变化，当 questionId 变化时重新加载题目
watch(questionIdFromRoute, (newQuestionId, oldQuestionId) => {
  if (newQuestionId && newQuestionId !== oldQuestionId) {
    fetchQuestion()
  }
})

// 生命周期
onMounted(async () => {
  await fetchQuestion()
  connectWebSocket()
  startTimer()
  
  // 等待 MathLive 初始化后设置编辑器
  nextTick(() => {
    setTimeout(() => {
      if (mathField.value) {
        try {
          // 配置 MathLive 选项
          mathField.value.setOptions({
            virtualKeyboardMode: 'manual',
            virtualKeyboards: '',
            smartFence: true,
            smartSuperscript: true,
            removeExtraneousParentheses: true,
            defaultMode: 'math',
            readOnly: false,
            // 允许换行和空格
            plonkSound: null,
            keypressSound: null,
            // 允许输入空格和换行
            removeExtraneousParentheses: true
          })
          
          // 确保编辑器处于可编辑状态
          if (mathField.value.setReadOnly) {
            mathField.value.setReadOnly(false)
          }
          
          // 设置 placeholder（如果支持）
          if (mathField.value.placeholder !== undefined) {
            mathField.value.placeholder = '请在此输入您的解题步骤和答案...'
          }
          
          // 调试：检查编辑器状态
          console.log('MathLive 编辑器初始化:', {
            readOnly: mathField.value.readOnly,
            value: mathField.value.getValue(),
            isConnected: mathField.value.isConnected,
            hasFocus: document.activeElement === mathField.value
          })
          
          // 调试：检查编辑器状态
          console.log('MathLive 编辑器初始化:', {
            readOnly: mathField.value.readOnly,
            value: mathField.value.getValue(),
            isConnected: mathField.value.isConnected
          })
          
          // 设置初始值
          if (userAnswer.value) {
            mathField.value.setValue(userAnswer.value, { suppressChangeNotifications: true })
          }
          
          // 手动添加事件监听器（Vue 的 @input 可能不工作）
          const handleInput = (event) => {
            if (mathField.value) {
              isUpdatingFromMathField = true
              const currentValue = mathField.value.getValue()
              if (currentValue !== userAnswer.value) {
                userAnswer.value = currentValue
                handleMathInput(event)
              }
              // 使用 nextTick 确保更新完成
              nextTick(() => {
                isUpdatingFromMathField = false
              })
            }
          }
          
          const handleFocus = () => {
            showHintSection()
          }
          
          // 处理键盘事件，支持回车和空格
          const handleKeyDown = (event) => {
            // 回车键 - 插入换行
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              event.stopPropagation()
              mathField.value.insert('\\\\')
              userAnswer.value = mathField.value.getValue()
              handleMathInput(event)
              return false
            }
            
            // Shift+Enter 也支持换行
            if (event.key === 'Enter' && event.shiftKey) {
              event.preventDefault()
              event.stopPropagation()
              mathField.value.insert('\\\\')
              userAnswer.value = mathField.value.getValue()
              handleMathInput(event)
              return false
            }
            
            // 空格键 - 允许输入空格
            if (event.key === ' ') {
              // 允许空格，不阻止默认行为
              // MathLive 会自动处理空格
            }
            
            // 快捷键：Alt+1 输入 ∵，Alt+2 输入 ∴
            if (event.altKey) {
              if (event.key === '1' || event.keyCode === 49) {
                event.preventDefault()
                mathField.value.insert('\\because ')
                userAnswer.value = mathField.value.getValue()
                handleMathInput(event)
                return false
              }
              if (event.key === '2' || event.keyCode === 50) {
                event.preventDefault()
                mathField.value.insert('\\therefore ')
                userAnswer.value = mathField.value.getValue()
                handleMathInput(event)
                return false
              }
            }
          }
          
          mathField.value.addEventListener('input', handleInput)
          mathField.value.addEventListener('focus', handleFocus)
          mathField.value.addEventListener('keydown', handleKeyDown)
          
          // 保存清理函数
          mathField.value._cleanup = () => {
            mathField.value.removeEventListener('input', handleInput)
            mathField.value.removeEventListener('focus', handleFocus)
            mathField.value.removeEventListener('keydown', handleKeyDown)
          }
          
          // 自动聚焦到编辑器（使用多种方式确保聚焦成功）
          const autoFocus = () => {
            if (mathField.value) {
              try {
                // 确保编辑器处于可编辑状态
                if (mathField.value.setReadOnly) {
                  mathField.value.setReadOnly(false)
                }
                
                // 方法1: 直接调用 focus
                mathField.value.focus()
                
                // 方法2: 使用 requestAnimationFrame 确保 DOM 已更新
                requestAnimationFrame(() => {
                  if (mathField.value) {
                    try {
                      // 再次确保可编辑
                      if (mathField.value.setReadOnly) {
                        mathField.value.setReadOnly(false)
                      }
                      
                      mathField.value.focus()
                      
                      // 确保光标可见
                      // MathLive 会自动显示光标，focus() 已经足够
                      // 不需要额外的命令来移动光标
                    } catch (e) {
                      console.warn('requestAnimationFrame 聚焦失败:', e)
                    }
                  }
                })
              } catch (error) {
                console.warn('自动聚焦失败:', error)
              }
            }
          }
          
          // 延迟聚焦，确保 MathLive 完全初始化
          setTimeout(autoFocus, 300)
          // 备用聚焦，如果第一次失败
          setTimeout(autoFocus, 600)
          
        } catch (error) {
          console.warn('设置 MathLive 选项失败:', error)
        }
      }
    }, 300)
  })
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  if (inputTimer.value) {
    clearTimeout(inputTimer.value)
  }
  
  // 清理 MathLive 事件监听器
  if (mathField.value && mathField.value._cleanup) {
    mathField.value._cleanup()
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
        
        .hint-container {
            background: linear-gradient(145deg, #f0f4ff, #e0e7ff);
            border-left: 4px solid #667eea;
            border-radius: 0 10px 10px 0;
        }

        .hint-content {
            line-height: 1.8;
        }

        .hint-content :deep(.katex) {
            font-size: 1.1em;
        }

        .hint-content :deep(.katex-display) {
            margin: 0.8em 0;
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
        
        /* 题目显示区域 */
        .question-display {
            background: transparent;
            padding: 0;
        }
        
        .question-content {
            font-family: 'Noto Serif SC', serif;
            font-size: 1.5rem;
            color: #1f2937;
            text-align: left;
            padding: 1.5rem;
            background: linear-gradient(145deg, #ffffff, #f8faff);
            border-radius: 12px;
            border: 2px solid #e5e7eb;
            min-height: 80px;
            line-height: 1.8;
        }
        
        .question-content .katex {
            font-size: 1.3rem;
        }
        
        .question-content .katex-display {
            margin: 1rem 0;
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
        
        /* MathLive 编辑器样式 */
        .mathlive-container {
            margin-bottom: 1rem;
        }
        
        .math-field-container {
            width: 100%;
            min-height: 120px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 1rem;
            background: linear-gradient(145deg, #f8faff, #e8ecf7);
            transition: all 0.3s ease;
        }
        
        .math-field-container:focus-within {
            background: white;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        /* MathLive math-field 元素样式 */
        .math-field-container math-field {
            width: 100%;
            min-height: 80px;
            font-size: 1.2rem;
            display: block;
            cursor: text;
            pointer-events: auto;
            outline: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        /* 确保 MathLive 内部元素正确显示和可交互 */
        .math-field-container math-field::part(virtual-keyboard-toggle) {
            display: none;
        }
        
        /* 确保 MathLive 内部可编辑区域可点击 */
        .math-field-container math-field::part(content) {
            cursor: text;
            pointer-events: auto;
        }
        
        /* 确保光标可见 */
        .math-field-container math-field::part(selection) {
            background-color: rgba(102, 126, 234, 0.2);
        }
        
        /* 全局样式：确保 MathLive 光标可见 */
        .math-field-container math-field .ML__caret,
        .math-field-container math-field .ML__caret:before {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            background-color: #667eea !important;
            width: 2px !important;
        }
        
        /* 确保编辑器内容区域可见 */
        .math-field-container math-field .ML__base {
            min-height: 60px;
            padding: 0.5rem;
            display: flex;
            align-items: center;
        }
        
        /* 聚焦时的光标样式 */
        .math-field-container:focus-within math-field .ML__caret {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }
        
        /* 确保容器可点击并聚焦 */
        .math-field-container {
            cursor: text;
            position: relative;
        }
        
        .math-field-container:hover {
            border-color: #c0c0c0;
        }
        
        /* 确保 MathLive 内部输入区域可见和可编辑 */
        .math-field-container math-field .ML__base {
            min-height: 60px;
            padding: 0.5rem;
        }
        
        /* 确保光标闪烁动画可见 */
        .math-field-container math-field .ML__caret {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        /* 确保编辑器处于可编辑状态时的样式 */
        .math-field-container math-field[readonly="false"],
        .math-field-container math-field:not([readonly]) {
            cursor: text;
        }
        
        /* 键盘切换按钮 */
        .keyboard-toggle-container {
            margin-top: 0.75rem;
            display: flex;
            justify-content: flex-end;
        }
        
        .keyboard-toggle-btn {
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background: linear-gradient(145deg, #f8faff, #e8ecf7);
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            color: #667eea;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .keyboard-toggle-btn:hover {
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            border-color: #667eea;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .keyboard-toggle-btn.active {
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            border-color: #667eea;
        }
        
        /* KaTeX 渲染样式 */
        .math-formula .katex,
        .question-content .katex {
            font-size: 1.3rem;
        }
        
        .question-content .katex-display {
            margin: 0.5rem 0;
            text-align: center;
        }
        
        .math-error {
            color: #ef4444;
            background: #fee2e2;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
    </style>

