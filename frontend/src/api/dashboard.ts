import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const http = axios.create({ baseURL: BASE, timeout: 15000 })

export interface DashboardData {
  today: string
  today_pnl: number
  today_trade_count: number
  today_plan_locked: boolean
  today_review_done: boolean
  month_pnl: number
  month_trade_count: number
  month_win_count: number
  month_loss_count: number
  month_win_rate: number
  month_avg_pnl_ratio: number
  pending_review_count: number
  pending_audit_count: number
  top_blind_spots: string[]
  pnl_curve: { date: string; pnl: number }[]
  emotion_stats: { emotion: string; win_rate: number; count: number }[]
  recent_trades: {
    id: number
    symbol: string
    name: string
    direction: string
    entry_price: number
    exit_price: number | null
    pnl_amount: number | null
    pnl_ratio: number | null
    status: string
    review_status: string
    emotion: string
    entry_time: string | null
  }[]
}

export const dashboardApi = {
  get: () => http.get<DashboardData>('/api/dashboard').then(r => r.data),
}