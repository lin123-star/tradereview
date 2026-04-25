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

export type Direction = 'buy' | 'sell' | 'add' | 'reduce'
export type TradeStatus = 'open' | 'closed'
export type ReviewStatus = 'pending' | 'reviewing' | 'done'

export interface TradeOut {
  id: number
  symbol: string
  name: string
  direction: Direction
  entry_price: number
  entry_time: string
  position_ratio: number
  entry_logic: string
  entry_locked: boolean
  exit_price: number | null
  exit_time: string | null
  exit_logic: string
  pnl_amount: number | null
  pnl_ratio: number | null
  emotion: string
  exit_emotion: string
  strategy: string
  market_env: string
  plan_followed: string
  lesson: string
  counterfactual: string
  hypothesis: string
  uncertainty: number
  review_date: string | null
  status: TradeStatus
  review_status: ReviewStatus
  created_at: string
  updated_at: string
}

export interface TradeStep1Form {
  symbol: string
  name: string
  direction: Direction
  entry_price: number | null
  entry_time: string
  position_ratio: number
  entry_logic: string
  market_env: string
  strategy: string
  emotion: string
  review_date: string | null
}

export interface TradeStep2Form {
  exit_price: number | null
  exit_time: string
  exit_logic: string
  exit_emotion: string
  plan_followed: string
  lesson: string
  counterfactual: string
  hypothesis: string
  uncertainty: number
}

export interface TradeListResult {
  total: number
  offset: number
  limit: number
  items: TradeOut[]
}

export const tradeApi = {
  // Step1 入场录入
  create: (data: TradeStep1Form) =>
    http.post<TradeOut>('/api/trade', data).then(r => r.data),

  // Step2 出场录入
  complete: (tradeId: number, data: TradeStep2Form) =>
    http.post<TradeOut>(`/api/trade/${tradeId}/complete`, data).then(r => r.data),

  // 查询列表
  list: (params?: {
    status?: string
    review_status?: string
    symbol?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }) => http.get<TradeListResult>('/api/trade', { params }).then(r => r.data),

  // 待复盘列表
  pendingReview: () =>
    http.get<TradeOut[]>('/api/trade/pending-review').then(r => r.data),

  // 单条查询
  getById: (id: number) =>
    http.get<TradeOut>(`/api/trade/${id}`).then(r => r.data),

  // 更新审讯状态
  updateReviewStatus: (id: number, review_status: ReviewStatus) =>
    http.patch<TradeOut>(`/api/trade/${id}/review-status`, null, {
      params: { review_status },
    }).then(r => r.data),

  // 删除（仅持仓中）
  delete: (id: number) =>
    http.delete(`/api/trade/${id}`).then(r => r.data),
}
