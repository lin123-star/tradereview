<template>
  <div class="review-section">
    <div class="section-head">二、产业信息整理</div>

    <el-card shadow="never">
      <template #header>
        <div class="card-header-row">
          <span class="card-title">🔍 AI产业信息检索</span>
          <span class="card-subtitle">自动搜索今日相关产业动态</span>
        </div>
      </template>

      <!-- 板块选择 -->
      <el-form-item label="选择今日关注板块">
        <div class="sector-chips">
          <el-check-tag
            v-for="s in SECTORS"
            :key="s"
            :checked="form.selected_sectors.includes(s)"
            type="success"
            @change="toggleSector(s)"
          >{{ s }}</el-check-tag>
        </div>
      </el-form-item>

      <!-- 补充关键词 -->
      <el-form-item label="补充关键词">
        <el-input
          v-model="form.extra_keywords"
          placeholder="例：茅台渠道价格、宁德固态电池进展..."
          clearable
        />
      </el-form-item>

      <!-- 搜索按钮 -->
      <div class="search-action">
        <el-button
          type="primary"
          plain
          :loading="searching"
          :icon="Search"
          @click="store.searchNews()"
        >
          {{ searching ? 'AI搜索中...' : 'AI搜索今日产业动态' }}
        </el-button>
        <span class="search-hint">调用 web_search 自动抓取归类</span>
      </div>

      <!-- 搜索结果 -->
      <template v-if="newsResult.length">
        <el-divider />
        <div
          v-for="(items, sector) in newsBySector"
          :key="sector"
          class="news-sector"
        >
          <div class="news-sector-head">
            <span class="news-sector-name">{{ sector }}</span>
            <el-tag
              size="small"
              :type="sectorSentiment(items)"
            >
              {{ sectorSentimentLabel(items) }}
            </el-tag>
          </div>
          <div
            v-for="(item, idx) in items"
            :key="idx"
            class="news-item"
          >
            <span
              class="news-dot"
              :class="item.sentiment"
            ></span>
            <div class="news-body">
              <div class="news-title">{{ item.title }}</div>
              <div class="news-meta">
                {{ item.source }} ·
                <span :class="'sentiment-' + item.sentiment">{{ item.sentiment_label }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 摘要输入 -->
      <el-form-item style="margin-top: 14px">
        <template #label>
          <span class="form-label-with-hint">
            产业信息摘要与影响判断
            <span class="label-hint">AI搜索后可编辑，或手动填写</span>
          </span>
        </template>
        <el-input
          v-model="form.industry_summary"
          type="textarea"
          :rows="4"
          placeholder="例：白酒消费数据超预期，茅台批价回升，主线逻辑向好；宁德固态电池进度超预期，欧盟关税短期已price-in。对持仓影响：茅台止盈目标可上调..."
        />
      </el-form-item>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { Search } from '@element-plus/icons-vue'
import { useReviewStore } from '@/stores/review'
import type { NewsItem } from '@/api/review'

const SECTORS = ['白酒', '新能源', '半导体', '军工', '医药', '银行', '地产', 'AI/TMT', '消费', '化工', '有色']

const store = useReviewStore()
const { form, searching, newsResult, newsBySector } = storeToRefs(store)

function toggleSector(s: string) {
  const idx = form.value.selected_sectors.indexOf(s)
  if (idx === -1) {
    form.value.selected_sectors.push(s)
  } else {
    form.value.selected_sectors.splice(idx, 1)
  }
}

function sectorSentiment(items: NewsItem[]) {
  const pos = items.filter(i => i.sentiment === 'positive').length
  const neg = items.filter(i => i.sentiment === 'negative').length
  if (pos > neg) return 'success'
  if (neg > pos) return 'danger'
  return 'info'
}

function sectorSentimentLabel(items: NewsItem[]) {
  const pos = items.filter(i => i.sentiment === 'positive').length
  const neg = items.filter(i => i.sentiment === 'negative').length
  if (pos > neg) return '整体偏多'
  if (neg > pos) return '整体偏空'
  return '中性'
}
</script>

<style scoped>
.review-section { margin-bottom: 8px; }
.section-head {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding-bottom: 8px;
  border-bottom: 2px solid #C8102E;
  display: inline-block;
  margin-bottom: 14px;
}
.card-header-row { display: flex; align-items: center; gap: 10px; }
.card-title { font-size: 13px; font-weight: 600; }
.card-subtitle { font-size: 11px; color: var(--el-text-color-secondary); }

.sector-chips { display: flex; flex-wrap: wrap; gap: 8px; }

.search-action { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.search-hint { font-size: 11px; color: var(--el-text-color-secondary); }

/* 新闻列表 */
.news-sector { margin-bottom: 14px; }
.news-sector:last-child { margin-bottom: 0; }
.news-sector-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 8px;
}
.news-sector-name { font-size: 12px; font-weight: 600; }

.news-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-fill-color-lighter);
}
.news-item:last-child { border-bottom: none; }

.news-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.news-dot.positive { background: #1A7C3E; }
.news-dot.negative { background: #C8102E; }
.news-dot.neutral  { background: #8A95A3; }

.news-body { flex: 1; }
.news-title { font-size: 12.5px; line-height: 1.5; color: var(--el-text-color-primary); margin-bottom: 3px; }
.news-meta  { font-size: 10px; color: var(--el-text-color-secondary); }
.sentiment-positive { color: #1A7C3E; }
.sentiment-negative { color: #C8102E; }
.sentiment-neutral  { color: #8A95A3; }

.form-label-with-hint { display: flex; flex-direction: column; gap: 2px; }
.label-hint { font-size: 11px; color: var(--el-text-color-secondary); font-weight: 400; }
</style>
