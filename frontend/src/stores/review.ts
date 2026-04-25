import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reviewApi, aiApi, type DailyReview, type NewsItem, type ArticleOut } from '@/api/review'
import { ElMessage } from 'element-plus'

const today = () => new Date().toISOString().slice(0, 10)

export const useReviewStore = defineStore('review', () => {
  // ── 状态 ──────────────────────────────────────────
  const currentDate = ref<string>(today())
  const loading = ref(false)
  const saving = ref(false)
  const searching = ref(false)
  const generating = ref(false)

  const form = ref<DailyReview>({
    date: today(),
    pnl_amount: 0,
    trade_count: 0,
    win_count: 0,
    loss_count: 0,
    market_overview: '',
    plan_accuracy: '',
    market_style: '',
    market_split: '',
    style_desc: '',
    leading_sectors: '',
    lagging_sectors: '',
    sector_summary: '',
    selected_sectors: [],
    extra_keywords: '',
    ai_news_result: [],
    industry_summary: '',
    best_trade: '',
    worst_trade: '',
    emotion_state: '',
    key_lesson: '',
    counterfactual: '',
    next_hypothesis: '',
    luck_ratio: '',
  })

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
      Object.assign(form.value, data)
      newsResult.value = data.ai_news_result || []
      isLoaded.value = true
    } catch (e: any) {
      if (e?.response?.status === 404) {
        // 当日无记录，重置表单
        resetForm(d)
        isLoaded.value = false
      }
    } finally {
      loading.value = false
    }
  }

  // ── 保存复盘 ──────────────────────────────────────
  async function saveReview() {
    saving.value = true
    try {
      const payload = {
        ...form.value,
        ai_news_result: newsResult.value,
      }
      const saved = await reviewApi.upsert(currentDate.value, payload)
      Object.assign(form.value, saved)
      isLoaded.value = true
      ElMessage.success('复盘已保存')
      return true
    } catch (e) {
      ElMessage.error('保存失败，请检查网络')
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
    } catch (e) {
      ElMessage.error('AI搜索失败，请检查API配置')
    } finally {
      searching.value = false
    }
  }

  // ── 生成三框架文章 ────────────────────────────────
  async function generateArticles() {
    // 先保存再生成
    const ok = await saveReview()
    if (!ok) return
    generating.value = true
    try {
      const result = await aiApi.generateArticles(currentDate.value)
      articles.value = result
      ElMessage.success('三篇文章生成完成')
    } catch (e) {
      ElMessage.error('文章生成失败')
    } finally {
      generating.value = false
    }
  }

  async function loadArticles() {
    try {
      articles.value = await aiApi.getArticles(currentDate.value)
    } catch {}
  }

  function resetForm(date: string) {
    form.value = {
      date,
      pnl_amount: 0, trade_count: 0, win_count: 0, loss_count: 0,
      market_overview: '', plan_accuracy: '', market_style: '',
      market_split: '', style_desc: '', leading_sectors: '',
      lagging_sectors: '', sector_summary: '', selected_sectors: [],
      extra_keywords: '', ai_news_result: [], industry_summary: '',
      best_trade: '', worst_trade: '', emotion_state: '', key_lesson: '',
      counterfactual: '', next_hypothesis: '', luck_ratio: '',
    }
    newsResult.value = []
  }

  return {
    currentDate, loading, saving, searching, generating,
    form, newsResult, articles, isLoaded, newsBySector,
    loadReview, saveReview, searchNews, generateArticles, loadArticles,
  }
})
