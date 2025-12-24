<template>
  <div class="min-h-screen bg-gradient-to-br from-yellow-50 via-white to-orange-50 relative overflow-x-hidden">
    <!-- 装饰性浮动元素 -->
    <div class="fixed inset-0 pointer-events-none">
      <div class="floating-element absolute top-10 left-10 w-6 h-6 bg-yellow-400 rounded-full opacity-20"></div>
      <div class="floating-element absolute top-1/4 right-20 w-8 h-8 bg-orange-400 rounded-full opacity-20"></div>
      <div class="floating-element absolute bottom-1/4 left-1/4 w-4 h-4 bg-red-400 rounded-full opacity-20"></div>
      <div class="floating-element absolute top-1/2 right-1/3 w-5 h-5 bg-yellow-600 rounded-full opacity-20"></div>
    </div>

    <!-- 古代花纹背景 -->
    <div class="ancient-pattern fixed inset-0 pointer-events-none"></div>

    <!-- 主容器 -->
    <div class="relative z-10 min-h-screen flex flex-col">
      <!-- 头部 -->
      <header class="text-center py-8 px-4">
        <div class="inline-flex items-center justify-center mb-4">
          <i class="fas fa-chess-board text-4xl text-yellow-700 mr-3"></i>
          <h1 class="text-4xl md:text-6xl font-bold text-yellow-800 title-glow">数学残局挑战</h1>
          <i class="fas fa-calculator text-4xl text-yellow-700 ml-3"></i>
        </div>
        <p class="text-lg md:text-xl text-yellow-700 font-medium">破解数学谜题，挑战思维极限</p>
        <div class="flex justify-center items-center mt-4 space-x-4 text-yellow-600">
          <i class="fas fa-medal"></i>
          <span class="text-sm">智慧如棋，步步为营</span>
          <i class="fas fa-trophy"></i>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <main class="flex-1 container mx-auto px-4 py-8">
        <!-- 难度选择区域 -->
        <section class="mb-16">
          <h2 class="text-2xl md:text-3xl font-bold text-center text-yellow-800 mb-8">
            <i class="fas fa-star mr-2"></i>
            选择你的挑战等级
            <i class="fas fa-star ml-2"></i>
          </h2>
          
          <div class="flex flex-wrap justify-center items-center gap-8 md:gap-16 mb-8">
            <!-- 初级 -->
            <div class="difficulty-level text-center group">
              <div 
                class="chess-piece difficulty-beginner mb-4 mx-auto" 
                :class="{ 'ring-4 ring-yellow-400': selectedLevel === 'beginner' }"
                @click="selectLevel('beginner')"
              >
                初级
              </div>
              <h3 class="text-lg font-semibold text-green-700 mb-2">基础入门</h3>
              <p class="text-sm text-green-600">适合初学者<br>掌握基本概念</p>
              <div class="mt-2 text-xs text-green-500">
                <i class="fas fa-leaf mr-1"></i>
                轻松上手
              </div>
            </div>

            <!-- 中级 -->
            <div class="difficulty-level text-center group">
              <div 
                class="chess-piece difficulty-intermediate mb-4 mx-auto" 
                :class="{ 'ring-4 ring-yellow-400': selectedLevel === 'intermediate' }"
                @click="selectLevel('intermediate')"
              >
                中级
              </div>
              <h3 class="text-lg font-semibold text-orange-700 mb-2">进阶挑战</h3>
              <p class="text-sm text-orange-600">提升解题技巧<br>拓展思维广度</p>
              <div class="mt-2 text-xs text-orange-500">
                <i class="fas fa-fire mr-1"></i>
                挑战自我
              </div>
            </div>

            <!-- 高级 -->
            <div class="difficulty-level text-center group">
              <div 
                class="chess-piece difficulty-advanced mb-4 mx-auto" 
                :class="{ 'ring-4 ring-yellow-400': selectedLevel === 'advanced' }"
                @click="selectLevel('advanced')"
              >
                高级
              </div>
              <h3 class="text-lg font-semibold text-red-100 mb-2">大师级别</h3>
              <p class="text-sm text-red-200">极限思维训练<br>突破认知边界</p>
              <div class="mt-2 text-xs text-red-300">
                <i class="fas fa-crown mr-1"></i>
                王者之路
              </div>
            </div>
          </div>
        </section>

        <!-- 知识点分类区域 -->
        <section class="mb-12">
          <h2 class="text-2xl md:text-3xl font-bold text-center text-yellow-800 mb-8">
            <i class="fas fa-book-open mr-2"></i>
            知识点分类
            <i class="fas fa-bookmark ml-2"></i>
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <!-- 代数 -->
            <div 
              class="knowledge-card p-6" 
              :class="{ 
                'ring-4 ring-blue-400': selectedKnowledge === 'algebra',
                'ring-2 ring-yellow-300 animate-pulse': selectedLevel && selectedKnowledge !== 'algebra'
              }"
              @click="selectKnowledge('algebra')"
            >
              <div class="text-center">
                <div class="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                  <i class="fas fa-square-root-alt text-3xl text-blue-600"></i>
                </div>
                <h3 class="text-xl font-bold text-blue-700 mb-3">代数</h3>
                <p class="text-gray-600 mb-4">方程、不等式、函数等代数运算与推理</p>
                <div class="flex justify-center space-x-2 text-xs text-gray-500">
                  <span class="bg-blue-100 px-2 py-1 rounded">方程</span>
                  <span class="bg-blue-100 px-2 py-1 rounded">函数</span>
                  <span class="bg-blue-100 px-2 py-1 rounded">不等式</span>
                </div>
              </div>
            </div>

            <!-- 几何 -->
            <div 
              class="knowledge-card p-6" 
              :class="{ 
                'ring-4 ring-blue-400': selectedKnowledge === 'geometry',
                'ring-2 ring-yellow-300 animate-pulse': selectedLevel && selectedKnowledge !== 'geometry'
              }"
              @click="selectKnowledge('geometry')"
            >
              <div class="text-center">
                <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                  <i class="fas fa-shapes text-3xl text-green-600"></i>
                </div>
                <h3 class="text-xl font-bold text-green-700 mb-3">几何</h3>
                <p class="text-gray-600 mb-4">图形性质、空间关系、几何证明</p>
                <div class="flex justify-center space-x-2 text-xs text-gray-500">
                  <span class="bg-green-100 px-2 py-1 rounded">三角形</span>
                  <span class="bg-green-100 px-2 py-1 rounded">圆</span>
                  <span class="bg-green-100 px-2 py-1 rounded">立体</span>
                </div>
              </div>
            </div>

            <!-- 统计 -->
            <div 
              class="knowledge-card p-6" 
              :class="{ 
                'ring-4 ring-blue-400': selectedKnowledge === 'statistics',
                'ring-2 ring-yellow-300 animate-pulse': selectedLevel && selectedKnowledge !== 'statistics'
              }"
              @click="selectKnowledge('statistics')"
            >
              <div class="text-center">
                <div class="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center">
                  <i class="fas fa-chart-bar text-3xl text-purple-600"></i>
                </div>
                <h3 class="text-xl font-bold text-purple-700 mb-3">统计与概率</h3>
                <p class="text-gray-600 mb-4">数据分析、概率计算、统计推断</p>
                <div class="flex justify-center space-x-2 text-xs text-gray-500">
                  <span class="bg-purple-100 px-2 py-1 rounded">概率</span>
                  <span class="bg-purple-100 px-2 py-1 rounded">统计</span>
                  <span class="bg-purple-100 px-2 py-1 rounded">数据</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 游戏特色介绍 -->
        <section class="text-center mb-12">
          <h2 class="text-2xl font-bold text-yellow-800 mb-6">
            <i class="fas fa-lightbulb mr-2"></i>
            挑战特色
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div class="bg-white bg-opacity-80 p-6 rounded-lg border-2 border-yellow-200">
              <i class="fas fa-puzzle-piece text-3xl text-yellow-600 mb-3"></i>
              <h3 class="text-lg font-semibold mb-2">残局设计</h3>
              <p class="text-gray-600 text-sm">每道题目都是精心设计的数学"残局"，需要巧妙的思路才能破解</p>
            </div>
            <div class="bg-white bg-opacity-80 p-6 rounded-lg border-2 border-yellow-200">
              <i class="fas fa-graduation-cap text-3xl text-yellow-600 mb-3"></i>
              <h3 class="text-lg font-semibold mb-2">分级训练</h3>
              <p class="text-gray-600 text-sm">从基础到进阶，循序渐进提升数学思维能力</p>
            </div>
            <div class="bg-white bg-opacity-80 p-6 rounded-lg border-2 border-yellow-200">
              <i class="fas fa-trophy text-3xl text-yellow-600 mb-3"></i>
              <h3 class="text-lg font-semibold mb-2">成就系统</h3>
              <p class="text-gray-600 text-sm">完成挑战获得成就徽章，记录你的数学征程</p>
            </div>
          </div>
        </section>
      </main>

      <!-- 底部 -->
      <footer class="text-center py-6 px-4 bg-yellow-800 bg-opacity-10">
        <div class="flex items-center justify-center mb-2">
          <i class="fas fa-chess-king text-yellow-700 mr-2"></i>
          <span class="text-yellow-800 font-medium">智者千虑，必有一得</span>
          <i class="fas fa-chess-queen text-yellow-700 ml-2"></i>
        </div>
        <p class="text-sm text-yellow-600">© 2024 数学残局挑战 - 让数学思维如棋艺般精进</p>
      </footer>
    </div>

    <!-- 操作提示 -->
    <div 
      ref="hintRef"
      class="fixed top-4 right-4 bg-yellow-100 border-2 border-yellow-300 rounded-lg p-4 shadow-lg transition-all duration-500 opacity-90"
    >
      <div class="flex items-center">
        <i :class="hintIcon" class="mr-2"></i>
        <span class="text-yellow-800 text-sm font-medium">{{ hintText }}</span>
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
const selectedKnowledge = ref('')
const hintRef = ref(null)
const hintText = ref('点击难度等级开始挑战，选择知识点分类查看题目')
const hintIcon = ref('fas fa-info-circle text-yellow-600')

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

const getLevelName = (level) => levelNames[level] || level
const getKnowledgeName = (knowledge) => knowledgeNames[knowledge] || knowledge

const selectLevel = (level) => {
  selectedLevel.value = level
  selectedKnowledge.value = ''
  
  updateHint(
    `已选择${getLevelName(level)}难度，请选择知识点分类`,
    'fas fa-check-circle text-green-600',
    '#F0FDF4'
  )
}

const selectKnowledge = (knowledge) => {
  if (!selectedLevel.value) {
    updateHint(
      '请先选择难度等级',
      'fas fa-exclamation-triangle text-orange-600',
      '#FEF3C7'
    )
    
    // 提示选择难度动画
    const pieces = document.querySelectorAll('.chess-piece')
    pieces.forEach(piece => {
      gsap.to(piece, {
        duration: 0.5,
        scale: 1.1,
        yoyo: true,
        repeat: 1
      })
    })
    return
  }
  
  selectedKnowledge.value = knowledge
  
  updateHint(
    `准备进入${getLevelName(selectedLevel.value)}-${getKnowledgeName(knowledge)}挑战！`,
    'fas fa-play-circle text-blue-600',
    '#EFF6FF'
  )
  
  // 导航到答题页面
  setTimeout(() => {
    router.push({
      path: '/answer',
      query: {
        level: selectedLevel.value,
        knowledge: knowledge
      }
    })
  }, 1000)
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
  // GSAP动画初始化
  gsap.from('.title-glow', {
    duration: 1.5,
    y: -50,
    opacity: 0,
    ease: "bounce.out"
  })
  
  gsap.from('.chess-piece', {
    duration: 1,
    scale: 0,
    opacity: 0,
    stagger: 0.2,
    ease: "back.out(1.7)",
    delay: 0.5
  })
  
  gsap.from('.knowledge-card', {
    duration: 0.8,
    y: 50,
    opacity: 0,
    stagger: 0.1,
    ease: "power2.out",
    delay: 1
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
      document.querySelectorAll('.chess-piece').forEach(piece => {
        piece.style.width = '60px'
        piece.style.height = '60px'
        piece.style.fontSize = '14px'
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

