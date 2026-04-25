import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reviewApi, aiApi, type DailyReview, type NewsItem, type ArticleOut } from '@/api/review'
import { ElMessage } from 'element-plus'

const today = () => new Date().toISOString().slice(0, 10)

export interface VsRow {
  plan: string
  actual: string
}

export const useReviewStore = defineStore('review', () => {
  // ── 状态 ──────────────────────────────────────────
  const currentDate = ref<string>(today())
  const loading = ref(false)
  const saving = ref(false)
  const searching = ref(false)
  const generating = ref(false)

  const form = ref<DailyReview>(_emptyForm(today()))
  const vsRows = ref<VsRow[]>([{ plan: '', actual: '' }])
  const newsResult = ref<NewsItem[]>([])
  const articles = ref<ArticleOut[]>([])
  const isLoaded = ref(false)

  // ── 按板块分组的新闻 ──────────────────────────────
  const newsBySector = computed(() => {
    const map: Record<string, NewsItem[]> = {}
    for (const item of newsResult.value) {
      if (!map[item.sector]) map[item.sector] = []
      map[item.sector].push(item)
    }
    return map
  })

  // ── 加载当日复盘 ──────────────────────────────────
  async function loadReview(date?: string) {
    const d = date || currentDate.value
    currentDate.value = d
    loading.value = true
    try {
      const data = await reviewApi.getByDate(d)
      form.value = data
      // 恢复 vs_rows
      vsRows.value = (data.vs_rows && data.vs_rows.length)
        ? data.vs_rows
        : [{ plan: '', actual: '' }]
      // 恢复新闻
      newsResult.value = data.ai_news_result || []
      isLoaded.value = true
    } catch (e: any) {
      if (e?.response?.status === 404) {
        _reset(d)
        isLoaded.value = false
      } else {
        ElMessage.error('加载复盘数据失败')
      }
    } finally {
      loading.value = false
    }
  }

  // ── 保存复盘 ──────────────────────────────────────
  async function saveReview() {
    saving.value = true
    try {
      const payload: DailyReview = {
        ...form.value,
        vs_rows: vsRows.value,
        ai_news_result: newsResult.value,
      }
      const saved = await reviewApi.upsert(currentDate.value, payload)
      form.value = saved
      vsRows.value = saved.vs_rows?.length ? saved.vs_rows : [{ plan: '', actual: '' }]
      isLoaded.value = true
      ElMessage.success('复盘已保存')
      return true
    } catch (e) {
      ElMessage.error('保存失败，请检查网络连接')
      return false
    } finally {
      saving.value = false
    }
  }

  // ── AI搜索产业信息 ────────────────────────────────
  async function searchNews() {
    if (!form.value.selected_sectors.length) {
      ElMessage.warning('请至少选择一个板块')
      return
    }
    searching.value = true
    try {
      const result = await aiApi.searchNews({
        sectors: form.value.selected_sectors,
        extra_keywords: form.value.extra_keywords,
        review_date: currentDate.value,
      })
      newsResult.value = result.news
      form.value.industry_summary = result.summary
      ElMessage.success(`搜索完成，共 ${result.news.length} 条产业信息`)
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'AI搜索失败，请检查API配置和代理'
      ElMessage.error(msg)
    } finally {
      searching.value = false
    }
  }

  // ── 生成三框架文章 ────────────────────────────────
  async function generateArticles() {
    const ok = await saveReview()
    if (!ok) return
    generating.value = true
    try {
      const result = await aiApi.generateArticles(currentDate.value)
      articles.value = result
      ElMessage.success('三篇文章生成完成')
    } catch (e: any) {
      const msg = e?.response?.data?.detail || '文章生成失败'
      ElMessage.error(msg)
    } finally {
      generating.value = false
    }
  }

  // ── 加载已有文章 ──────────────────────────────────
  async function loadArticles() {
    try {
      const result = await aiApi.getArticles(currentDate.value)
      if (result.length) {
        articles.value = result
      }
    } catch {
      // 没有文章时静默失败
    }
  }

  // ── vsRows 操作 ───────────────────────────────────
  function addVsRow() {
    vsRows.value.push({ plan: '', actual: '' })
  }

  function removeVsRow(idx: number) {
    if (vsRows.value.length > 1) {
      vsRows.value.splice(idx, 1)
    }
  }

  // ── 内部工具 ──────────────────────────────────────
  function _reset(d: string) {
    form.value = _emptyForm(d)
    vsRows.value = [{ plan: '', actual: '' }]
    newsResult.value = []
    articles.value = []
  }

  return {
    currentDate, loading, saving, searching, generating,
    form, vsRows, newsResult, articles, isLoaded, newsBySector,
    loadReview, saveReview, searchNews, generateArticles, loadArticles,
    addVsRow, removeVsRow,
  }
})

function _emptyForm(d: string): DailyReview {
  return {
    date: d,
    pnl_amount: 0, trade_count: 0, win_count: 0, loss_count: 0,
    market_overview: '', plan_accuracy: '', market_style: '',
    market_split: '', style_desc: '', leading_sectors: '',
    lagging_sectors: '', sector_summary: '',
    selected_sectors: [], extra_keywords: '',
    ai_news_result: [], industry_summary: '',
    vs_rows: [], best_trade: '', worst_trade: '',
    emotion_state: '', key_lesson: '', counterfactual: '',
    next_hypothesis: '', luck_ratio: '',
  }
}
