import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import PlanView from '@/views/PlanView.vue'
import TradeView from '@/views/TradeView.vue'
import AuditView from '@/views/AuditView.vue'
import DailyReviewView from '@/views/DailyReviewView.vue'
import ArticleView from '@/views/ArticleView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',          redirect: '/dashboard' },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/plan',      name: 'plan',      component: PlanView },
    { path: '/trade',     name: 'trade',     component: TradeView },
    { path: '/audit',     name: 'audit',     component: AuditView },
    { path: '/review',    name: 'review',    component: DailyReviewView },
    { path: '/article',   name: 'article',   component: ArticleView },
    { path: '/history',   name: 'history',   component: TradeView },
  ],
})

export default router