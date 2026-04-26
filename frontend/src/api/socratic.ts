import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const http = axios.create({ baseURL: BASE, timeout: 60000 })

http.interceptors.response.use(
  res => res,
  err => {
    const detail = err?.response?.data?.detail
    if (detail) err.message = typeof detail === 'string' ? detail : JSON.stringify(detail)
    return Promise.reject(err)
  }
)

export interface Message {
  role: 'ai' | 'user'
  content: string
}

export interface SessionOut {
  id: number
  trade_id: number
  messages: Message[]
  blind_spots: string[]
  summary: string
  status: 'active' | 'completed'
  created_at: string
  updated_at: string
}

export interface ReplyResponse {
  session_id: number
  ai_message: string
  blind_spots: string[]
  status: 'active' | 'completed'
  summary: string
}

export const socraticApi = {
  start: (trade_id: number) =>
    http.post<SessionOut>('/api/socratic/start', { trade_id }).then(r => r.data),

  reply: (session_id: number, user_message: string) =>
    http.post<ReplyResponse>('/api/socratic/reply', { session_id, user_message })
      .then(r => r.data),

  getByTrade: (trade_id: number) =>
    http.get<SessionOut[]>(`/api/socratic/trade/${trade_id}`).then(r => r.data),

  getSession: (session_id: number) =>
    http.get<SessionOut>(`/api/socratic/session/${session_id}`).then(r => r.data),
}
