<template>
  <div class="records-container">
    <div class="records-header">
      <div class="header-left">
        <button @click="goHome" class="btn-home" title="返回主页">
          <i class="fas fa-home"></i>
        </button>
        <h1 class="records-title">
          <i class="fas fa-history mr-2"></i>
          我的答题记录
        </h1>
      </div>
      <div class="records-filters">
        <button @click="loadAnalysis" class="btn-analysis" v-if="currentUser">
          <i class="fas fa-chart-line mr-2"></i>
          查看分析报告
        </button>
      </div>
    </div>

    <!-- 分析报告弹窗 -->
    <div v-if="showAnalysis" class="analysis-modal" @click.self="showAnalysis = false">
      <div class="analysis-content">
        <div class="analysis-header">
          <h2>学习分析报告</h2>
          <button @click="showAnalysis = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <!-- 六维能力图 -->
        <div class="ability-chart">
          <h3>六维能力评估</h3>
          <div class="chart-container">
            <canvas ref="abilityChart" width="400" height="400"></canvas>
          </div>
        </div>
        
        <!-- 薄弱点 -->
        <div class="weak-points">
          <h3>薄弱点分析</h3>
          <div v-if="analysisData.weak_points && analysisData.weak_points.length > 0">
            <div class="weak-point-tag" v-for="point in analysisData.weak_points" :key="point">
              {{ point }}
            </div>
          </div>
          <p v-else class="no-weak-points">恭喜！您没有明显的薄弱点。</p>
        </div>
        
        <!-- 推荐题目 -->
        <div class="recommended-questions" v-if="analysisData.recommended_questions && analysisData.recommended_questions.length > 0">
          <h3>推荐训练题目</h3>
          <div class="question-list">
            <div 
              v-for="q in analysisData.recommended_questions" 
              :key="q.id"
              class="question-card"
              @click="goToQuestion(q.id)"
            >
              <div class="question-preview" v-html="renderMathContent(q.content.substring(0, 100) + '...')"></div>
              <div class="question-meta">
                <span class="difficulty">难度: {{ q.difficulty }}</span>
                <span class="tags">{{ q.tags.join(', ') }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 总结 -->
        <div class="analysis-summary">
          <h3>分析总结</h3>
          <p>{{ analysisData.summary }}</p>
        </div>
      </div>
    </div>

    <!-- 答题记录列表 -->
    <div class="records-list">
      <div v-if="loading" class="loading">
        <i class="fas fa-spinner fa-spin"></i> 加载中...
      </div>
      <div v-else-if="records.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <p>暂无答题记录</p>
        <button @click="goHome" class="btn-back-home">
          <i class="fas fa-home mr-2"></i>
          返回主页开始答题
        </button>
      </div>
      <div v-else>
        <div 
          v-for="record in records" 
          :key="record.id"
          class="record-item"
        >
          <div class="record-header">
            <span class="record-date">{{ formatDate(record.created_at) }}</span>
            <span 
              class="record-status" 
              :class="getStatusClass(record.is_correct)"
              :title="getStatusTooltip(record.is_correct)"
            >
              {{ getStatusText(record.is_correct) }}
            </span>
          </div>
          <div class="record-question" v-html="renderMathContent(record.question_content || '')"></div>
          <div class="record-details">
            <span class="detail-item">
              <i class="fas fa-clock"></i> {{ record.time_spent || 0 }}秒
            </span>
            <span class="detail-item">
              <i class="fas fa-lightbulb"></i> {{ record.hint_count }}次提示
            </span>
            <button 
              v-if="record.question_id" 
              @click="viewSolutions(record.question_id)"
              class="btn-solutions"
            >
              <i class="fas fa-list"></i> 查看解法
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import { useUser } from '../composables/useUser'

const router = useRouter()
const { currentUser, users, loadUsers } = useUser()

const records = ref([])
const loading = ref(false)
const showAnalysis = ref(false)
const analysisData = ref({})
const abilityChart = ref(null)

// 加载答题记录
const loadRecords = async () => {
  loading.value = true
  try {
    const url = currentUser.value 
      ? `http://localhost:8000/api/answer-records?user_id=${currentUser.value.id}`
      : 'http://localhost:8000/api/answer-records'
    const response = await fetch(url)
    if (!response.ok) throw new Error('加载失败')
    records.value = await response.json()
  } catch (error) {
    console.error('加载答题记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听全局用户变化，自动更新数据
watch(currentUser, (newUser, oldUser) => {
  // 当用户变化时，重新加载答题记录
  loadRecords()
}, { immediate: false })

// 加载分析报告
const loadAnalysis = async () => {
  if (!currentUser.value) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/analysis/${currentUser.value.id}`)
    if (!response.ok) throw new Error('加载分析失败')
    analysisData.value = await response.json()
    showAnalysis.value = true
    
    nextTick(() => {
      drawAbilityChart()
    })
  } catch (error) {
    console.error('加载分析报告失败:', error)
    alert('加载分析报告失败')
  }
}

// 绘制六维能力图
const drawAbilityChart = () => {
  if (!abilityChart.value || !analysisData.value.abilities) return
  
  const canvas = abilityChart.value
  const ctx = canvas.getContext('2d')
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = 150
  
  const abilities = analysisData.value.abilities
  const abilityNames = Object.keys(abilities)
  const angleStep = (2 * Math.PI) / abilityNames.length
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 绘制网格
  ctx.strokeStyle = '#e0e0e0'
  ctx.lineWidth = 1
  for (let i = 1; i <= 5; i++) {
    const r = (radius * i) / 5
    ctx.beginPath()
    ctx.arc(centerX, centerY, r, 0, 2 * Math.PI)
    ctx.stroke()
  }
  
  // 绘制轴线
  ctx.strokeStyle = '#ccc'
  abilityNames.forEach((_, index) => {
    const angle = index * angleStep - Math.PI / 2
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(x, y)
    ctx.stroke()
  })
  
  // 绘制数据点
  ctx.fillStyle = 'rgba(102, 126, 234, 0.3)'
  ctx.strokeStyle = '#667eea'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  abilityNames.forEach((name, index) => {
    const score = abilities[name] || 0
    const normalizedScore = score / 100
    const angle = index * angleStep - Math.PI / 2
    const r = radius * normalizedScore
    const x = centerX + r * Math.cos(angle)
    const y = centerY + r * Math.sin(angle)
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
  
  // 绘制标签
  ctx.fillStyle = '#333'
  ctx.font = '14px Arial'
  ctx.textAlign = 'center'
  abilityNames.forEach((name, index) => {
    const angle = index * angleStep - Math.PI / 2
    const x = centerX + (radius + 30) * Math.cos(angle)
    const y = centerY + (radius + 30) * Math.sin(angle)
    ctx.fillText(name, x, y)
    ctx.fillText(`${abilities[name] || 0}`, x, y + 20)
  })
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取状态文本
const getStatusText = (isCorrect) => {
  if (isCorrect === 1) return '正确'
  if (isCorrect === 2) return '错误'
  return '未判断' // 0 = 未判断：答案尚未被系统或老师评判
}

const getStatusTooltip = (isCorrect) => {
  if (isCorrect === 1) return '答案正确'
  if (isCorrect === 2) return '答案错误'
  return '未判断：答案尚未被系统或老师评判，等待审核中'
}

// 获取状态样式类
const getStatusClass = (isCorrect) => {
  if (isCorrect === 1) return 'status-correct'
  if (isCorrect === 2) return 'status-wrong'
  return 'status-unknown'
}

// 渲染数学公式
const renderMathContent = (content) => {
  if (!content) return ''
  // 简单的数学公式渲染（可以复用Answer.vue中的逻辑）
  try {
    return content.replace(/\$([^$]+)\$/g, (match, formula) => {
      try {
        return katex.renderToString(formula, { throwOnError: false })
      } catch {
        return match
      }
    })
  } catch {
    return content
  }
}

// 查看解法
const viewSolutions = async (questionId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/questions/${questionId}/solutions`)
    if (response.ok) {
      const solutions = await response.json()
      alert(`该题目有${solutions.length}种解法：\n${solutions.map(s => s.method).join('\n')}`)
    }
  } catch (error) {
    console.error('获取解法失败:', error)
  }
}

// 跳转到题目
const goToQuestion = (questionId) => {
  router.push(`/answer?questionId=${questionId}`)
}

// 返回主页
const goHome = () => {
  router.push('/')
}

onMounted(async () => {
  // 加载用户列表（如果还没有加载）
  await loadUsers()
  // 加载答题记录（会根据当前用户自动过滤）
  loadRecords()
})
</script>

<style scoped>
.records-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-home {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(145deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-home:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-home:active {
  transform: translateY(0) scale(1);
}

.records-title {
  font-size: 2rem;
  color: #333;
}

.records-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.btn-analysis {
  padding: 0.5rem 1.5rem;
  background: linear-gradient(145deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-analysis:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.record-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.record-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.record-date {
  color: #666;
  font-size: 0.9rem;
}

.record-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.status-correct {
  background: #d4edda;
  color: #155724;
}

.status-wrong {
  background: #f8d7da;
  color: #721c24;
}

.status-unknown {
  background: #e2e3e5;
  color: #383d41;
}

.record-question {
  margin-bottom: 1rem;
  color: #333;
  line-height: 1.6;
}

.record-details {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  color: #666;
  font-size: 0.9rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-solutions {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-solutions:hover {
  background: #e9ecef;
}

.loading, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.btn-back-home {
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(145deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-back-home:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.analysis-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.analysis-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f3f4f6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ability-chart {
  margin-bottom: 2rem;
}

.chart-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.weak-points {
  margin-bottom: 2rem;
}

.weak-point-tag {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #fff3cd;
  color: #856404;
  border-radius: 20px;
  margin: 0.5rem 0.5rem 0.5rem 0;
  font-size: 0.9rem;
}

.recommended-questions {
  margin-bottom: 2rem;
}

.question-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.question-card:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.question-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.analysis-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  line-height: 1.6;
}
</style>

