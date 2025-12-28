import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // 将 math-field 识别为 custom element，而不是 Vue 组件
          isCustomElement: (tag) => tag === 'math-field'
        }
      }
    })
  ],
  server: {
    port: 3000,
    open: true
  }
})

