<template>
  <div class="plan-page">

    <!-- 顶部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">每日交易计划</h2>
        <div class="page-sub">
          <el-date-picker
            v-model="currentDate"
            type="date"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            :clearable="false"
            size="small"
            :disabled="form.locked"
            @change="store.loadPlan(currentDate)"
          />
          <span class="date-hint">盘前填写</span>
          <!-- 锁定状态标识 -->
          <el-tag v-if="form.locked" type="danger" size="small">
            <el-icon><Lock /></el-icon> 已锁定
            <span v-if="form.locked_at" style="margin-left:4px;font-size:10px">
              {{ formatTime(form.locked_at) }}
            </span>
          </el-tag>
          <el-tag v-else type="info" size="small">未锁定</el-tag>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="store.loadPlan(currentDate)">查看历史计划</el-button>
        <el-button
          :disabled="form.locked"
          :loading="saving"
          @click="store.savePlan()"
        >保存草稿</el-button>
        <el-button
          type="primary"
          :disabled="form.locked"
          :loading="locking"
          style="background:#C8102E;border-color:#C8102E"
          @click="store.lockPlan()"
        >
          <el-icon><Lock /></el-icon>
          {{ form.locked ? '已锁定' : '保存并锁定' }}
        </el-button>
      </div>
    </div>

    <!-- 锁定提示条 -->
    <div v-if="form.locked" class="locked-banner">
      <el-icon><Lock /></el-icon>
      今日计划已锁定，开始交易吧。锁定时间：{{ formatTime(form.locked_at) }}
    </div>

    <el-form
      :model="form"
      label-position="top"
      class="plan-form"
      :disabled="form.locked"
    >
      <div class="plan-grid">

        <!-- 左列 -->
        <div class="plan-col">

          <!-- 大盘研判 -->
          <el-card shadow="never" class="plan-card">
            <template #header>
              <span class="card-title">🌐 大盘研判</span>
            </template>

            <el-form-item label="大盘趋势">
              <el-radio-group v-model="form.market_trend">
                <el-radio-button value="bull">强势上攻</el-radio-button>
                <el-radio-button value="mild_bull">温和上涨</el-radio-button>
                <el-radio-button value="sideways">震荡整理</el-radio-button>
                <el-radio-button value="mild_bear">弱势下跌</el-radio-button>
                <el-radio-button value="bear">急跌风险</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="市场情绪预判">
              <el-radio-group v-model="form.market_sentiment">
                <el-radio-button value="optimistic">极度乐观</el-radio-button>
                <el-radio-button value="mild_optimistic">偏乐观</el-radio-button>
                <el-radio-button value="neutral">中性</el-radio-button>
                <el-radio-button value="pessimistic">偏悲观</el-radio-button>
                <el-radio-button value="panic">恐慌</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="重点关注板块">
              <div class="sector-chips">
                <el-check-tag
                  v-for="s in SECTORS"
                  :key="s"
                  :checked="form.focus_sectors.includes(s)"
                  type="primary"
                  @change="toggleSector(s)"
                >{{ s }}</el-check-tag>
              </div>
            </el-form-item>

            <el-form-item label="大盘分析（支撑/压力/逻辑）">
              <el-input
                v-model="form.market_analysis"
                type="textarea"
                :rows="3"
                placeholder="例：上证3350一线有支撑，昨日放量上攻，今日重点看3380能否企稳..."
              />
            </el-form-item>
          </el-card>

          <!-- 操作纪律 -->
          <el-card shadow="never" class="plan-card">
            <template #header>
              <span class="card-title">📏 今日操作纪律</span>
            </template>

            <el-form-item label="最大亏损上限（触达强制停止操作）">
              <el-input
                v-model="form.max_loss_limit"
                placeholder="例：-1.5% 或 -3000元"
                style="width:200px"
              />
            </el-form-item>

            <el-form-item label="最多操作笔数">
              <el-input-number
                v-model="form.max_trade_count"
                :min="1" :max="20"
                controls-position="right"
                style="width:150px"
              />
            </el-form-item>

            <el-form-item label="今日重点克服的情绪弱点">
              <el-radio-group v-model="form.emotion_weakness">
                <el-radio-button value="chasing">追涨</el-radio-button>
                <el-radio-button value="panic_sell">恐慌杀跌</el-radio-button>
                <el-radio-button value="greedy">贪婪不止盈</el-radio-button>
                <el-radio-button value="overtrading">频繁操作</el-radio-button>
                <el-radio-button value="fomo">FOMO</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-card>

          <!-- 入场计划 -->
          <el-card shadow="never" class="plan-card">
            <template #header>
              <span class="card-title">🎯 具体入场计划</span>
            </template>

            <el-form-item label="入场条件 / 止损 / 目标位">
              <el-input
                v-model="form.entry_plan"
                type="textarea"
                :rows="5"
                placeholder="例：
600519 茅台：突破1750且成交量>5日均量，买5%仓，止损1710，目标1800
300750 宁德：回踩200附近放量企稳，买3%仓，止损195"
              />
            </el-form-item>

            <el-form-item label="今日核心假设（可验证）">
              <el-input
                v-model="form.core_hypothesis"
                type="textarea"
                :rows="3"
                placeholder="例：我假设白酒板块今日受消费数据提振，茅台将突破前高。若10点前未突破1750，则放弃今日操作。"
              />
            </el-form-item>
          </el-card>
        </div>

        <!-- 右列：观察池 -->
        <div class="plan-col">
          <el-card shadow="never" class="plan-card watchlist-card">
            <template #header>
              <div class="card-header-row">
                <span class="card-title">👁 今日观察池</span>
                <el-button
                  size="small"
                  plain
                  :disabled="form.locked"
                  @click="store.addWatchItem()"
                >+ 添加标的</el-button>
              </div>
            </template>

            <div v-if="!form.watchlist.length" class="watch-empty">
              <el-empty :image-size="60" description="点击「添加标的」填写观察标的" />
            </div>

            <div
              v-for="(item, idx) in form.watchlist"
              :key="idx"
              class="watch-item"
            >
              <div class="watch-item-head">
                <span class="watch-idx">{{ idx + 1 }}</span>
                <el-input
                  v-model="item.symbol"
                  placeholder="代码"
                  size="small"
                  style="width:90px"
                />
                <el-input
                  v-model="item.name"
                  placeholder="名称"
                  size="small"
                  style="width:100px"
                />
                <el-input-number
                  v-model="item.price"
                  placeholder="现价"
                  size="small"
                  :precision="2"
                  controls-position="right"
                  style="width:110px"
                />
                <el-button
                  size="small"
                  text
                  type="danger"
                  :disabled="form.locked"
                  @click="store.removeWatchItem(idx)"
                >删除</el-button>
              </div>

              <div class="watch-item-body">
                <div class="watch-field">
                  <span class="watch-label">入场条件</span>
                  <el-input
                    v-model="item.entry_condition"
                    placeholder="例：突破1750且量能放大"
                    size="small"
                  />
                </div>
                <div class="watch-field-row">
                  <div class="watch-field half">
                    <span class="watch-label">止损价</span>
                    <el-input-number
                      v-model="item.stop_loss"
                      size="small"
                      :precision="2"
                      controls-position="right"
                      style="width:100%"
                    />
                  </div>
                  <div class="watch-field half">
                    <span class="watch-label">目标价</span>
                    <el-input-number
                      v-model="item.target"
                      size="small"
                      :precision="2"
                      controls-position="right"
                      style="width:100%"
                    />
                  </div>
                </div>
                <div class="watch-field">
                  <span class="watch-label">备注</span>
                  <el-input
                    v-model="item.note"
                    placeholder="补充说明..."
                    size="small"
                  />
                </div>
              </div>
            </div>

            <!-- 锁定提醒 -->
            <div class="lock-hint">
              <el-icon><InfoFilled /></el-icon>
              锁定后计划将与今日复盘自动对比，帮你量化执行纪律
            </div>
          </el-card>

          <!-- 历史计划列表 -->
          <el-card shadow="never" class="plan-card" style="margin-top:12px">
            <template #header>
              <span class="card-title">📚 近期计划记录</span>
            </template>
            <div v-if="!historyList.length" style="padding:12px;text-align:center;color:var(--el-text-color-secondary);font-size:12px">
              暂无历史计划
            </div>
            <div
              v-for="p in historyList"
              :key="p.date"
              class="history-item"
              @click="store.loadPlan(p.date)"
            >
              <span class="hi-date">{{ p.date }}</span>
              <el-tag size="small" :type="p.locked ? 'danger' : 'info'">
                {{ p.locked ? '已锁定' : '草稿' }}
              </el-tag>
              <span class="hi-sectors">{{ p.focus_sectors.slice(0, 3).join(' · ') }}</span>
            </div>
          </el-card>
        </div>

      </div>
    </el-form>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { Lock, InfoFilled } from '@element-plus/icons-vue'
import { usePlanStore } from '@/stores/plan'
import { planApi, type DailyPlan } from '@/api/plan'

const SECTORS = ['白酒', '新能源', '半导体', '军工', '医药', '银行', '地产', 'AI/TMT', '消费', '化工', '有色', '券商']

const store = usePlanStore()
const { currentDate, form, loading, saving, locking } = storeToRefs(store)

const historyList = ref<DailyPlan[]>([])

function toggleSector(s: string) {
  const idx = form.value.focus_sectors.indexOf(s)
  if (idx === -1) {
    form.value.focus_sectors.push(s)
  } else {
    form.value.focus_sectors.splice(idx, 1)
  }
}

function formatTime(t?: string | null) {
  if (!t) return ''
  return t.slice(0, 16).replace('T', ' ')
}

async function loadHistory() {
  try {
    historyList.value = await planApi.getList(10)
  } catch {}
}

onMounted(async () => {
  await store.loadPlan()
  await loadHistory()
})
</script>

<style scoped>
.plan-page { padding: 20px 24px; max-width: 1200px; margin: 0 auto; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 16px;
}

.header-left { display: flex; flex-direction: column; gap: 8px; }
.header-right { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }

.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 700;
  color: var(--el-text-color-primary); margin: 0;
}

.page-sub { display: flex; align-items: center; gap: 10px; }
.date-hint { font-size: 12px; color: var(--el-text-color-secondary); }

/* 锁定提示条 */
.locked-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #FEF0F0;
  border: 1px solid #FBC4C4;
  border-left: 3px solid #C8102E;
  border-radius: 2px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #792020;
}

.plan-form { margin-top: 0; }

.plan-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 14px;
}

.plan-col { display: flex; flex-direction: column; gap: 12px; }
.plan-card { border-radius: 4px; }
.card-title { font-size: 13px; font-weight: 600; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }

.sector-chips { display: flex; flex-wrap: wrap; gap: 7px; }

/* 观察池 */
.watchlist-card { flex: 1; }
.watch-empty { padding: 20px; }

.watch-item {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  margin-bottom: 10px;
  overflow: hidden;
}
.watch-item:last-of-type { margin-bottom: 0; }

.watch-item-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--el-fill-color-lighter);
  border-bottom: 1px solid var(--el-border-color);
}

.watch-idx {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #C8102E;
  color: white;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.watch-item-body { padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.watch-field { display: flex; flex-direction: column; gap: 4px; }
.watch-field-row { display: flex; gap: 10px; }
.watch-field.half { flex: 1; }
.watch-label { font-size: 11px; color: var(--el-text-color-secondary); }

.lock-hint {
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 历史列表 */
.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background .12s;
  font-size: 12.5px;
}
.history-item:last-child { border-bottom: none; }
.history-item:hover { background: #FEF0F0; }
.hi-date { font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.hi-sectors { font-size: 11px; color: var(--el-text-color-secondary); flex: 1; }
</style>