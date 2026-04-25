<template>
  <div class="review-section">
    <div class="section-head">三、操作复盘</div>

    <!-- 今日盈亏摘要 -->
    <el-card shadow="never" class="kpi-card">
      <div class="kpi-row">
        <div class="kpi-item">
          <div class="kpi-label">今日盈亏（元）</div>
          <el-input-number
            v-model="form.pnl_amount"
            :precision="0"
            :step="100"
            controls-position="right"
            style="width:100%"
          />
        </div>
        <div class="kpi-item">
          <div class="kpi-label">操作笔数</div>
          <el-input-number
            v-model="form.trade_count"
            :min="0" :max="50"
            controls-position="right"
            style="width:100%"
          />
        </div>
        <div class="kpi-item">
          <div class="kpi-label">盈利笔数</div>
          <el-input-number
            v-model="form.win_count"
            :min="0"
            controls-position="right"
            style="width:100%"
          />
        </div>
        <div class="kpi-item">
          <div class="kpi-label">亏损笔数</div>
          <el-input-number
            v-model="form.loss_count"
            :min="0"
            controls-position="right"
            style="width:100%"
          />
        </div>
      </div>
    </el-card>

    <!-- 计划 vs 实际对比 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header-row">
          <span class="card-title">📋 计划 vs 实际对比</span>
          <el-button size="small" plain @click="store.addVsRow()">+ 添加一行</el-button>
        </div>
      </template>

      <div class="vs-table-wrap">
        <!-- 表头 -->
        <div class="vs-row vs-head">
          <div class="vs-cell-plan">今日计划</div>
          <div class="vs-cell-actual vs-actual-red">实际执行</div>
          <div class="vs-cell-del"></div>
        </div>
        <!-- 数据行 -->
        <div v-for="(row, idx) in vsRows" :key="idx" class="vs-row">
          <div class="vs-cell-plan">
            <el-input
              v-model="row.plan"
              placeholder="例：茅台 突破1750买入"
              size="small"
            />
          </div>
          <div class="vs-cell-actual">
            <el-input
              v-model="row.actual"
              placeholder="例：1752入场 ✓"
              size="small"
            />
          </div>
          <div class="vs-cell-del">
            <el-button
              v-if="vsRows.length > 1"
              size="small" text type="danger"
              @click="store.removeVsRow(idx)"
            >×</el-button>
          </div>
        </div>
      </div>

      <!-- 执行纪律备注 -->
      <div class="discipline-note" v-if="form.worst_trade">
        ⚠ {{ form.worst_trade }}
      </div>
    </el-card>

    <!-- 操作总结 + 深度思考 -->
    <div class="op-grid">
      <el-card shadow="never">
        <template #header><span class="card-title">✍️ 操作总结</span></template>

        <el-form-item label="最符合计划的操作">
          <el-input
            v-model="form.best_trade"
            placeholder="例：茅台突破入场，完全按计划执行"
          />
        </el-form-item>

        <el-form-item label="执行纪律备注">
          <el-input
            v-model="form.worst_trade"
            placeholder="例：1笔计划外操作（五粮液），亏损-4.45%。执行纪律评分：65/100"
          />
        </el-form-item>

        <el-form-item label="今日情绪状态">
          <el-radio-group v-model="form.emotion_state">
            <el-radio-button value="冷静">冷静</el-radio-button>
            <el-radio-button value="略有波动">略有波动</el-radio-button>
            <el-radio-button value="明显情绪化">明显情绪化</el-radio-button>
            <el-radio-button value="失控">失控</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="今日最重要的一条教训">
          <el-input
            v-model="form.key_lesson"
            placeholder="一句话，必填"
          />
        </el-form-item>
      </el-card>

      <el-card shadow="never">
        <template #header><span class="card-title">🧠 深度思考</span></template>

        <el-form-item label="如果今天重来，改变哪个决策？">
          <el-input
            v-model="form.counterfactual"
            type="textarea" :rows="3"
            placeholder="反事实思考..."
          />
        </el-form-item>

        <el-form-item label="明日可验证假设">
          <el-input
            v-model="form.next_hypothesis"
            type="textarea" :rows="3"
            placeholder="例：若明日茅台开盘在1750上方且量能>今日，则持有..."
          />
        </el-form-item>

        <el-form-item label="这次盈利有多少是运气？">
          <el-radio-group v-model="form.luck_ratio">
            <el-radio-button value="纯实力">纯实力</el-radio-button>
            <el-radio-button value="主要实力">主要实力</el-radio-button>
            <el-radio-button value="一半一半">一半一半</el-radio-button>
            <el-radio-button value="主要运气">主要运气</el-radio-button>
            <el-radio-button value="纯运气">纯运气</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useReviewStore } from '@/stores/review'

const store = useReviewStore()
const { form, vsRows } = storeToRefs(store)
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

.kpi-card { background: var(--el-fill-color-lighter); margin-bottom: 12px; }
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-item { display: flex; flex-direction: column; gap: 6px; }
.kpi-label { font-size: 11px; color: var(--el-text-color-secondary); }

.card-title { font-size: 13px; font-weight: 600; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }

.vs-table-wrap {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.vs-row {
  display: grid;
  grid-template-columns: 1fr 1fr 36px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.vs-row:last-of-type { border-bottom: none; }

.vs-head {
  background: var(--el-fill-color-lighter);
  font-size: 12px;
  font-weight: 600;
}

.vs-cell-plan,
.vs-cell-actual,
.vs-cell-del {
  padding: 8px 12px;
  display: flex;
  align-items: center;
}

.vs-cell-plan {
  border-right: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
}
.vs-actual-red { color: #C8102E; }
.vs-cell-del { padding: 4px; justify-content: center; }

.vs-cell-plan :deep(.el-input__wrapper),
.vs-cell-actual :deep(.el-input__wrapper) {
  box-shadow: none !important;
  background: transparent;
  padding: 0;
}

.discipline-note {
  margin-top: 10px;
  padding: 9px 12px;
  background: #FEF0F0;
  border: 1px solid #FBC4C4;
  border-left: 3px solid #C8102E;
  border-radius: 2px;
  font-size: 12px;
  color: #792020;
}

.op-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}
</style>
