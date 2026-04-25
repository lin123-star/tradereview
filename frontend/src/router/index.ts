import { createRouter, createWebHistory } from 'vue-router'
import DailyReviewView from '@/views/DailyReviewView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/review',
    },
    {
      path: '/review',
      name: 'review',
      component: DailyReviewView,
    },
    // 后续模块占位
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DailyReviewView.vue') },
    { path: '/plan',     name: 'plan',      component: () => import('@/views/DailyReviewView.vue') },
    { path: '/audit',   name: 'audit',     component: () => import('@/views/DailyReviewView.vue') },
    { path: '/article', name: 'article',   component: () => import('@/views/DailyReviewView.vue') },
  ],
})

export default router
