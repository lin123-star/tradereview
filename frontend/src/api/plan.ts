import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const http = axios.create({ baseURL: BASE, timeout: 30000 })

http.interceptors.response.use(
  res => res,
  err => {
    const detail = err?.response?.data?.detail
    if (detail) err.message = typeof detail === 'string' ? detail : JSON.stringify(detail)
    return Promise.reject(err)
  }
)

export interface WatchItem {
  symbol: string
  name: string
  price: number | null
  entry_condition: string
  stop_loss: number | null
  target: number | null
  note: string
}

export interface DailyPlan {
  id?: number
  date: string
  locked: boolean
  market_trend: string
  market_sentiment: string
  focus_sectors: string[]
  market_analysis: string
  max_loss_limit: string
  max_trade_count: number
  emotion_weakness: string
  watchlist: WatchItem[]
  entry_plan: string
  core_hypothesis: string
  created_at?: string
  updated_at?: string
  locked_at?: string | null
}

export const planApi = {
  getByDate: (date: string) =>
    http.get<DailyPlan>(`/api/plan/${date}`).then(r => r.data),

  getList: (limit = 30) =>
    http.get<DailyPlan[]>('/api/plan/list', { params: { limit } }).then(r => r.data),

  upsert: (date: string, data: Partial<DailyPlan>) =>
    http.post<DailyPlan>(`/api/plan/${date}`, data).then(r => r.data),

  lock: (date: string) =>
    http.post<DailyPlan>(`/api/plan/${date}/lock`).then(r => r.data),
}