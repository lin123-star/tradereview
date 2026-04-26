import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const http = axios.create({ baseURL: BASE, timeout: 15000 })

http.interceptors.response.use(
  res => res,
  err => {
    const detail = err?.response?.data?.detail
    if (detail) err.message = typeof detail === 'string' ? detail : JSON.stringify(detail)
    return Promise.reject(err)
  }
)

export interface Strategy {
  id: number
  name: string
  category: string
  description: string
  entry_signal: string
  stop_loss_rule: string
  take_profit_rule: string
  applicable_market: string
  total_count: number
  win_count: number
  loss_count: number
  win_rate: number
  avg_pnl_ratio: number
  avg_win_ratio: number
  avg_loss_ratio: number
  created_at: string
  updated_at: string
}

export interface StrategyCreate {
  name: string
  category?: string
  description?: string
  entry_signal?: string
  stop_loss_rule?: string
  take_profit_rule?: string
  applicable_market?: string
}

export const strategyApi = {
  getAll: () =>
    http.get<Strategy[]>('/api/strategy').then(r => r.data),

  create: (data: StrategyCreate) =>
    http.post<Strategy>('/api/strategy', data).then(r => r.data),

  update: (id: number, data: Partial<StrategyCreate>) =>
    http.put<Strategy>(`/api/strategy/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    http.delete(`/api/strategy/${id}`).then(r => r.data),

  recalc: (id: number) =>
    http.post<Strategy>(`/api/strategy/${id}/recalc`).then(r => r.data),
}