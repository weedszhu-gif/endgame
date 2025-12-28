<template>
  <Transition name="keyboard-slide">
    <div v-if="visible" class="virtual-keyboard-overlay" @click.self="close">
      <div class="virtual-keyboard" @click.stop>
        <div class="keyboard-header">
          <span class="keyboard-title">数学符号键盘</span>
          <button @click="close" class="keyboard-close-btn" title="关闭">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <!-- 分类标签 -->
        <div class="keyboard-tabs">
          <button
            v-for="category in categories"
            :key="category.id"
            @click="activeCategory = category.id"
            class="tab-btn"
            :class="{ active: activeCategory === category.id }"
          >
            {{ category.name }}
          </button>
        </div>
        
        <!-- 符号网格 -->
        <div class="keyboard-grid">
          <button
            v-for="item in currentSymbols"
            :key="item.symbol || item.action"
            @click="handleSymbolClick(item)"
            class="keyboard-key"
            :class="{
              'keyboard-key-action': item.action,
              'keyboard-key-special': item.special
            }"
            :title="item.name || item.symbol"
          >
            <span v-if="item.icon" class="key-icon">
              <i :class="item.icon"></i>
            </span>
            <span v-else>{{ item.symbol || item.label }}</span>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { defineEmits, defineProps, computed, ref } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['symbol-click', 'close', 'update:visible'])

// 当前激活的分类
const activeCategory = ref('basic')

// 分类定义
const categories = [
  { id: 'basic', name: '基础' },
  { id: 'operators', name: '运算符' },
  { id: 'relations', name: '关系' },
  { id: 'functions', name: '函数' },
  { id: 'greek', name: '希腊字母' },
  { id: 'actions', name: '功能' }
]

// 符号定义（按分类）
const symbolCategories = {
  basic: [
    { symbol: '(', name: '左括号' },
    { symbol: ')', name: '右括号' },
    { symbol: '[', name: '左方括号' },
    { symbol: ']', name: '右方括号' },
    { symbol: '{', name: '左花括号' },
    { symbol: '}', name: '右花括号' },
    { symbol: ',', name: '逗号' },
    { symbol: '.', name: '点' },
    { symbol: ':', name: '冒号' },
    { symbol: ';', name: '分号' }
  ],
  operators: [
    { symbol: '+', name: '加号' },
    { symbol: '-', name: '减号' },
    { symbol: '×', name: '乘号' },
    { symbol: '÷', name: '除号' },
    { symbol: '±', name: '正负号' },
    { symbol: '·', name: '点乘' },
    { symbol: '^', name: '幂次' },
    { symbol: '_', name: '下标' },
    { symbol: '√', name: '根号', special: true },
    { symbol: '∛', name: '立方根' },
    { symbol: '∑', name: '求和' },
    { symbol: '∏', name: '连乘' }
  ],
  relations: [
    { symbol: '=', name: '等于' },
    { symbol: '≠', name: '不等于' },
    { symbol: '≈', name: '约等于' },
    { symbol: '≤', name: '小于等于' },
    { symbol: '≥', name: '大于等于' },
    { symbol: '<', name: '小于' },
    { symbol: '>', name: '大于' },
    { symbol: '≪', name: '远小于' },
    { symbol: '≫', name: '远大于' },
    { symbol: '≡', name: '恒等于' },
    { symbol: '∝', name: '正比于' },
    { symbol: '∈', name: '属于' }
  ],
  functions: [
    { symbol: 'sin', name: '正弦' },
    { symbol: 'cos', name: '余弦' },
    { symbol: 'tan', name: '正切' },
    { symbol: 'log', name: '对数' },
    { symbol: 'ln', name: '自然对数' },
    { symbol: 'lim', name: '极限' },
    { symbol: '∫', name: '积分' },
    { symbol: '∂', name: '偏导' },
    { symbol: '∠', name: '角' },
    { symbol: '°', name: '度' },
    { symbol: 'π', name: '圆周率' },
    { symbol: '∞', name: '无穷' },
    { symbol: '∵', name: '因为' },
    { symbol: '∴', name: '所以' }
  ],
  greek: [
    { symbol: 'α', name: 'Alpha' },
    { symbol: 'β', name: 'Beta' },
    { symbol: 'γ', name: 'Gamma' },
    { symbol: 'δ', name: 'Delta' },
    { symbol: 'ε', name: 'Epsilon' },
    { symbol: 'θ', name: 'Theta' },
    { symbol: 'λ', name: 'Lambda' },
    { symbol: 'μ', name: 'Mu' },
    { symbol: 'π', name: 'Pi' },
    { symbol: 'ρ', name: 'Rho' },
    { symbol: 'σ', name: 'Sigma' },
    { symbol: 'φ', name: 'Phi' },
    { symbol: 'ω', name: 'Omega' }
  ],
  actions: [
    { action: 'newline', label: '换行', icon: 'fas fa-arrow-down', name: '换行' },
    { action: 'backspace', label: '退格', icon: 'fas fa-backspace', name: '退格' },
    { action: 'space', label: '空格', icon: 'fas fa-minus', name: '空格' },
    { action: 'clear', label: '清空', icon: 'fas fa-eraser', name: '清空' },
    { action: 'left', label: '←', icon: 'fas fa-arrow-left', name: '左移' },
    { action: 'right', label: '→', icon: 'fas fa-arrow-right', name: '右移' },
    { action: 'fraction', label: '分数', icon: 'fas fa-divide', name: '分数' },
    { action: 'power', label: 'x^y', icon: 'fas fa-superscript', name: '次方' },
    { action: 'superscript', label: '上标', icon: 'fas fa-superscript', name: '上标' },
    { action: 'subscript', label: '下标', icon: 'fas fa-subscript', name: '下标' }
  ]
}

// 当前分类的符号
const currentSymbols = computed(() => {
  return symbolCategories[activeCategory.value] || []
})

const handleSymbolClick = (item) => {
  if (item.action) {
    // 功能键
    emit('symbol-click', { type: 'action', action: item.action, name: item.name })
  } else {
    // 符号
    emit('symbol-click', { type: 'symbol', symbol: item.symbol, name: item.name })
  }
}

const close = () => {
  emit('update:visible', false)
  emit('close')
}
</script>

<style scoped>
/* 遮罩层 */
.virtual-keyboard-overlay {
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
  backdrop-filter: blur(4px);
}

/* 键盘容器 */
.virtual-keyboard {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

/* 键盘头部 */
.keyboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.keyboard-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.keyboard-close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f3f4f6;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.keyboard-close-btn:hover {
  background: #e5e7eb;
  color: #333;
  transform: rotate(90deg);
}

/* 分类标签 */
.keyboard-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.75rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: #f3f4f6;
  color: #666;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  font-weight: 500;
}

.tab-btn:hover {
  background: #e5e7eb;
  color: #333;
}

.tab-btn.active {
  background: linear-gradient(145deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.keyboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
  padding-bottom: 0.5rem;
}

/* 自定义滚动条样式 */
.keyboard-grid::-webkit-scrollbar {
  width: 8px;
}

.keyboard-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.keyboard-grid::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.keyboard-grid::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.keyboard-key {
  padding: 0.9rem 0.5rem;
  font-size: 1.3rem;
  font-weight: bold;
  background: linear-gradient(145deg, #ffffff, #f8faff);
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #333;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
  position: relative;
}

.keyboard-key-action {
  background: linear-gradient(145deg, #fef3c7, #fde68a);
  border-color: #fbbf24;
}

.keyboard-key-action:hover {
  background: linear-gradient(145deg, #fbbf24, #f59e0b);
  color: white;
}

.keyboard-key-special {
  font-size: 1.6rem;
}

.key-icon {
  font-size: 1.2rem;
}

.keyboard-key:hover {
  background: linear-gradient(145deg, #667eea, #764ba2);
  color: white;
  border-color: #667eea;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.keyboard-key:active {
  transform: translateY(0) scale(1);
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

/* 特殊符号样式调整 */
.keyboard-key:nth-child(5) {
  /* √ 根号 */
  font-size: 1.8rem;
}

.keyboard-key:nth-child(6) {
  /* ∠ 角 */
  font-size: 1.6rem;
}

/* 动画效果 */
.keyboard-slide-enter-active,
.keyboard-slide-leave-active {
  transition: opacity 0.3s ease;
}

.keyboard-slide-enter-active .virtual-keyboard,
.keyboard-slide-leave-active .virtual-keyboard {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.keyboard-slide-enter-from {
  opacity: 0;
}

.keyboard-slide-enter-from .virtual-keyboard {
  transform: translateY(50px) scale(0.9);
  opacity: 0;
}

.keyboard-slide-leave-to {
  opacity: 0;
}

.keyboard-slide-leave-to .virtual-keyboard {
  transform: translateY(50px) scale(0.9);
  opacity: 0;
}
</style>

