import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Answer from '../components/Answer.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/answer',
    name: 'Answer',
    component: Answer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

