<template>
  <div class="min-h-screen bg-[#FAF9F6] relative overflow-x-hidden">
    <!-- 主容器 -->
    <div class="relative z-10 min-h-screen flex flex-col">
      <!-- 头部 -->
      <header class="text-center py-8 px-4">
        <div class="inline-flex items-center justify-center mb-4">
          <i class="fas fa-th text-2xl text-amber-800 mr-3"></i>
          <h1 class="text-4xl md:text-5xl font-bold text-amber-900">数学残局挑战</h1>
          <i class="fas fa-th text-2xl text-amber-800 ml-3"></i>
        </div>
        <p class="text-base md:text-lg text-amber-800 font-medium mb-2">破解数学谜题，挑战思维极限</p>
        <div class="flex justify-center items-center mt-2 space-x-2 text-amber-700">
          <i class="fas fa-chess-pawn text-sm"></i>
          <span class="text-sm">智慧如棋，步步为营</span>
          <i class="fas fa-trophy text-sm"></i>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <main class="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        <!-- 难度选择区域 -->
        <section class="mb-12">
          <h2 class="text-2xl md:text-3xl font-bold text-center text-amber-900 mb-8">
            <i class="fas fa-star text-amber-700 mr-2"></i>
            选择你的挑战等级
            <i class="fas fa-star text-amber-700 ml-2"></i>
          </h2>
          
          <div class="flex flex-wrap justify-center items-start gap-8 md:gap-12 mb-8">
            <!-- 初级 -->
            <div class="difficulty-level text-center group w-full md:w-auto">
              <div 
                class="level-circle difficulty-beginner mb-4 mx-auto" 
                :class="{ 'selected': selectedLevel === 'beginner' }"
                @click="selectLevel('beginner')"
              >
                基础入门
              </div>
              <h3 class="text-lg font-semibold text-green-700 mb-3">基础入门</h3>
              <ul class="text-sm text-green-700 space-y-1 text-left max-w-xs mx-auto">
                <li>适合初学者</li>
                <li>掌握基本概念</li>
                <li class="flex items-center">
                  <i class="fas fa-leaf mr-2 text-green-600"></i>
                  轻松上手
                </li>
              </ul>
            </div>

            <!-- 中级 -->
            <div class="difficulty-level text-center group w-full md:w-auto">
              <div 
                class="level-circle difficulty-intermediate mb-4 mx-auto" 
                :class="{ 'selected': selectedLevel === 'intermediate' }"
                @click="selectLevel('intermediate')"
              >
                进阶挑战
              </div>
              <h3 class="text-lg font-semibold text-orange-700 mb-3">进阶挑战</h3>
              <ul class="text-sm text-orange-700 space-y-1 text-left max-w-xs mx-auto">
                <li>提升解题技巧</li>
                <li>拓展思维广度</li>
                <li class="flex items-center">
                  <i class="fas fa-brain mr-2 text-orange-600"></i>
                  挑战自我
                </li>
              </ul>
            </div>

            <!-- 高级 -->
            <div class="difficulty-level text-center group w-full md:w-auto">
              <div 
                class="level-circle difficulty-advanced mb-4 mx-auto" 
                :class="{ 'selected': selectedLevel === 'advanced' }"
                @click="selectLevel('advanced')"
              >
                大师级别
              </div>
              <h3 class="text-lg font-semibold text-red-700 mb-3">大师级别</h3>
              <ul class="text-sm text-red-700 space-y-1 text-left max-w-xs mx-auto">
                <li>极限思维训练</li>
                <li>突破认知边界</li>
                <li class="flex items-center">
                  <i class="fas fa-crown mr-2 text-red-600"></i>
                  王者之路
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 知识点标签区域 -->
        <section v-if="selectedLevel && availableTags.length > 0" class="mb-12">
          <h2 class="text-2xl md:text-3xl font-bold text-center text-amber-900 mb-8">
            <i class="fas fa-book text-amber-800 mr-2"></i>
            选择知识点
            <i class="fas fa-book text-amber-800 ml-2"></i>
          </h2>
          
          <div class="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
            <div
              v-for="tag in availableTags"
              :key="tag"
              @click="selectTag(tag)"
              class="tag-card px-6 py-3 bg-white rounded-full border-2 border-amber-300 cursor-pointer transition-all duration-300 hover:scale-110 hover:shadow-lg hover:border-amber-500"
            >
              <span class="text-amber-800 font-medium">{{ tag }}</span>
            </div>
          </div>
          
          <div v-if="loadingTags" class="text-center mt-4">
            <div class="text-amber-600">正在加载知识点...</div>
          </div>
        </section>

      </main>
    </div>

    <!-- 操作提示 -->
    <div 
      ref="hintRef"
      class="fixed top-4 right-4 bg-yellow-50 border-2 border-amber-200 rounded-lg p-3 shadow-md transition-all duration-500 opacity-90 max-w-xs"
    >
      <div class="flex items-center">
        <i :class="hintIcon" class="mr-2"></i>
        <span class="text-amber-800 text-xs font-medium">{{ hintText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'

const router = useRouter()

const selectedLevel = ref('')
const hintRef = ref(null)
const hintText = ref('点击难度等级开始挑战')
const hintIcon = ref('fas fa-info-circle text-yellow-600')
const availableTags = ref([])
const loadingTags = ref(false)

const levelNames = {
  'beginner': '初级',
  'intermediate': '中级',
  'advanced': '高级'
}

const getLevelName = (level) => levelNames[level] || level

// 难度映射到数据库难度值
const difficultyMap = {
  'beginner': 1,    // 初级：难度1-2
  'intermediate': 2, // 中级：难度3
  'advanced': 3     // 高级：难度4-5
}

// 获取该难度级别的所有知识点标签
const fetchTagsByLevel = async (level) => {
  try {
    loadingTags.value = true
    const difficulty = difficultyMap[level] || 1
    const apiUrl = `http://localhost:8000/api/questions?difficulty=${difficulty}&limit=100`
    
    const response = await fetch(apiUrl)
    if (!response.ok) {
      throw new Error('获取知识点失败')
    }
    
    const data = await response.json()
    // 收集所有唯一的标签
    const tagSet = new Set()
    data.questions.forEach(q => {
      q.tags.forEach(tag => tagSet.add(tag))
    })
    availableTags.value = Array.from(tagSet)
  } catch (error) {
    console.error('获取知识点失败:', error)
    availableTags.value = []
  } finally {
    loadingTags.value = false
  }
}

const selectLevel = async (level) => {
  selectedLevel.value = level
  
  updateHint(
    `已选择${getLevelName(level)}难度，请选择知识点`,
    'fas fa-check-circle text-green-600',
    '#F0FDF4'
  )
  
  // 获取该难度级别的知识点标签
  await fetchTagsByLevel(level)
}

const selectTag = (tag) => {
  if (!selectedLevel.value) return
  
  updateHint(
    `已选择${tag}，正在加载题目...`,
    'fas fa-play-circle text-blue-600',
    '#EFF6FF'
  )
  
  // 跳转到答题页面，带上级别和标签参数
  setTimeout(() => {
    router.push({
      path: '/answer',
      query: {
        level: selectedLevel.value,
        tag: tag
      }
    })
  }, 500)
}

const updateHint = (text, icon, bgColor) => {
  hintText.value = text
  hintIcon.value = icon
  
  nextTick(() => {
    if (hintRef.value) {
      gsap.to(hintRef.value, {
        duration: 0.3,
        opacity: 1,
        scale: 1,
        backgroundColor: bgColor || '#FEF9C3'
      })
    }
  })
}

onMounted(() => {
  // 等待 DOM 完全渲染
  nextTick(() => {
    // GSAP动画初始化
    gsap.from('h1', {
      duration: 1.5,
      y: -50,
      opacity: 0,
      ease: "bounce.out"
    })
    
    // 使用 fromTo 确保动画结束后元素完全可见且可点击
    const circles = document.querySelectorAll('.level-circle')
    circles.forEach((circle, index) => {
      // 先设置初始状态，确保元素可见
      gsap.set(circle, { 
        scale: 0, 
        opacity: 0,
        pointerEvents: 'none' // 动画期间禁用点击
      })
      
      gsap.to(circle, {
        duration: 1,
        scale: 1,
        opacity: 1,
        ease: "back.out(1.7)",
        delay: 0.5 + index * 0.2,
        pointerEvents: 'auto', // 动画结束后启用点击
        onComplete: () => {
          // 动画完成后清除内联样式，让CSS样式生效
          gsap.set(circle, { clearProps: "all" })
        }
      })
    })
    
    gsap.from('.knowledge-card', {
      duration: 0.8,
      y: 50,
      opacity: 0,
      stagger: 0.1,
      ease: "power2.out",
      delay: 1
    })
  })

  // 提示自动隐藏
  setTimeout(() => {
    if (hintRef.value) {
      gsap.to(hintRef.value, {
        duration: 0.5,
        opacity: 0.3,
        scale: 0.95
      })
    }
  }, 3000)

  // 响应式调整
  const adjustForMobile = () => {
    if (window.innerWidth < 768) {
      document.querySelectorAll('.level-circle').forEach(circle => {
        circle.style.width = '80px'
        circle.style.height = '80px'
        circle.style.fontSize = '16px'
      })
    }
  }

  window.addEventListener('resize', adjustForMobile)
  adjustForMobile()
})
</script>

<style scoped>
/* 样式已移至 src/style.css */
</style>

