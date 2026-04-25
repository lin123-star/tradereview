import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tradeApi, type TradeOut, type TradeStep1Form, type TradeStep2Form } from '@/api/trade'
import { ElMessage } from 'element-plus'

export const useTradeStore = defineStore('trade', () => {
  const trades = ref<TradeOut[]>([])
  const total = ref(0)
  const loading = ref(false)
  const submitting = ref(false)
  const pendingReviews = ref<TradeOut[]>([])

  // ── 加载列表 ──────────────────────────────────────
  async function loadList(params?: Parameters<typeof tradeApi.list>[0]) {
    loading.value = true
    try {
      const res = await tradeApi.list(params)
      trades.value = res.items
      total.value = res.total
    } catch (e: any) {
      ElMessage.error(e.message || '加载交易记录失败')
    } finally {
      loading.value = false
    }
  }

  // ── 加载待复盘 ────────────────────────────────────
  async function loadPendingReviews() {
    try {
      pendingReviews.value = await tradeApi.pendingReview()
    } catch (e: any) {
      ElMessage.error(e.message || '加载待复盘记录失败')
    }
  }

  // ── Step1 入场录入 ────────────────────────────────
  async function createTrade(form: TradeStep1Form): Promise<TradeOut | null> {
    submitting.value = true
    try {
      const trade = await tradeApi.create(form)
      ElMessage.success(`入场记录已创建并锁定：${trade.symbol} ${dirLabel(trade.direction)} @ ${trade.entry_price}`)
      await loadList()
      return trade
    } catch (e: any) {
      ElMessage.error(e.message || '录入失败')
      return null
    } finally {
      submitting.value = false
    }
  }

  // ── Step2 出场录入 ────────────────────────────────
  async function completeTrade(tradeId: number, form: TradeStep2Form): Promise<TradeOut | null> {
    submitting.value = true
    try {
      const trade = await tradeApi.complete(tradeId, form)
      const pnl = trade.pnl_amount ?? 0
      const pnlStr = pnl >= 0 ? `+¥${pnl.toFixed(0)}` : `-¥${Math.abs(pnl).toFixed(0)}`
      ElMessage.success(`出场记录已保存：${trade.symbol} ${pnlStr}`)
      await loadList()
      return trade
    } catch (e: any) {
      ElMessage.error(e.message || '出场录入失败')
      return null
    } finally {
      submitting.value = false
    }
  }

  // ── 删除 ──────────────────────────────────────────
  async function deleteTrade(id: number) {
    try {
      await tradeApi.delete(id)
      ElMessage.success('已删除')
      await loadList()
    } catch (e: any) {
      ElMessage.error(e.message || '删除失败')
    }
  }

  function dirLabel(dir: string) {
    const map: Record<string, string> = {
      buy: '买入', sell: '卖出', add: '加仓', reduce: '减仓',
    }
    return map[dir] || dir
  }

  return {
    trades, total, loading, submitting, pendingReviews,
    loadList, loadPendingReviews, createTrade, completeTrade, deleteTrade,
  }
})
