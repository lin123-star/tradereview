<template>
  <div class="review-page">

    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">每日行情复盘</h2>
        <div class="page-sub">
          <el-date-picker
            v-model="currentDate"
            type="date"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            :clearable="false"
            size="small"
            @change="store.loadReview(currentDate)"
          />
          <span class="date-hint">收盘后填写</span>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="handleSave" :loading="saving">
          保存复盘
        </el-button>
        <el-button
          type="primary"
          :loading="generating"
          @click="handleGenerate"
          style="background:#C8102E;border-color:#C8102E"
        >
          保存 &amp; 生成三框架文章 →
        </el-button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-mask">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <span>加载复盘数据...</span>
    </div>

    <template v-else>
      <el-form
        ref="formRef"
        :model="form"
        label-position="top"
        label-width="auto"
        class="review-form"
      >
        <!-- 三个模块 -->
        <MarketSection />
        <IndustrySection />
        <OperationSection />
      </el-form>

      <!-- 底部保存 -->
      <div class="page-footer">
        <el-button @click="handleSave" :loading="saving" size="large">
          保存复盘
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="generating"
          @click="handleGenerate"
          style="background:#C8102E;border-color:#C8102E"
        >
          {{ generating ? 'AI生成中...' : '保存 & 生成三框架文章 →' }}
        </el-button>
      </div>

      <!-- 生成文章结果 -->
      <div v-if="articles.length" class="articles-area">
        <div class="section-head" style="margin-bottom:14px">文章工坊 · 生成结果</div>
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane
            v-for="art in articles"
            :key="art.framework"
            :label="FW_LABELS[art.framework] || art.framework"
            :name="art.framework"
          >
            <div class="article-card">
              <div class="article-title-wrap">
                <div
                  class="article-title"
                  contenteditable="true"
                  @input="art.title = ($event.target as HTMLElement).innerText"
                >{{ art.title }}</div>
                <div class="article-title-hint">点击标题可直接编辑</div>
              </div>
              <div
                class="article-body"
                contenteditable="true"
                @input="art.content = ($event.target as HTMLElement).innerText"
              >{{ art.content }}</div>
              <div class="article-footer">
                <span class="art-meta">约 {{ art.word_count }} 字</span>
                <span class="art-meta">非投资建议声明 ✓</span>
                <div style="margin-left:auto;display:flex;gap:8px">
                  <el-button size="small" @click="copyArticle(art)">复制全文</el-button>
                  <el-button size="small" type="primary" style="background:#C8102E;border-color:#C8102E">
                    推送公众号草稿箱
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useReviewStore } from '@/stores/review'
import MarketSection from '@/components/review/MarketSection.vue'
import IndustrySection from '@/components/review/IndustrySection.vue'
import OperationSection from '@/components/review/OperationSection.vue'
import type { ArticleOut } from '@/api/review'

const FW_LABELS: Record<string, string> = {
  resonance: '① 散户共鸣',
  methodology: '② 方法论',
  reflection: '③ 认知反思',
}

const store = useReviewStore()
const { form, currentDate, loading, saving, generating, articles } = storeToRefs(store)

const activeTab = ref('resonance')

onMounted(async () => {
  await store.loadReview()
  await store.loadArticles()
  if (articles.value.length) activeTab.value = articles.value[0].framework
})

async function handleSave() {
  await store.saveReview()
}

async function handleGenerate() {
  await store.generateArticles()
  if (articles.value.length) {
    activeTab.value = articles.value[0].framework
    // 滚动到文章区域
    document.querySelector('.articles-area')?.scrollIntoView({ behavior: 'smooth' })
  }
}

function copyArticle(art: ArticleOut) {
  const text = `${art.title}\n\n${art.content}`
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}
</script>

<style scoped>
.review-page {
  padding: 20px 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 16px;
}

.header-left { display: flex; flex-direction: column; gap: 8px; }

.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin: 0;
}

.page-sub { display: flex; align-items: center; gap: 10px; }
.date-hint { font-size: 12px; color: var(--el-text-color-secondary); }
.header-right { display: flex; gap: 10px; flex-shrink: 0; }

.loading-mask {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px;
  color: var(--el-text-color-secondary);
}

.review-form { display: flex; flex-direction: column; gap: 20px; }

.page-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
}

/* 文章区域 */
.articles-area { margin-top: 32px; }

.section-head {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding-bottom: 8px;
  border-bottom: 2px solid #C8102E;
  display: inline-block;
}

.article-card { display: flex; flex-direction: column; }

.article-title-wrap {
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--el-border-color);
}

.article-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  outline: none;
  cursor: text;
  min-height: 1.5em;
}

.article-title-hint {
  font-size: 10px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}

.article-body {
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

.article-footer {
  padding: 10px 20px;
  border-top: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--el-fill-color-lighter);
}

.art-meta { font-size: 11px; color: var(--el-text-color-secondary); }
</style>
