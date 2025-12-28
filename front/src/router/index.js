import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Answer from '../components/Answer.vue'
import Analysis from '../components/Analysis.vue'
import Records from '../components/Records.vue'

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
  },
  {
    path: '/records',
    name: 'Records',
    component: Records
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

