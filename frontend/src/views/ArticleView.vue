<template>
  <div class="article-page">

    <div class="page-header">
      <div>
        <h2 class="page-title">文章工坊</h2>
        <div class="page-sub">基于真实复盘数据 · AI生成 · 三框架输出</div>
      </div>
    </div>

    <!-- 选择复盘日期生成文章 -->
    <el-card shadow="never" class="gen-card">
      <template #header>
        <span class="card-title">⚡ 生成新文章</span>
      </template>

      <div class="gen-row">
        <div class="gen-field">
          <span class="gen-label">选择复盘日期</span>
          <el-date-picker
            v-model="genDate"
            type="date"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            :clearable="false"
            style="width:180px"
          />
        </div>

        <!-- 素材来源检查 -->
        <div class="source-checks">
          <div
            v-for="src in sourceStatus"
            :key="src.label"
            :class="['source-chip', src.ready ? 'ready' : 'missing']"
          >
            <span>{{ src.ready ? '✅' : '⬜' }}</span>
            <span>{{ src.label }}</span>
          </div>
        </div>

        <el-button
          type="primary"
          :loading="generating"
          :disabled="!genDate"
          style="background:#C8102E;border-color:#C8102E;margin-left:auto"
          @click="generate"
        >
          生成三框架文章
        </el-button>
      </div>

      <div v-if="generating" class="gen-tip">
        <el-icon class="is-loading"><Loading /></el-icon>
        AI 正在基于复盘数据生成三篇文章，约需 30-60 秒...
      </div>
    </el-card>

    <!-- 文章展示区 -->
    <div v-if="articles.length" class="articles-wrap">
      <el-tabs v-model="activeTab" type="border-card" class="art-tabs">
        <el-tab-pane
          v-for="art in articles"
          :key="art.framework"
          :label="fwLabel(art.framework)"
          :name="art.framework"
        >
          <div class="art-meta-row">
            <el-tag :type="fwTagType(art.framework)" size="small">
              {{ fwDesc(art.framework) }}
            </el-tag>
            <span class="art-meta-info">约 {{ art.word_count }} 字</span>
            <span class="art-meta-info">非投资建议声明 ✓</span>
            <div style="margin-left:auto;display:flex;gap:8px">
              <el-button size="small" @click="copyArticle(art)">复制全文</el-button>
              <el-button
                size="small"
                type="primary"
                :style="fwBtnStyle(art.framework)"
                @click="pushToWechat(art)"
              >推送公众号草稿箱</el-button>
            </div>
          </div>

          <div class="art-card">
            <div class="art-title-area">
              <div
                class="art-title"
                contenteditable="true"
                @blur="e => art.title = (e.target as HTMLElement).innerText.trim()"
              >{{ art.title }}</div>
              <div class="art-title-hint">点击标题可直接编辑</div>
            </div>
            <div
              class="art-body"
              contenteditable="true"
              @blur="e => art.content = (e.target as HTMLElement).innerText.trim()"
            >{{ art.content }}</div>
          </div>

          <div class="art-footer-row">
            <el-button size="small" @click="regenerateSingle(art.framework)">
              重新生成此框架
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 历史文章列表 -->
    <el-card shadow="never" class="history-card">
      <template #header>
        <div class="card-header-row">
          <span class="card-title">📚 历史发布文章</span>
          <el-select
            v-model="historyDate"
            placeholder="选择日期筛选"
            clearable
            style="width:160px"
            size="small"
            @change="loadHistoryArticles"
          >
            <el-option
              v-for="d in reviewDates"
              :key="d"
              :label="d"
              :value="d"
            />
          </el-select>
        </div>
      </template>

      <div v-if="!historyArticles.length" class="history-empty">
        暂无历史文章，先选择日期生成文章吧
      </div>

      <el-table
        v-else
        :data="historyArticles"
        stripe
        style="width:100%"
      >
        <el-table-column label="框架" width="120">
          <template #default="{ row }">
            <el-tag :type="fwTagType(row.framework)" size="small">
              {{ fwLabel(row.framework) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标题" min-width="280">
          <template #default="{ row }">
            <span style="font-family:'Noto Serif SC',serif;font-size:13px">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="来源日期" width="120">
          <template #default="{ row }">
            <span style="font-size:12px;color:#8A95A3">{{ row.review_date }}</span>
          </template>
        </el-table-column>
        <el-table-column label="字数" width="80">
          <template #default="{ row }">
            <span style="font-size:12px">{{ row.word_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.published ? 'success' : 'info'" size="small">
              {{ row.published ? '已推送' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" width="150">
          <template #default="{ row }">
            <span style="font-size:11px;color:#8A95A3">
              {{ row.created_at?.slice(0,16).replace('T',' ') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130">
          <template #default="{ row }">
            <el-button size="small" plain @click="viewArticle(row)">查看</el-button>
            <el-button size="small" plain @click="copyArticle(row)" style="margin-left:4px">复制</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import { aiApi, reviewApi, type ArticleOut } from '@/api/review'
import { planApi } from '@/api/plan'

const today = new Date().toISOString().slice(0, 10)
const genDate = ref(today)
const generating = ref(false)
const articles = ref<ArticleOut[]>([])
const activeTab = ref('resonance')
const historyDate = ref('')
const historyArticles = ref<ArticleOut[]>([])
const reviewDates = ref<string[]>([])

// 素材来源状态（简化版，实际可以调接口检查）
const sourceStatus = computed(() => [
  { label: '每日计划', ready: true },
  { label: '交易记录', ready: true },
  { label: 'AI审讯', ready: true },
  { label: '每日复盘', ready: true },
])

// ── 生成文章 ──────────────────────────────────────────
async function generate() {
  if (!genDate.value) return
  generating.value = true
  try {
    // 先尝试加载已有文章
    const existing = await aiApi.getArticles(genDate.value)
    if (existing.length) {
      articles.value = existing
      activeTab.value = existing[0].framework
      ElMessage.info('已加载该日期已有文章，重新生成请点击「重新生成此框架」')
      return
    }
    // 生成新文章
    const result = await aiApi.generateArticles(genDate.value)
    articles.value = result
    activeTab.value = result[0]?.framework || 'resonance'
    ElMessage.success('三篇文章生成完成')
    await loadReviewDates()
  } catch (e: any) {
    ElMessage.error(e.message || '生成失败，请确认已保存该日期的复盘内容')
  } finally {
    generating.value = false
  }
}

async function regenerateSingle(framework: string) {
  ElMessage.info('重新生成功能待实现，当前先重新生成全部')
  await generate()
}

// ── 历史文章 ──────────────────────────────────────────
async function loadReviewDates() {
  try {
    const list = await reviewApi.getList(90)
    reviewDates.value = list.map(r => r.date as unknown as string)
    if (reviewDates.value.length && !historyDate.value) {
      historyDate.value = reviewDates.value[0]
      await loadHistoryArticles()
    }
  } catch {}
}

async function loadHistoryArticles() {
  if (!historyDate.value) return
  try {
    historyArticles.value = await aiApi.getArticles(historyDate.value)
  } catch {
    historyArticles.value = []
  }
}

// ── 工具函数 ──────────────────────────────────────────
function fwLabel(fw: string) {
  return { resonance: '① 散户共鸣', methodology: '② 方法论', reflection: '③ 认知反思' }[fw] || fw
}

function fwDesc(fw: string) {
  return { resonance: '情绪叙事', methodology: '规则提炼', reflection: '深度反思' }[fw] || fw
}

function fwTagType(fw: string): 'danger' | 'primary' | 'success' {
  return { resonance: 'danger', methodology: 'primary', reflection: 'success' }[fw] as any || 'info'
}

function fwBtnStyle(fw: string) {
  const colors: Record<string, string> = {
    resonance: '#C8102E', methodology: '#1565C0', reflection: '#1A7C3E'
  }
  const c = colors[fw] || '#C8102E'
  return { background: c, borderColor: c }
}

function copyArticle(art: ArticleOut) {
  const text = `${art.title}\n\n${art.content}`
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

function pushToWechat(art: ArticleOut) {
  ElNotification({
    title: '推送草稿箱',
    message: '公众号草稿箱推送功能（ScriptCat方案）待接入',
    type: 'info',
    duration: 3000,
  })
}

function viewArticle(art: ArticleOut) {
  articles.value = [art]
  activeTab.value = art.framework
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  // 加载今日已有文章
  try {
    const existing = await aiApi.getArticles(today)
    if (existing.length) {
      articles.value = existing
      activeTab.value = existing[0].framework
    }
  } catch {}
  await loadReviewDates()
})
</script>

<style scoped>
.article-page { padding: 20px 24px; max-width: 1100px; margin: 0 auto; }

.page-header { margin-bottom: 18px; }
.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 700; margin: 0;
}
.page-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

/* 生成区 */
.gen-card { margin-bottom: 16px; border-radius: 4px; }
.card-title { font-size: 13px; font-weight: 600; }

.gen-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.gen-field { display: flex; align-items: center; gap: 10px; }
.gen-label { font-size: 13px; color: var(--el-text-color-secondary); white-space: nowrap; }

.source-checks { display: flex; gap: 8px; flex-wrap: wrap; }
.source-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  border: 1px solid;
}
.source-chip.ready {
  background: #EAF5EE;
  border-color: #A8D5B8;
  color: #1A7C3E;
}
.source-chip.missing {
  background: var(--el-fill-color-lighter);
  border-color: var(--el-border-color);
  color: var(--el-text-color-secondary);
}

.gen-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 文章展示 */
.articles-wrap { margin-bottom: 16px; }

.art-tabs { border-radius: 4px; }

.art-meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.art-meta-info { font-size: 11px; color: var(--el-text-color-secondary); }

.art-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.art-title-area {
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--el-border-color);
}

.art-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  outline: none;
  cursor: text;
  min-height: 1.5em;
}

.art-title-hint {
  font-size: 10px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}

.art-body {
  padding: 16px 20px;
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  line-height: 1.9;
  color: var(--el-text-color-primary);
  outline: none;
  cursor: text;
  min-height: 200px;
  white-space: pre-wrap;
}

.art-footer-row {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

/* 历史文章 */
.history-card { border-radius: 4px; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.history-empty {
  padding: 30px;
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>