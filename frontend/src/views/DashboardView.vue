<template>
  <div class="dash-page">

    <!-- 顶部欢迎 -->
    <div class="dash-header">
      <div>
        <h2 class="dash-title">仪表台</h2>
        <div class="dash-sub">{{ todayStr }} · 欢迎回来</div>
      </div>
      <el-button :loading="loading" @click="loadData">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <div v-if="loading" class="loading-wrap">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <template v-else-if="data">

      <!-- 今日状态栏 -->
      <div class="today-bar">
        <div class="today-item" :class="data.today_plan_locked ? 'done' : 'todo'">
          <el-icon>
            <component :is="data.today_plan_locked ? 'Lock' : 'EditPen'" />
          </el-icon>
          <span>今日计划</span>
          <span class="today-status">{{ data.today_plan_locked ? '已锁定' : '未填写' }}</span>
          <el-button
            v-if="!data.today_plan_locked"
            size="small" type="primary" plain
            style="margin-left:auto"
            @click="$router.push('/plan')"
          >去填写</el-button>
        </div>
        <div class="today-divider"></div>
        <div class="today-item" :class="data.today_review_done ? 'done' : 'todo'">
          <el-icon><Document /></el-icon>
          <span>今日复盘</span>
          <span class="today-status">{{ data.today_review_done ? '已完成' : '未填写' }}</span>
          <el-button
            v-if="!data.today_review_done"
            size="small" type="primary" plain
            style="margin-left:auto"
            @click="$router.push('/review')"
          >去复盘</el-button>
        </div>
        <div class="today-divider"></div>
        <div class="today-item" :class="data.pending_review_count > 0 ? 'todo' : 'done'">
          <el-icon><Warning /></el-icon>
          <span>待复盘交易</span>
          <span class="today-status" :style="data.pending_review_count > 0 ? 'color:#C8102E' : ''">
            {{ data.pending_review_count }} 笔
          </span>
          <el-button
            v-if="data.pending_review_count > 0"
            size="small" type="danger" plain
            style="margin-left:auto"
            @click="$router.push('/audit')"
          >去审讯</el-button>
        </div>
      </div>

      <!-- 核心指标卡片 -->
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">今日盈亏</div>
          <div
            class="stat-value"
            :class="data.today_pnl >= 0 ? 'pos' : 'neg'"
          >
            {{ data.today_pnl >= 0 ? '+' : '' }}¥{{ data.today_pnl.toFixed(0) }}
          </div>
          <div class="stat-sub">今日操作 {{ data.today_trade_count }} 笔</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">本月收益</div>
          <div
            class="stat-value"
            :class="data.month_pnl >= 0 ? 'pos' : 'neg'"
          >
            {{ data.month_pnl >= 0 ? '+' : '' }}¥{{ data.month_pnl.toFixed(0) }}
          </div>
          <div class="stat-sub">
            共 {{ data.month_trade_count }} 笔 ·
            均盈亏 {{ (data.month_avg_pnl_ratio * 100).toFixed(2) }}%
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">本月胜率</div>
          <div class="stat-value neutral">
            {{ (data.month_win_rate * 100).toFixed(1) }}%
          </div>
          <div class="stat-sub">
            {{ data.month_win_count }}胜 / {{ data.month_loss_count }}负
          </div>
        </div>

        <div class="stat-card blind-card">
          <div class="stat-label">最高频认知盲区</div>
          <div v-if="data.top_blind_spots.length" class="blind-list">
            <div
              v-for="(bs, i) in data.top_blind_spots"
              :key="bs"
              class="blind-item"
            >
              <span class="blind-rank">{{ i + 1 }}</span>
              <span class="blind-name">{{ bs }}</span>
            </div>
          </div>
          <div v-else class="stat-sub">暂无数据（完成审讯后显示）</div>
        </div>
      </div>

      <!-- 图表区 -->
      <div class="chart-grid">

        <!-- 盈亏曲线 -->
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span class="card-title">📈 近30日盈亏曲线</span>
          </template>
          <div v-if="!data.pnl_curve.length" class="chart-empty">
            暂无数据
          </div>
          <div v-else class="bar-chart-wrap">
            <div class="bar-chart-area">
              <div
                v-for="item in data.pnl_curve"
                :key="item.date"
                class="bar-col"
              >
                <div class="bar-val-label" :class="item.pnl >= 0 ? 'pos' : 'neg'">
                  {{ item.pnl >= 0 ? '+' : '' }}{{ item.pnl.toFixed(0) }}
                </div>
                <div class="bar-container">
                  <div
                    class="bar-fill"
                    :class="item.pnl >= 0 ? 'pos' : 'neg'"
                    :style="barStyle(item.pnl)"
                  ></div>
                </div>
                <div class="bar-date">{{ item.date.slice(5) }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 情绪胜率 -->
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span class="card-title">🧠 情绪 · 胜率（本月）</span>
          </template>
          <div v-if="!data.emotion_stats.length" class="chart-empty">
            暂无数据
          </div>
          <div v-else class="emotion-list">
            <div
              v-for="item in data.emotion_stats"
              :key="item.emotion"
              class="emotion-row"
            >
              <span class="emotion-label">{{ item.emotion }}</span>
              <div class="emotion-bar-bg">
                <div
                  class="emotion-bar-fill"
                  :style="{
                    width: (item.win_rate * 100) + '%',
                    background: emotionColor(item.win_rate)
                  }"
                ></div>
              </div>
              <span
                class="emotion-rate"
                :style="{ color: emotionColor(item.win_rate) }"
              >
                {{ (item.win_rate * 100).toFixed(0) }}%
              </span>
              <span class="emotion-count">{{ item.count }}笔</span>
            </div>
          </div>
          <div
            v-if="data.emotion_stats.length >= 2"
            class="emotion-insight"
          >
            {{ emotionInsight }}
          </div>
        </el-card>
      </div>

      <!-- 近期交易 -->
      <el-card shadow="never" class="recent-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">📊 近期交易记录</span>
            <el-button size="small" plain @click="$router.push('/trade')">
              全部记录 →
            </el-button>
          </div>
        </template>

        <el-table :data="data.recent_trades" stripe style="width:100%">
          <el-table-column label="标的" width="130">
            <template #default="{ row }">
              <div class="sym-block">
                <span class="sym-code">{{ row.symbol }}</span>
                <span class="sym-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="方向" width="80">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="['买入','加仓'].includes(row.direction) ? 'success' : 'danger'"
              >{{ row.direction }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入场价" width="90">
            <template #default="{ row }">
              <span style="font-family:'JetBrains Mono',monospace">{{ row.entry_price }}</span>
            </template>
          </el-table-column>
          <el-table-column label="盈亏" width="120">
            <template #default="{ row }">
              <template v-if="row.pnl_amount != null">
                <div :class="row.pnl_amount >= 0 ? 'pnl-pos' : 'pnl-neg'">
                  {{ row.pnl_amount >= 0 ? '+' : '' }}¥{{ row.pnl_amount.toFixed(0) }}
                </div>
                <div style="font-size:10px;color:#8A95A3">
                  {{ row.pnl_amount >= 0 ? '+' : '' }}{{ (row.pnl_ratio * 100).toFixed(2) }}%
                </div>
              </template>
              <span v-else style="color:#8A95A3;font-size:12px">持仓中</span>
            </template>
          </el-table-column>
          <el-table-column label="情绪" width="80">
            <template #default="{ row }">
              <span style="font-size:12px">{{ row.emotion }}</span>
            </template>
          </el-table-column>
          <el-table-column label="复盘状态" width="100">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="reviewTagType(row.review_status)"
              >{{ reviewLabel(row.review_status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入场时间" width="140">
            <template #default="{ row }">
              <span style="font-size:12px;color:#8A95A3">
                {{ row.entry_time ? row.entry_time.slice(0,16).replace('T',' ') : '' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button
                v-if="row.review_status === 'pending' && row.status === 'closed'"
                size="small"
                type="danger"
                plain
                @click="$router.push('/audit')"
              >去审讯</el-button>
              <el-button
                v-else-if="row.status === 'open'"
                size="small"
                plain
                @click="$router.push('/trade')"
              >出场录入</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

    </template>

    <!-- 无数据状态 -->
    <div v-else class="empty-wrap">
      <el-empty description="暂无数据，开始录入第一笔交易吧">
        <el-button
          type="primary"
          style="background:#C8102E;border-color:#C8102E"
          @click="$router.push('/plan')"
        >先填写今日计划</el-button>
      </el-empty>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh, Loading, Lock, EditPen, Document, Warning } from '@element-plus/icons-vue'
import { dashboardApi, type DashboardData } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

const data = ref<DashboardData | null>(null)
const loading = ref(false)

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
})

async function loadData() {
  loading.value = true
  try {
    data.value = await dashboardApi.get()
  } catch (e: any) {
    ElMessage.error(e.message || '加载仪表台数据失败')
  } finally {
    loading.value = false
  }
}

// ── 盈亏柱状图高度计算 ────────────────────────────────
function barStyle(pnl: number) {
  if (!data.value?.pnl_curve.length) return { height: '0%' }
  const maxAbs = Math.max(...data.value.pnl_curve.map(i => Math.abs(i.pnl)))
  const pct = maxAbs > 0 ? (Math.abs(pnl) / maxAbs) * 100 : 0
  return { height: `${Math.max(pct, 4)}%` }
}

// ── 情绪颜色 ──────────────────────────────────────────
function emotionColor(rate: number) {
  if (rate >= 0.65) return '#1A7C3E'
  if (rate >= 0.45) return '#B8860B'
  return '#C8102E'
}

// ── 情绪洞察文字 ──────────────────────────────────────
const emotionInsight = computed(() => {
  if (!data.value?.emotion_stats.length) return ''
  const stats = data.value.emotion_stats
  const best = stats[0]
  const worst = stats[stats.length - 1]
  if (best.emotion === worst.emotion) return ''
  const ratio = best.count > 0 && worst.count > 0
    ? (best.win_rate / worst.win_rate).toFixed(1)
    : null
  return ratio
    ? `「${best.emotion}」状态胜率是「${worst.emotion}」状态的 ${ratio} 倍`
    : ''
})

function reviewTagType(s: string): 'success' | 'warning' | 'danger' | 'info' {
  return { done: 'success', reviewing: 'warning', pending: 'danger' }[s] as any || 'info'
}

function reviewLabel(s: string) {
  return { pending: '待复盘', reviewing: '审讯中', done: '已完成' }[s] || s
}

onMounted(loadData)
</script>

<style scoped>
.dash-page { padding: 20px 24px; max-width: 1100px; margin: 0 auto; }

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.dash-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 700; margin: 0;
}
.dash-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

.loading-wrap {
  display: flex; align-items: center; justify-content: center;
  gap: 12px; padding: 80px; color: var(--el-text-color-secondary);
}

/* 今日状态栏 */
.today-bar {
  display: flex;
  align-items: center;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  margin-bottom: 16px;
  overflow: hidden;
}

.today-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  flex: 1;
  font-size: 13px;
  transition: background .12s;
}

.today-item.done { background: #F0F9F0; }
.today-item.todo { background: #FEF9F0; }
.today-item.done .el-icon { color: #1A7C3E; }
.today-item.todo .el-icon { color: #B8860B; }

.today-status { margin-left: 4px; font-size: 12px; color: var(--el-text-color-secondary); }
.today-divider { width: 1px; background: var(--el-border-color); height: 40px; flex-shrink: 0; }

/* 指标卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-top: 3px solid #C8102E;
  border-radius: 2px;
  padding: 16px 18px;
}

.stat-label { font-size: 11px; color: var(--el-text-color-secondary); margin-bottom: 8px; }
.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 26px; font-weight: 700; line-height: 1.1; margin-bottom: 5px;
}
.stat-value.pos { color: #1A7C3E; }
.stat-value.neg { color: #C8102E; }
.stat-value.neutral { color: var(--el-text-color-primary); }
.stat-sub { font-size: 11px; color: var(--el-text-color-secondary); }

.blind-card { border-top-color: #B8860B; }
.blind-list { display: flex; flex-direction: column; gap: 6px; }
.blind-item { display: flex; align-items: center; gap: 8px; }
.blind-rank {
  width: 18px; height: 18px; border-radius: 50%;
  background: #C8102E; color: white;
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.blind-name { font-size: 13px; font-family: 'Noto Serif SC', serif; }

/* 图表区 */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

.chart-card { border-radius: 4px; }
.card-title { font-size: 13px; font-weight: 600; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.chart-empty { padding: 30px; text-align: center; color: var(--el-text-color-secondary); font-size: 13px; }

/* 盈亏柱状图 */
.bar-chart-wrap { padding: 8px 4px 0; }
.bar-chart-area {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 120px;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-val-label {
  font-size: 8px;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
  margin-bottom: 2px;
  opacity: 0;
  transition: opacity .15s;
}

.bar-col:hover .bar-val-label { opacity: 1; }

.bar-container {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 1px 1px 0 0;
  min-height: 3px;
  transition: opacity .15s;
}

.bar-fill.pos { background: linear-gradient(180deg, #1A7C3E, #A8D5B8); }
.bar-fill.neg { background: linear-gradient(180deg, #C8102E, #E8C0C8); }
.bar-col:hover .bar-fill { opacity: 0.75; }

.bar-date {
  font-size: 8px;
  color: var(--el-text-color-secondary);
  margin-top: 3px;
  white-space: nowrap;
}

.bar-val-label.pos { color: #1A7C3E; }
.bar-val-label.neg { color: #C8102E; }

/* 情绪胜率 */
.emotion-list { display: flex; flex-direction: column; gap: 12px; padding: 4px 0; }
.emotion-row { display: flex; align-items: center; gap: 10px; }
.emotion-label { font-size: 12px; color: var(--el-text-color-secondary); width: 40px; flex-shrink: 0; }
.emotion-bar-bg { flex: 1; height: 7px; background: var(--el-fill-color); border-radius: 3px; overflow: hidden; }
.emotion-bar-fill { height: 100%; border-radius: 3px; transition: width .4s; }
.emotion-rate { font-size: 12px; font-weight: 600; width: 36px; text-align: right; font-family: 'JetBrains Mono', monospace; }
.emotion-count { font-size: 10px; color: var(--el-text-color-secondary); width: 28px; }

.emotion-insight {
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: 'Noto Serif SC', serif;
}

/* 近期交易 */
.recent-card { border-radius: 4px; }

.sym-block { display: flex; flex-direction: column; gap: 2px; }
.sym-code { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 13px; }
.sym-name { font-size: 10px; color: var(--el-text-color-secondary); }
.pnl-pos { color: #1A7C3E; font-family: 'JetBrains Mono', monospace; font-weight: 500; }
.pnl-neg { color: #C8102E; font-family: 'JetBrains Mono', monospace; font-weight: 500; }

.empty-wrap { padding: 80px; text-align: center; }
</style>