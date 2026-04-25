import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const http = axios.create({ baseURL: BASE, timeout: 90000 })

// 统一处理错误，把后端 detail 透传出来
http.interceptors.response.use(
  res => res,
  err => {
    const detail = err?.response?.data?.detail
    if (detail) err.message = detail
    return Promise.reject(err)
  }
)

export interface VsRow {
  plan: string
  actual: string
}

export interface NewsItem {
  sector: string
  title: string
  source: string
  sentiment: 'positive' | 'negative' | 'neutral'
  sentiment_label: string
}

export interface DailyReview {
  id?: number
  date: string
  pnl_amount: number
  trade_count: number
  win_count: number
  loss_count: number
  // 盘面梳理
  market_overview: string
  plan_accuracy: string
  market_style: string
  market_split: string
  style_desc: string
  leading_sectors: string
  lagging_sectors: string
  sector_summary: string
  // 产业信息
  selected_sectors: string[]
  extra_keywords: string
  ai_news_result: NewsItem[]
  industry_summary: string
  // 操作复盘
  vs_rows: VsRow[]
  best_trade: string
  worst_trade: string
  emotion_state: string
  key_lesson: string
  counterfactual: string
  next_hypothesis: string
  luck_ratio: string
  created_at?: string
  updated_at?: string
}

export interface ArticleOut {
  id: number
  review_date: string
  framework: string
  title: string
  content: string
  word_count: number
  published: number
  created_at: string
}

// ── 复盘 CRUD ─────────────────────────────────────────
export const reviewApi = {
  getByDate: (date: string) =>
    http.get<DailyReview>(`/api/review/${date}`).then(r => r.data),

  getList: (limit = 30) =>
    http.get<DailyReview[]>('/api/review/list', { params: { limit } }).then(r => r.data),

  upsert: (date: string, data: Partial<DailyReview>) =>
    http.post<DailyReview>(`/api/review/${date}`, data).then(r => r.data),

  patch: (date: string, data: Partial<DailyReview>) =>
    http.patch<DailyReview>(`/api/review/${date}`, data).then(r => r.data),
}

// ── AI ────────────────────────────────────────────────
export const aiApi = {
  searchNews: (params: {
    sectors: string[]
    extra_keywords: string
    review_date: string
  }) =>
    http.post<{ news: NewsItem[]; summary: string }>(
      '/api/review/ai/search-news', params,
    ).then(r => r.data),

  generateArticles: (reviewDate: string) =>
    http.post<ArticleOut[]>(
      `/api/review/${reviewDate}/generate-articles`,
    ).then(r => r.data),

  getArticles: (reviewDate: string) =>
    http.get<ArticleOut[]>(`/api/review/${reviewDate}/articles`).then(r => r.data),
}
