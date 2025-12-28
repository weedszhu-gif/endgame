<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500">
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
              <i class="fas fa-chart-line text-white text-2xl mr-3"></i>
              <span class="text-white text-xl font-bold">薄弱点分析</span>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="goToRecords"
              class="text-white hover:text-yellow-200 transition-colors px-4 py-2 rounded-lg bg-white bg-opacity-10 hover:bg-opacity-20 flex items-center gap-2"
              title="查看答题记录"
            >
              <i class="fas fa-history"></i>
              <span class="text-sm font-medium">答题记录</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- 标题和用户选择 -->
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold text-white mb-4">学习分析报告</h1>
          <p class="text-white text-lg opacity-90 mb-4">基于您的答题表现，为您生成个性化分析</p>
          <div v-if="loading" class="text-white">
            <i class="fas fa-spinner fa-spin"></i> 加载中...
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 六维能力雷达图 -->
          <div class="analysis-card p-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
              <i class="fas fa-radar text-blue-500 mr-2"></i>
              六维能力评估
            </h2>
            <div v-if="!currentUser" class="text-center text-gray-500 py-8">
              <i class="fas fa-info-circle text-4xl mb-4"></i>
              <p>请先在右上角选择用户以查看能力评估</p>
            </div>
            <div v-else-if="!hasAbilityData" class="text-center text-gray-500 py-8">
              <i class="fas fa-chart-line text-4xl mb-4 text-gray-400"></i>
              <p class="mb-2">该用户暂无答题数据</p>
              <p class="text-sm text-gray-400">请先完成一些题目，系统才能生成能力评估</p>
              <button
                @click="goHome"
                class="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <i class="fas fa-play mr-2"></i>
                去答题
              </button>
            </div>
            <div v-else class="radar-chart-container">
              <canvas ref="radarChart" width="400" height="400"></canvas>
            </div>
          </div>

          <!-- 知识点评分 -->
          <div class="analysis-card p-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
              <i class="fas fa-tags text-green-500 mr-2"></i>
              知识点掌握情况
            </h2>
            <div v-if="!currentUser" class="text-center text-gray-500 py-8">
              <i class="fas fa-info-circle text-4xl mb-4"></i>
              <p>请先在右上角选择用户以查看知识点掌握情况</p>
            </div>
            <div v-else-if="Object.keys(tagScores).length === 0" class="text-center text-gray-500 py-8">
              <i class="fas fa-inbox text-4xl mb-4 text-gray-400"></i>
              <p class="mb-2">该用户暂无知识点数据</p>
              <p class="text-sm text-gray-400">完成题目后，系统会自动分析您的知识点掌握情况</p>
              <button
                @click="goHome"
                class="mt-4 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                <i class="fas fa-play mr-2"></i>
                去答题
              </button>
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="(score, tag) in tagScores"
                :key="tag"
                class="tag-score-item"
              >
                <div class="flex justify-between items-center mb-2">
                  <span class="font-semibold text-gray-700">{{ tag }}</span>
                  <span class="text-lg font-bold" :class="getScoreColor(score)">
                    {{ Math.round(score) }}%
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div
                    class="h-3 rounded-full transition-all duration-500"
                    :class="getScoreBarColor(score)"
                    :style="{ width: `${Math.min(100, Math.max(0, score))}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 总结建议 -->
        <div class="analysis-card p-8 mt-8">
          <h2 class="text-2xl font-bold text-gray-800 mb-4 text-center">
            <i class="fas fa-lightbulb text-yellow-500 mr-2"></i>
            学习建议
          </h2>
          <div v-if="!currentUser" class="bg-gray-50 border-l-4 border-gray-400 p-6 rounded">
            <p class="text-gray-600 leading-relaxed">请先在右上角选择用户以查看学习建议</p>
          </div>
          <div v-else-if="!analysisSummary" class="bg-gray-50 border-l-4 border-gray-400 p-6 rounded">
            <p class="text-gray-600 leading-relaxed">正在生成学习建议...</p>
          </div>
          <div v-else class="bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
            <p class="text-gray-700 leading-relaxed">{{ analysisSummary }}</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="text-center mt-8 flex justify-center gap-4">
          <button
            @click="goHome"
            class="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <i class="fas fa-home mr-2"></i>
            返回主页
          </button>
          <button
            @click="goToRecords"
            class="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white px-8 py-3 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <i class="fas fa-history mr-2"></i>
            查看答题记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser } from '../composables/useUser'

const route = useRoute()
const router = useRouter()
const { currentUser, users, loadUsers } = useUser()

// 六维能力数据
const abilities = ref({
  '逻辑推理': 75,
  '空间想象': 60,
  '计算能力': 80,
  '问题分析': 70,
  '创新思维': 65,
  '知识应用': 72
})

// 知识点评分
const tagScores = ref({})

// 分析总结
const analysisSummary = ref('')

const radarChart = ref(null)
const loading = ref(false)

// 计算是否有能力数据
const hasAbilityData = computed(() => {
  return Object.values(abilities.value).some(score => score > 0)
})

// 获取分数颜色
const getScoreColor = (score) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

// 获取进度条颜色
const getScoreBarColor = (score) => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

// 返回主页
const goHome = () => {
  router.push('/')
}

// 跳转到答题记录页面
const goToRecords = () => {
  router.push('/records')
}

// 绘制雷达图
const drawRadarChart = () => {
  const canvas = radarChart.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 40
  const angleStep = (2 * Math.PI) / Object.keys(abilities.value).length

  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 绘制网格
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  for (let i = 1; i <= 5; i++) {
    ctx.beginPath()
    ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI)
    ctx.stroke()
  }

  // 绘制轴线
  ctx.strokeStyle = '#d1d5db'
  ctx.lineWidth = 1
  let angle = -Math.PI / 2
  Object.keys(abilities.value).forEach(() => {
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(
      centerX + radius * Math.cos(angle),
      centerY + radius * Math.sin(angle)
    )
    ctx.stroke()
    angle += angleStep
  })
  
  // 检查是否有数据
  const hasData = Object.values(abilities.value).some(score => score > 0)
  
  if (hasData) {
    // 绘制数据区域
    ctx.fillStyle = 'rgba(59, 130, 246, 0.3)'
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 2
    ctx.beginPath()
    angle = -Math.PI / 2
    let first = true
    Object.values(abilities.value).forEach((value) => {
      const r = (radius * value) / 100
      const x = centerX + r * Math.cos(angle)
      const y = centerY + r * Math.sin(angle)
      if (first) {
        ctx.moveTo(x, y)
        first = false
      } else {
        ctx.lineTo(x, y)
      }
      angle += angleStep
    })
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // 绘制数据点和标签
    ctx.fillStyle = '#3b82f6'
    ctx.font = '14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    angle = -Math.PI / 2
    Object.entries(abilities.value).forEach(([name, value]) => {
      const r = (radius * value) / 100
      const x = centerX + r * Math.cos(angle)
      const y = centerY + r * Math.sin(angle)
      
      // 绘制点
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fill()
      
      // 绘制标签
      const labelX = centerX + (radius + 20) * Math.cos(angle)
      const labelY = centerY + (radius + 20) * Math.sin(angle)
      ctx.fillStyle = '#374151'
      ctx.fillText(name, labelX, labelY)
      ctx.fillStyle = '#3b82f6'
      
      angle += angleStep
    })
  } else {
    // 如果没有数据，只显示标签
    ctx.fillStyle = '#9ca3af'
    ctx.font = '14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    angle = -Math.PI / 2
    Object.keys(abilities.value).forEach((name) => {
      const labelX = centerX + (radius + 20) * Math.cos(angle)
      const labelY = centerY + (radius + 20) * Math.sin(angle)
      ctx.fillText(name, labelX, labelY)
      angle += angleStep
    })
  }
}

// 获取分析数据
const fetchAnalysis = async () => {
  if (!currentUser.value) {
    return
  }
  
  loading.value = true
  try {
    const apiUrl = `http://localhost:8000/api/analysis/${currentUser.value.id}`
    
    const response = await fetch(apiUrl)
    if (!response.ok) {
      throw new Error(`获取分析数据失败: ${response.status}`)
    }
    const data = await response.json()
    
    // 更新数据
    if (data.abilities) {
      // 确保能力名称匹配（兼容新旧格式）
      const abilityMapping = {
        '逻辑推理': '逻辑推理',
        '空间想象': '空间想象',
        '计算能力': '计算能力',
        '问题分析': '问题分析',
        '创新思维': '创新思维',
        '知识应用': '综合应用',
        '综合应用': '综合应用'
      }
      
      const mappedAbilities = {}
      for (const [key, value] of Object.entries(data.abilities)) {
        const mappedKey = abilityMapping[key] || key
        mappedAbilities[mappedKey] = value
      }
      abilities.value = mappedAbilities
    }
    if (data.tag_scores) {
      tagScores.value = data.tag_scores
    } else {
      tagScores.value = {}
    }
    if (data.summary) {
      analysisSummary.value = data.summary
    } else {
      analysisSummary.value = '根据您的答题表现，建议加强薄弱能力的训练。'
    }
    
    // 重新绘制雷达图
    setTimeout(() => {
      drawRadarChart()
    }, 100)
  } catch (error) {
    console.error('获取分析数据失败:', error)
    // 使用默认数据
    analysisSummary.value = '根据您的答题表现，建议加强空间想象和创新思维能力的训练。在知识点方面，建议重点复习二次函数和几何证明相关内容。'
    tagScores.value = {}
    setTimeout(() => {
      drawRadarChart()
    }, 100)
  } finally {
    loading.value = false
  }
}

// 监听全局用户变化，自动更新数据
watch(currentUser, (newUser, oldUser) => {
  if (newUser) {
    // 用户变化时，加载新用户的分析数据
    fetchAnalysis()
  } else {
    // 如果用户被清空，清空数据
    tagScores.value = {}
    analysisSummary.value = ''
    abilities.value = {
      '逻辑推理': 0,
      '空间想象': 0,
      '计算能力': 0,
      '问题分析': 0,
      '创新思维': 0,
      '知识应用': 0
    }
    setTimeout(() => {
      drawRadarChart()
    }, 100)
  }
}, { immediate: false })

onMounted(async () => {
  // 加载用户列表（如果还没有加载）
  await loadUsers()
  // 如果有全局用户，加载数据
  if (currentUser.value) {
    fetchAnalysis()
  }
  // 注意：URL 中的 user_id 参数由全局导航栏的用户选择器处理
})
</script>

<style scoped>
.analysis-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.analysis-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.radar-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.tag-score-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
</style>

