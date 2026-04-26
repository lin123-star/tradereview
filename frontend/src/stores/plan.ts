import { defineStore } from 'pinia'
import { ref } from 'vue'
import { planApi, type DailyPlan, type WatchItem } from '@/api/plan'
import { ElMessage, ElMessageBox } from 'element-plus'

const today = () => new Date().toISOString().slice(0, 10)

function emptyPlan(d: string): DailyPlan {
  return {
    date: d,
    locked: false,
    market_trend: '',
    market_sentiment: '',
    focus_sectors: [],
    market_analysis: '',
    max_loss_limit: '-1.5%',
    max_trade_count: 2,
    emotion_weakness: '',
    watchlist: [],
    entry_plan: '',
    core_hypothesis: '',
  }
}

export const usePlanStore = defineStore('plan', () => {
  const currentDate = ref(today())
  const form = ref<DailyPlan>(emptyPlan(today()))
  const loading = ref(false)
  const saving = ref(false)
  const locking = ref(false)
  const isLoaded = ref(false)

  async function loadPlan(date?: string) {
    const d = date || currentDate.value
    currentDate.value = d
    loading.value = true
    try {
      const data = await planApi.getByDate(d)
      form.value = data
      isLoaded.value = true
    } catch (e: any) {
      if (e?.response?.status === 404) {
        form.value = emptyPlan(d)
        isLoaded.value = false
      } else {
        ElMessage.error('加载计划失败')
      }
    } finally {
      loading.value = false
    }
  }

  async function savePlan() {
    if (form.value.locked) {
      ElMessage.warning('计划已锁定，不可修改')
      return false
    }
    saving.value = true
    try {
      const saved = await planApi.upsert(currentDate.value, form.value)
      form.value = saved
      isLoaded.value = true
      ElMessage.success('计划已保存')
      return true
    } catch (e: any) {
      ElMessage.error(e.message || '保存失败')
      return false
    } finally {
      saving.value = false
    }
  }

  async function lockPlan() {
    try {
      await ElMessageBox.confirm(
        '锁定后计划不可修改，确认锁定？',
        '锁定确认',
        { confirmButtonText: '确认锁定', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return // 用户取消
    }

    // 先保存再锁定
    const ok = await savePlan()
    if (!ok) return

    locking.value = true
    try {
      const locked = await planApi.lock(currentDate.value)
      form.value = locked
      ElMessage.success('计划已锁定，开始交易吧')
    } catch (e: any) {
      ElMessage.error(e.message || '锁定失败')
    } finally {
      locking.value = false
    }
  }

  // ── 观察池操作 ────────────────────────────────────
  function addWatchItem() {
    form.value.watchlist.push({
      symbol: '', name: '', price: null,
      entry_condition: '', stop_loss: null, target: null, note: '',
    })
  }

  function removeWatchItem(idx: number) {
    form.value.watchlist.splice(idx, 1)
  }

  return {
    currentDate, form, loading, saving, locking, isLoaded,
    loadPlan, savePlan, lockPlan, addWatchItem, removeWatchItem,
  }
})