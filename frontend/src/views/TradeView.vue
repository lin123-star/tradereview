<template>
  <div class="trade-page">

    <!-- 顶部 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">录入交易</h2>
        <div class="page-sub">两步录入 · 入场信息提交后锁定不可修改</div>
      </div>
    </div>

    <!-- Tab切换：入场录入 / 出场录入 / 持仓中 -->
    <el-tabs v-model="activeTab" class="main-tabs">

      <!-- ── Step1：入场录入 ── -->
      <el-tab-pane label="⊕ 入场录入" name="step1">
        <el-form
          ref="step1Ref"
          :model="step1Form"
          :rules="step1Rules"
          label-position="top"
          class="trade-form"
        >
          <div class="form-grid">
            <!-- 左列 -->
            <div class="form-col">
              <el-card shadow="never">
                <template #header>
                  <span class="card-title">📌 标的信息</span>
                </template>

                <el-form-item label="标的代码" prop="symbol">
                  <el-input
                    v-model="step1Form.symbol"
                    placeholder="例：600519"
                    style="width:160px"
                  />
                </el-form-item>

                <el-form-item label="标的名称">
                  <el-input
                    v-model="step1Form.name"
                    placeholder="例：贵州茅台"
                    style="width:200px"
                  />
                </el-form-item>

                <el-form-item label="交易方向" prop="direction">
                  <el-radio-group v-model="step1Form.direction">
                    <el-radio-button value="buy">
                      <span class="dir-buy">买入</span>
                    </el-radio-button>
                    <el-radio-button value="sell">
                      <span class="dir-sell">卖出</span>
                    </el-radio-button>
                    <el-radio-button value="add">加仓</el-radio-button>
                    <el-radio-button value="reduce">减仓</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="入场价格" prop="entry_price">
                  <el-input-number
                    v-model="step1Form.entry_price"
                    :precision="3"
                    :min="0"
                    controls-position="right"
                    style="width:180px"
                  />
                </el-form-item>

                <el-form-item label="入场时间" prop="entry_time">
                  <el-date-picker
                    v-model="step1Form.entry_time"
                    type="datetime"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    placeholder="选择入场时间"
                    style="width:220px"
                  />
                </el-form-item>

                <el-form-item label="仓位比例">
                  <el-slider
                    v-model="step1Form.position_ratio"
                    :min="0" :max="1" :step="0.05"
                    :format-tooltip="(v: number) => `${(v * 100).toFixed(0)}%`"
                    style="width:280px"
                  />
                  <span class="slider-label">{{ (step1Form.position_ratio * 100).toFixed(0) }}%</span>
                </el-form-item>
              </el-card>

              <el-card shadow="never" style="margin-top:12px">
                <template #header>
                  <span class="card-title">🏷️ 标签</span>
                </template>

                <el-form-item label="入场情绪">
                  <el-radio-group v-model="step1Form.emotion">
                    <el-radio-button value="calm">冷静</el-radio-button>
                    <el-radio-button value="greedy">贪婪</el-radio-button>
                    <el-radio-button value="panic">恐慌</el-radio-button>
                    <el-radio-button value="hesitant">犹豫</el-radio-button>
                    <el-radio-button value="impulsive">冲动</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="策略标签">
                  <StrategySelector
                    v-model="step1Form.strategy_tag_id"
                  />
                </el-form-item>

                <el-form-item label="市场环境">
                  <el-radio-group v-model="step1Form.market_env">
                    <el-radio-button value="bull">涨势</el-radio-button>
                    <el-radio-button value="bear">跌势</el-radio-button>
                    <el-radio-button value="sideways">震荡</el-radio-button>
                    <el-radio-button value="volatile">剧烈波动</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="关联复盘日期">
                  <el-date-picker
                    v-model="step1Form.review_date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    placeholder="关联今日复盘（可选）"
                    style="width:180px"
                  />
                </el-form-item>
              </el-card>
            </div>

            <!-- 右列：入场逻辑（最重要的字段） -->
            <div class="form-col">
              <el-card shadow="never" class="logic-card">
                <template #header>
                  <div class="logic-header">
                    <span class="card-title">🔒 入场逻辑</span>
                    <el-tag type="danger" size="small">提交后锁定</el-tag>
                  </div>
                </template>

                <div class="logic-warning">
                  <el-icon><WarningFilled /></el-icon>
                  这是整个系统最重要的字段。入场逻辑一旦提交不可修改，
                  这是防止「后见之偏」的核心机制。请在入场<strong>之前或入场时</strong>填写，
                  如实记录当时的判断依据，不要事后补填。
                </div>

                <el-form-item prop="entry_logic">
                  <el-input
                    v-model="step1Form.entry_logic"
                    type="textarea"
                    :rows="12"
                    placeholder="详细描述入场的判断依据，例如：
• 技术面：均线金叉，成交量放大至5日均量的1.5倍，MACD金叉
• 基本面：消费数据超预期，茅台批价持续回升
• 止损位：跌破1700元止损
• 目标位：第一目标1800元，第二目标1850元
• 仓位逻辑：当前总仓位30%，此次加至50%"
                    style="font-size:13px"
                  />
                </el-form-item>

                <div class="lock-tip">
                  <el-icon><Lock /></el-icon>
                  提交后系统将记录时间戳并锁定此字段，不允许任何修改
                </div>
              </el-card>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-footer">
            <el-button @click="resetStep1">重置</el-button>
            <el-button
              type="primary"
              :loading="submitting"
              style="background:#C8102E;border-color:#C8102E;min-width:140px"
              @click="handleStep1Submit"
            >
              <el-icon><Lock /></el-icon>
              提交并锁定入场记录
            </el-button>
          </div>
        </el-form>
      </el-tab-pane>

      <!-- ── Step2：出场录入 ── -->
      <el-tab-pane name="step2">
        <template #label>
          出场录入
          <el-badge
            v-if="openTrades.length"
            :value="openTrades.length"
            class="tab-badge"
          />
        </template>

        <div v-if="!openTrades.length" class="empty-tip">
          <el-empty description="暂无持仓中的交易" />
        </div>

        <template v-else>
          <!-- 选择要出场的交易 -->
          <div class="open-trade-list">
            <div
              v-for="t in openTrades"
              :key="t.id"
              class="open-trade-card"
              :class="{ selected: selectedTradeId === t.id }"
              @click="selectTrade(t)"
            >
              <div class="otc-left">
                <span class="otc-symbol">{{ t.symbol }}</span>
                <span class="otc-name">{{ t.name }}</span>
                <span :class="['otc-dir', t.direction]">{{ dirLabel(t.direction) }}</span>
              </div>
              <div class="otc-right">
                <div class="otc-price">入场 ¥{{ t.entry_price }}</div>
                <div class="otc-pos">仓位 {{ (t.position_ratio * 100).toFixed(0) }}%</div>
              </div>
            </div>
          </div>

          <!-- 出场表单 -->
          <el-form
            v-if="selectedTradeId"
            ref="step2Ref"
            :model="step2Form"
            :rules="step2Rules"
            label-position="top"
            class="trade-form"
            style="margin-top:16px"
          >
            <div class="form-grid">
              <el-card shadow="never">
                <template #header><span class="card-title">📤 出场信息</span></template>

                <el-form-item label="出场价格" prop="exit_price">
                  <el-input-number
                    v-model="step2Form.exit_price"
                    :precision="3"
                    :min="0"
                    controls-position="right"
                    style="width:180px"
                  />
                </el-form-item>

                <el-form-item label="出场时间" prop="exit_time">
                  <el-date-picker
                    v-model="step2Form.exit_time"
                    type="datetime"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    style="width:220px"
                  />
                </el-form-item>

                <el-form-item label="出场情绪">
                  <el-radio-group v-model="step2Form.exit_emotion">
                    <el-radio-button value="calm">冷静</el-radio-button>
                    <el-radio-button value="greedy">贪婪</el-radio-button>
                    <el-radio-button value="panic">恐慌</el-radio-button>
                    <el-radio-button value="hesitant">犹豫</el-radio-button>
                    <el-radio-button value="impulsive">冲动</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="是否符合计划">
                  <el-radio-group v-model="step2Form.plan_followed">
                    <el-radio-button value="yes">完全符合</el-radio-button>
                    <el-radio-button value="partial">部分符合</el-radio-button>
                    <el-radio-button value="no">计划外</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="出场逻辑">
                  <el-input
                    v-model="step2Form.exit_logic"
                    type="textarea"
                    :rows="3"
                    placeholder="为什么在这个点位离场..."
                  />
                </el-form-item>
              </el-card>

              <el-card shadow="never">
                <template #header><span class="card-title">🧠 复盘字段</span></template>

                <el-form-item label="核心教训（一句话）">
                  <el-input
                    v-model="step2Form.lesson"
                    placeholder="这笔交易最重要的一条教训"
                  />
                </el-form-item>

                <el-form-item label="如果重来会怎么做">
                  <el-input
                    v-model="step2Form.counterfactual"
                    type="textarea"
                    :rows="3"
                    placeholder="反事实思考..."
                  />
                </el-form-item>

                <el-form-item label="下次相同情境的可验证假设">
                  <el-input
                    v-model="step2Form.hypothesis"
                    type="textarea"
                    :rows="3"
                    placeholder="例：下次遇到均线金叉但大盘弱势时，我会先观察一个交易日再入场..."
                  />
                </el-form-item>

                <el-form-item label="这笔盈亏有多少是运气？（1=纯实力 5=纯运气）">
                  <el-slider
                    v-model="step2Form.uncertainty"
                    :min="1" :max="5" :step="1"
                    :marks="{ 1: '纯实力', 3: '一半', 5: '纯运气' }"
                    style="width:280px;margin-left:8px"
                  />
                </el-form-item>
              </el-card>
            </div>

            <div class="form-footer">
              <el-button
                type="primary"
                :loading="submitting"
                style="background:#C8102E;border-color:#C8102E;min-width:120px"
                @click="handleStep2Submit"
              >
                保存出场记录
              </el-button>
            </div>
          </el-form>
        </template>
      </el-tab-pane>

      <!-- ── 持仓中 ── -->
      <el-tab-pane label="持仓中" name="open">
        <el-table
          :data="openTrades"
          v-loading="loading"
          stripe
          style="width:100%"
          row-key="id"
        >
          <el-table-column type="expand">
            <template #default="{ row }">
              <TradeSnapshotPanel :trade-id="row.id" />
            </template>
          </el-table-column>        
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
              <el-tag :type="row.direction === 'buy' || row.direction === 'add' ? 'success' : 'danger'" size="small">
                {{ dirLabel(row.direction) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入场价" prop="entry_price" width="100" />
          <el-table-column label="仓位" width="80">
            <template #default="{ row }">{{ (row.position_ratio * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column label="入场时间" width="150">
            <template #default="{ row }">{{ formatTime(row.entry_time) }}</template>
          </el-table-column>
          <el-table-column label="策略" prop="strategy" width="100" />
          <el-table-column label="情绪" width="90">
            <template #default="{ row }">{{ emotionLabel(row.emotion) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                plain
                @click="goStep2(row)"
              >出场录入</el-button>
              <el-popconfirm
                title="确认删除这条持仓记录？"
                @confirm="store.deleteTrade(row.id)"
              >
                <template #reference>
                  <el-button size="small" type="danger" plain style="margin-left:4px">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ── 历史记录 ── -->
      <el-tab-pane label="历史记录" name="history">
        <el-table
          :data="closedTrades"
          v-loading="loading"
          stripe
          style="width:100%"
        >
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
              <el-tag :type="row.direction === 'buy' || row.direction === 'add' ? 'success' : 'danger'" size="small">
                {{ dirLabel(row.direction) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入场" prop="entry_price" width="90" />
          <el-table-column label="出场" prop="exit_price" width="90" />
          <el-table-column label="盈亏" width="110">
            <template #default="{ row }">
              <span :class="row.pnl_amount >= 0 ? 'pnl-pos' : 'pnl-neg'">
                {{ row.pnl_amount >= 0 ? '+' : '' }}{{ row.pnl_amount?.toFixed(0) }}元
              </span>
              <div style="font-size:10px;color:#8A95A3">
                {{ row.pnl_ratio >= 0 ? '+' : '' }}{{ (row.pnl_ratio * 100)?.toFixed(2) }}%
              </div>
            </template>
          </el-table-column>
          <el-table-column label="情绪" width="90">
            <template #default="{ row }">{{ emotionLabel(row.emotion) }}</template>
          </el-table-column>
          <el-table-column label="策略" prop="strategy" width="100" />
          <el-table-column label="计划执行" width="90">
            <template #default="{ row }">
              <el-tag
                :type="row.plan_followed === 'yes' ? 'success' : row.plan_followed === 'no' ? 'danger' : 'warning'"
                size="small"
              >
                {{ planLabel(row.plan_followed) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="复盘状态" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.review_status === 'done' ? 'success' : 'warning'"
                size="small"
              >
                {{ reviewLabel(row.review_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入场时间" width="140">
            <template #default="{ row }">{{ formatTime(row.entry_time) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Lock, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useTradeStore } from '@/stores/trade'
import type { TradeOut, TradeStep1Form, TradeStep2Form } from '@/api/trade'
import StrategySelector from '@/components/StrategySelector.vue'
import TradeSnapshotPanel from '@/components/TradesnapshotPanel.vue'

const store = useTradeStore()
const { trades, loading, submitting } = store.$state as any
const activeTab = ref('step1')
const step1Ref = ref()
const step2Ref = ref()
const selectedTradeId = ref<number | null>(null)

// ── 计算属性 ──────────────────────────────────────────
const openTrades = computed(() => store.trades.filter(t => t.status === 'open'))
const closedTrades = computed(() => store.trades.filter(t => t.status === 'closed'))

// ── Step1 表单 ────────────────────────────────────────
const step1Form = ref<TradeStep1Form & { strategy_tag_id: number | null }>({
  symbol: '',
  name: '',
  direction: 'buy',
  entry_price: null,
  entry_time: new Date().toISOString().slice(0, 19),
  position_ratio: 0.05,
  entry_logic: '',
  market_env: '',
  strategy: '',
  emotion: 'calm',
  review_date: new Date().toISOString().slice(0, 10),
  strategy_tag_id: null,
})

const step1Rules = {
  symbol: [{ required: true, message: '请填写标的代码', trigger: 'blur' }],
  direction: [{ required: true, message: '请选择交易方向', trigger: 'change' }],
  entry_price: [{ required: true, message: '请填写入场价格', trigger: 'blur' }],
  entry_time: [{ required: true, message: '请选择入场时间', trigger: 'change' }],
  entry_logic: [{ required: true, min: 10, message: '入场逻辑至少10个字', trigger: 'blur' }],
}

async function handleStep1Submit() {
  await step1Ref.value?.validate(async (valid: boolean) => {
    if (!valid) return
    const result = await store.createTrade(step1Form.value)
    if (result) {
      resetStep1()
      activeTab.value = 'open'
    }
  })
}

function resetStep1() {
  step1Form.value = {
    symbol: '', name: '', direction: 'buy',
    entry_price: null, entry_time: new Date().toISOString().slice(0, 19),
    position_ratio: 0.05, entry_logic: '', market_env: '',
    strategy: '', emotion: 'calm',
    review_date: new Date().toISOString().slice(0, 10),
    strategy_tag_id: null,
  }
}

// ── Step2 表单 ────────────────────────────────────────
const step2Form = ref<TradeStep2Form>({
  exit_price: null,
  exit_time: new Date().toISOString().slice(0, 19),
  exit_logic: '',
  exit_emotion: 'calm',
  plan_followed: '',
  lesson: '',
  counterfactual: '',
  hypothesis: '',
  uncertainty: 3,
})

const step2Rules = {
  exit_price: [{ required: true, message: '请填写出场价格', trigger: 'blur' }],
  exit_time: [{ required: true, message: '请选择出场时间', trigger: 'change' }],
}

function selectTrade(t: TradeOut) {
  selectedTradeId.value = t.id
}

function goStep2(t: TradeOut) {
  selectedTradeId.value = t.id
  activeTab.value = 'step2'
}

async function handleStep2Submit() {
  if (!selectedTradeId.value) {
    ElMessage.warning('请先选择要出场的交易')
    return
  }
  await step2Ref.value?.validate(async (valid: boolean) => {
    if (!valid) return
    const result = await store.completeTrade(selectedTradeId.value!, step2Form.value)
    if (result) {
      selectedTradeId.value = null
      activeTab.value = 'history'
    }
  })
}

// ── 工具函数 ──────────────────────────────────────────
function dirLabel(d: string) {
  return { buy: '买入', sell: '卖出', add: '加仓', reduce: '减仓' }[d] || d
}

function emotionLabel(e: string) {
  return { calm: '冷静', greedy: '贪婪', panic: '恐慌', hesitant: '犹豫', impulsive: '冲动' }[e] || e
}

function planLabel(p: string) {
  return { yes: '完全符合', partial: '部分符合', no: '计划外' }[p] || p
}

function reviewLabel(r: string) {
  return { pending: '待复盘', reviewing: '审讯中', done: '已完成' }[r] || r
}

function formatTime(t: string) {
  return t ? t.slice(0, 16).replace('T', ' ') : ''
}

onMounted(() => {
  store.loadList()
})
</script>

<style scoped>
.trade-page { padding: 20px 24px; max-width: 1100px; margin: 0 auto; }

.page-header { margin-bottom: 20px; }
.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 700;
  color: var(--el-text-color-primary); margin: 0;
}
.page-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

.main-tabs :deep(.el-tabs__header) { margin-bottom: 16px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-col { display: flex; flex-direction: column; gap: 0; }

.card-title { font-size: 13px; font-weight: 600; }

.logic-card { height: 100%; }
.logic-header { display: flex; align-items: center; justify-content: space-between; }

.logic-warning {
  padding: 10px 13px;
  background: #FEF0F0;
  border: 1px solid #FBC4C4;
  border-left: 3px solid #C8102E;
  border-radius: 2px;
  font-size: 12px;
  color: #792020;
  margin-bottom: 14px;
  line-height: 1.6;
}

.lock-tip {
  margin-top: 10px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.slider-label {
  margin-left: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #C8102E;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
}

/* 持仓选择卡片 */
.open-trade-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 4px; }

.open-trade-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all .15s;
  background: var(--el-bg-color);
}

.open-trade-card:hover { border-color: #C8102E; }
.open-trade-card.selected { border-color: #C8102E; background: #FEF0F0; }

.otc-left { display: flex; align-items: center; gap: 10px; }
.otc-symbol { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 14px; }
.otc-name { font-size: 12px; color: var(--el-text-color-secondary); }
.otc-dir { font-size: 12px; font-weight: 600; }
.otc-dir.buy, .otc-dir.add { color: #1A7C3E; }
.otc-dir.sell, .otc-dir.reduce { color: #C8102E; }
.otc-right { text-align: right; }
.otc-price { font-size: 13px; }
.otc-pos { font-size: 11px; color: var(--el-text-color-secondary); }

/* 表格 */
.sym-block { display: flex; flex-direction: column; gap: 2px; }
.sym-code { font-family: 'JetBrains Mono', monospace; font-weight: 700; }
.sym-name { font-size: 10px; color: var(--el-text-color-secondary); }
.pnl-pos { color: #1A7C3E; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.pnl-neg { color: #C8102E; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.dir-buy { color: #1A7C3E; }
.dir-sell { color: #C8102E; }

.tab-badge { margin-left: 4px; }
.empty-tip { padding: 40px; }
</style>
