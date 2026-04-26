<template>
  <div class="snapshot-panel">
    <div v-if="loading" class="snap-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载行情快照...
    </div>

    <div v-else-if="!snapshots.length" class="snap-empty">
      <span v-if="fetching">⏳ 行情数据抓取中，稍后刷新查看...</span>
      <span v-else>暂无行情快照数据</span>
    </div>

    <div v-else class="snap-content">
      <div
        v-for="snap in snapshots"
        :key="snap.id"
        class="snap-card"
        :class="snap.snapshot_type"
      >
        <!-- 快照标题 -->
        <div class="snap-head">
          <span class="snap-type-label">
            {{ snap.snapshot_type === 'entry' ? '📈 入场日行情' : '📉 出场日行情' }}
          </span>
          <span class="snap-date">{{ snap.snapshot_date }}</span>
          <el-tag
            size="small"
            :type="snap.fetch_status === 'done' ? 'success' : snap.fetch_status === 'failed' ? 'danger' : 'warning'"
          >
            {{ statusLabel(snap.fetch_status) }}
          </el-tag>
        </div>

        <div v-if="snap.fetch_status === 'done'" class="snap-body">

          <!-- 大盘数据 -->
          <div class="snap-section">
            <div class="snap-section-title">大盘</div>
            <div class="snap-metrics">
              <div class="metric">
                <span class="mk-label">上证</span>
                <span :class="['mk-val', pctClass(snap.sh_pct)]">
                  {{ fmtPct(snap.sh_pct) }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">深证</span>
                <span :class="['mk-val', pctClass(snap.sz_pct)]">
                  {{ fmtPct(snap.sz_pct) }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">创业板</span>
                <span :class="['mk-val', pctClass(snap.cy_pct)]">
                  {{ fmtPct(snap.cy_pct) }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">量能比</span>
                <span class="mk-val neutral">
                  {{ snap.sh_volume_ratio != null ? snap.sh_volume_ratio.toFixed(2) + 'x' : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">大盘趋势</span>
                <span :class="['mk-val', snap.market_trend === 'up' ? 'pos' : snap.market_trend === 'down' ? 'neg' : 'neutral']">
                  {{ trendLabel(snap.market_trend) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 个股数据 -->
          <div class="snap-section">
            <div class="snap-section-title">个股 · {{ snap.symbol }}</div>
            <div class="snap-metrics">
              <div class="metric">
                <span class="mk-label">当日涨跌</span>
                <span :class="['mk-val', pctClass(snap.stock_pct)]">
                  {{ fmtPct(snap.stock_pct) }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">收盘价</span>
                <span class="mk-val neutral">
                  {{ snap.stock_close != null ? '¥' + snap.stock_close.toFixed(2) : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">量能比</span>
                <span :class="['mk-val', volClass(snap.stock_volume_ratio)]">
                  {{ snap.stock_volume_ratio != null ? snap.stock_volume_ratio.toFixed(2) + 'x' : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">换手率</span>
                <span class="mk-val neutral">
                  {{ snap.stock_turnover != null ? snap.stock_turnover.toFixed(2) + '%' : '-' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 均线状态 -->
          <div class="snap-section">
            <div class="snap-section-title">均线状态</div>
            <div class="snap-metrics">
              <div class="metric">
                <span class="mk-label">MA5</span>
                <span :class="['mk-val', snap.above_ma5 === 1 ? 'pos' : 'neg']">
                  {{ snap.ma5 != null ? snap.ma5.toFixed(2) : '-' }}
                  <span class="mk-sub">{{ snap.above_ma5 === 1 ? '↑上方' : snap.above_ma5 === 0 ? '↓下方' : '' }}</span>
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">MA10</span>
                <span :class="['mk-val', snap.above_ma10 === 1 ? 'pos' : 'neg']">
                  {{ snap.ma10 != null ? snap.ma10.toFixed(2) : '-' }}
                  <span class="mk-sub">{{ snap.above_ma10 === 1 ? '↑上方' : snap.above_ma10 === 0 ? '↓下方' : '' }}</span>
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">MA20</span>
                <span :class="['mk-val', snap.above_ma20 === 1 ? 'pos' : 'neg']">
                  {{ snap.ma20 != null ? snap.ma20.toFixed(2) : '-' }}
                  <span class="mk-sub">{{ snap.above_ma20 === 1 ? '↑上方' : snap.above_ma20 === 0 ? '↓下方' : '' }}</span>
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">均线排列</span>
                <span :class="['mk-val', snap.ma_bullish === 1 ? 'pos' : 'neg']">
                  {{ snap.ma_bullish === 1 ? '多头排列' : snap.ma_bullish === 0 ? '空头排列' : '-' }}
                </span>
              </div>
            </div>
          </div>

          <!-- MACD -->
          <div class="snap-section">
            <div class="snap-section-title">MACD</div>
            <div class="snap-metrics">
              <div class="metric">
                <span class="mk-label">DIF</span>
                <span :class="['mk-val', snap.macd_diff != null && snap.macd_diff > 0 ? 'pos' : 'neg']">
                  {{ snap.macd_diff != null ? snap.macd_diff.toFixed(4) : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">DEA</span>
                <span :class="['mk-val', snap.macd_dea != null && snap.macd_dea > 0 ? 'pos' : 'neg']">
                  {{ snap.macd_dea != null ? snap.macd_dea.toFixed(4) : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">柱</span>
                <span :class="['mk-val', snap.macd_bar != null && snap.macd_bar > 0 ? 'pos' : 'neg']">
                  {{ snap.macd_bar != null ? snap.macd_bar.toFixed(4) : '-' }}
                </span>
              </div>
              <div class="metric">
                <span class="mk-label">金/死叉</span>
                <span :class="['mk-val', snap.macd_golden_cross === 1 ? 'pos' : snap.macd_golden_cross === -1 ? 'neg' : 'neutral']">
                  {{ snap.macd_golden_cross === 1 ? '金叉' : snap.macd_golden_cross === -1 ? '死叉' : '无' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 板块 -->
          <div v-if="snap.sector_name" class="snap-section">
            <div class="snap-section-title">板块</div>
            <div class="snap-metrics">
              <div class="metric">
                <span class="mk-label">所属板块</span>
                <span class="mk-val neutral">{{ snap.sector_name }}</span>
              </div>
              <div class="metric">
                <span class="mk-label">板块涨跌</span>
                <span :class="['mk-val', pctClass(snap.sector_pct)]">
                  {{ fmtPct(snap.sector_pct) }}
                </span>
              </div>
            </div>
          </div>

        </div>

        <!-- 抓取失败提示 -->
        <div v-else-if="snap.fetch_status === 'failed'" class="snap-error">
          抓取失败：{{ snap.fetch_error || '未知错误' }}
          <el-button size="small" plain @click="retrySnapshot(snap.trade_id)">重试</el-button>
        </div>

        <!-- 抓取中提示 -->
        <div v-else class="snap-pending">
          ⏳ 行情数据抓取中，通常需要10-30秒，可刷新查看
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const http = axios.create({ baseURL: BASE, timeout: 15000 })

interface Snapshot {
  id: number
  trade_id: number
  snapshot_date: string
  snapshot_type: string
  symbol: string
  sh_pct: number | null
  sz_pct: number | null
  cy_pct: number | null
  sh_volume_ratio: number | null
  market_trend: string
  stock_pct: number | null
  stock_volume: number | null
  stock_volume_ratio: number | null
  stock_turnover: number | null
  stock_close: number | null
  ma5: number | null
  ma10: number | null
  ma20: number | null
  above_ma5: number | null
  above_ma10: number | null
  above_ma20: number | null
  ma_bullish: number | null
  macd_diff: number | null
  macd_dea: number | null
  macd_bar: number | null
  macd_golden_cross: number | null
  sector_name: string
  sector_pct: number | null
  fetch_status: string
  fetch_error: string
}

const props = defineProps<{ tradeId: number }>()
const snapshots = ref<Snapshot[]>([])
const loading = ref(false)
const fetching = ref(false)

async function loadSnapshots() {
  loading.value = true
  try {
    const res = await http.get<Snapshot[]>(`/api/snapshot/trade/${props.tradeId}`)
    snapshots.value = res.data
    fetching.value = snapshots.value.some(s => s.fetch_status === 'pending')
  } catch {
    snapshots.value = []
  } finally {
    loading.value = false
  }
}

async function retrySnapshot(tradeId: number) {
  try {
    await http.post(`/api/snapshot/manual/${tradeId}`)
    ElMessage.success('重试任务已启动，约30秒后刷新查看')
    setTimeout(loadSnapshots, 5000)
  } catch {
    ElMessage.error('重试失败')
  }
}

// 格式化工具函数
function fmtPct(val: number | null): string {
  if (val == null) return '-'
  return (val >= 0 ? '+' : '') + val.toFixed(2) + '%'
}

function pctClass(val: number | null): string {
  if (val == null) return 'neutral'
  return val > 0 ? 'pos' : val < 0 ? 'neg' : 'neutral'
}

function volClass(val: number | null): string {
  if (val == null) return 'neutral'
  return val >= 1.5 ? 'pos' : val < 0.8 ? 'neg' : 'neutral'
}

function trendLabel(t: string): string {
  return { up: '上涨', down: 'down', sideways: '震荡' }[t] || t || '-'
}

function statusLabel(s: string): string {
  return { done: '已完成', failed: '抓取失败', pending: '抓取中' }[s] || s
}

onMounted(loadSnapshots)
</script>

<style scoped>
.snapshot-panel { padding: 12px 16px; }

.snap-loading, .snap-empty {
  display: flex; align-items: center; gap: 8px;
  color: var(--el-text-color-secondary); font-size: 12px; padding: 8px 0;
}

.snap-content { display: flex; gap: 14px; flex-wrap: wrap; }

.snap-card {
  flex: 1; min-width: 300px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px; overflow: hidden;
}

.snap-card.entry { border-top: 3px solid #1A7C3E; }
.snap-card.exit  { border-top: 3px solid #C8102E; }

.snap-head {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px;
  background: var(--el-fill-color-lighter);
  border-bottom: 1px solid var(--el-border-color);
}

.snap-type-label { font-size: 12px; font-weight: 600; flex: 1; }
.snap-date { font-size: 11px; color: var(--el-text-color-secondary); font-family: 'JetBrains Mono', monospace; }

.snap-body { padding: 10px 12px; display: flex; flex-direction: column; gap: 10px; }


.snap-section-title {
  font-size: 10px; font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase; letter-spacing: 0.1em;
  margin-bottom: 6px;
}

.snap-metrics { display: flex; flex-wrap: wrap; gap: 8px; }

.metric {
  display: flex; flex-direction: column; gap: 2px;
  min-width: 70px;
  padding: 6px 10px;
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.mk-label { font-size: 10px; color: var(--el-text-color-secondary); }
.mk-val {
  font-size: 13px; font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}
.mk-val.pos { color: #1A7C3E; }
.mk-val.neg { color: #C8102E; }
.mk-val.neutral { color: var(--el-text-color-primary); }
.mk-sub { font-size: 9px; font-weight: 400; margin-left: 2px; }

.snap-error {
  padding: 10px 12px;
  font-size: 12px; color: #C8102E;
  display: flex; align-items: center; gap: 10px;
}

.snap-pending {
  padding: 10px 12px;
  font-size: 12px; color: var(--el-text-color-secondary);
}
</style>