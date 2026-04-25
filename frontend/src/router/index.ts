import { createRouter, createWebHistory } from 'vue-router'
import DailyReviewView from '@/views/DailyReviewView.vue'
import TradeView from '@/views/TradeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/review' },
    { path: '/review',  name: 'review',  component: DailyReviewView },
    { path: '/trade',   name: 'trade',   component: TradeView },
    // 占位页，后续开发
    { path: '/dashboard', name: 'dashboard', component: DailyReviewView },
    { path: '/plan',      name: 'plan',      component: DailyReviewView },
    { path: '/audit',     name: 'audit',     component: DailyReviewView },
    { path: '/article',   name: 'article',   component: DailyReviewView },
    { path: '/data',      name: 'data',      component: DailyReviewView },
    { path: '/history',   name: 'history',   component: TradeView },
  ],
})

export default router
