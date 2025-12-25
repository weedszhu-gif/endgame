import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Answer from '../components/Answer.vue'
import Analysis from '../components/Analysis.vue'

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
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

