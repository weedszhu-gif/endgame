import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

// 导入并注册 MathLive
import { MathfieldElement } from 'mathlive'
import 'mathlive/fonts.css'
import 'mathlive/static.css'

// 注册 MathLive custom element
if (typeof window !== 'undefined' && !customElements.get('math-field')) {
  customElements.define('math-field', MathfieldElement)
}

createApp(App).use(router).mount('#app')

