<template>
  <div class="review-section">
    <div class="section-head">三、操作复盘</div>

    <div class="op-grid">
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
              style="width: 100%"
            />
          </div>
          <div class="kpi-item">
            <div class="kpi-label">操作笔数</div>
            <el-input-number
              v-model="form.trade_count"
              :min="0"
              :max="50"
              controls-position="right"
              style="width: 100%"
            />
          </div>
          <div class="kpi-item">
            <div class="kpi-label">盈利笔数</div>
            <el-input-number
              v-model="form.win_count"
              :min="0"
              controls-position="right"
              style="width: 100%"
            />
          </div>
          <div class="kpi-item">
            <div class="kpi-label">亏损笔数</div>
            <el-input-number
              v-model="form.loss_count"
              :min="0"
              controls-position="right"
              style="width: 100%"
            />
          </div>
        </div>
      </el-card>

      <!-- 操作总结 -->
      <el-card shadow="never">
        <template #header><span class="card-title">✍️ 操作总结</span></template>

        <el-form-item label="最符合计划的操作">
          <el-input
            v-model="form.best_trade"
            placeholder="例：茅台突破入场，完全按计划执行"
          />
        </el-form-item>

        <el-form-item label="最偏离计划的操作">
          <el-input
            v-model="form.worst_trade"
            placeholder="例：五粮液计划外入场，止损临时决定"
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

      <!-- 深度思考 -->
      <el-card shadow="never">
        <template #header><span class="card-title">🧠 深度思考</span></template>

        <el-form-item label="如果今天重来，改变哪个决策？">
          <el-input
            v-model="form.counterfactual"
            type="textarea"
            :rows="3"
            placeholder="反事实思考..."
          />
        </el-form-item>

        <el-form-item label="明日可验证假设">
          <el-input
            v-model="form.next_hypothesis"
            type="textarea"
            :rows="3"
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
const { form } = storeToRefs(store)
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
.op-grid { display: flex; flex-direction: column; gap: 12px; }
.card-title { font-size: 13px; font-weight: 600; }

.kpi-card { background: var(--el-fill-color-lighter); }
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-item { display: flex; flex-direction: column; gap: 6px; }
.kpi-label { font-size: 11px; color: var(--el-text-color-secondary); }
</style>
