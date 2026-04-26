<template>
  <div class="strategy-selector">

    <!-- 选择已有策略 -->
    <div class="select-row">
      <el-select
        v-model="selectedId"
        placeholder="选择策略标签"
        clearable
        filterable
        style="flex:1"
        @change="onSelect"
      >
        <el-option
          v-for="s in strategies"
          :key="s.id"
          :value="s.id"
          :label="s.name"
        >
          <div class="opt-row">
            <span class="opt-name">{{ s.name }}</span>
            <span v-if="s.total_count > 0" class="opt-stat">
              胜率 {{ (s.win_rate * 100).toFixed(0) }}% · {{ s.total_count }}笔
            </span>
            <span v-else class="opt-stat">暂无数据</span>
          </div>
        </el-option>
      </el-select>
      <el-button plain @click="showCreate = true">+ 新建策略</el-button>
    </div>

    <!-- 已选策略详情预览 -->
    <div v-if="selectedStrategy" class="strategy-preview">
      <div class="preview-header">
        <span class="preview-name">{{ selectedStrategy.name }}</span>
        <el-button size="small" text @click="showEdit = true">编辑</el-button>
      </div>
      <div v-if="selectedStrategy.entry_signal" class="preview-field">
        <span class="pf-label">入场信号：</span>{{ selectedStrategy.entry_signal }}
      </div>
      <div v-if="selectedStrategy.stop_loss_rule" class="preview-field">
        <span class="pf-label">止损规则：</span>{{ selectedStrategy.stop_loss_rule }}
      </div>
      <div v-if="selectedStrategy.take_profit_rule" class="preview-field">
        <span class="pf-label">目标位：</span>{{ selectedStrategy.take_profit_rule }}
      </div>
      <div v-if="selectedStrategy.total_count > 0" class="preview-stats">
        <span :class="['stat-val', selectedStrategy.win_rate >= 0.5 ? 'pos' : 'neg']">
          胜率 {{ (selectedStrategy.win_rate * 100).toFixed(1) }}%
        </span>
        <span class="stat-sep">·</span>
        <span class="stat-val">共 {{ selectedStrategy.total_count }} 笔</span>
        <span class="stat-sep">·</span>
        <span :class="['stat-val', selectedStrategy.avg_pnl_ratio >= 0 ? 'pos' : 'neg']">
          均盈亏 {{ (selectedStrategy.avg_pnl_ratio * 100).toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- 新建策略弹窗 -->
    <el-dialog
      v-model="showCreate"
      title="新建策略标签"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" label-position="top">
        <el-form-item label="策略名称" required>
          <el-input
            v-model="createForm.name"
            placeholder="例：均线金叉+量能放大、MACD底背离+板块强势"
          />
        </el-form-item>
        <el-form-item label="大类">
          <el-radio-group v-model="createForm.category">
            <el-radio-button value="trend">趋势跟踪</el-radio-button>
            <el-radio-button value="reversal">反转</el-radio-button>
            <el-radio-button value="news">消息面</el-radio-button>
            <el-radio-button value="quant">量化信号</el-radio-button>
            <el-radio-button value="other">其他</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="入场信号">
          <el-input
            v-model="createForm.entry_signal"
            type="textarea"
            :rows="2"
            placeholder="例：MA5上穿MA10且成交量>5日均量的1.5倍，MACD柱由负转正"
          />
        </el-form-item>
        <el-form-item label="止损规则">
          <el-input
            v-model="createForm.stop_loss_rule"
            type="textarea"
            :rows="2"
            placeholder="例：跌破MA10或亏损超过3%止损，取先到者"
          />
        </el-form-item>
        <el-form-item label="目标位规则">
          <el-input
            v-model="createForm.take_profit_rule"
            type="textarea"
            :rows="2"
            placeholder="例：第一目标前高，第二目标止盈线，盈利超8%减半仓"
          />
        </el-form-item>
        <el-form-item label="适用市场环境">
          <el-input
            v-model="createForm.applicable_market"
            placeholder="例：趋势市、大盘上涨且板块强势时"
          />
        </el-form-item>
        <el-form-item label="策略简介">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="2"
            placeholder="简单描述这个策略的核心逻辑..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button
          type="primary"
          :loading="creating"
          style="background:#C8102E;border-color:#C8102E"
          @click="handleCreate"
        >创建策略</el-button>
      </template>
    </el-dialog>

    <!-- 编辑策略弹窗 -->
    <el-dialog
      v-model="showEdit"
      title="编辑策略标签"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form v-if="selectedStrategy" :model="editForm" label-position="top">
        <el-form-item label="策略名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="入场信号">
          <el-input v-model="editForm.entry_signal" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="止损规则">
          <el-input v-model="editForm.stop_loss_rule" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="目标位规则">
          <el-input v-model="editForm.take_profit_rule" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="策略简介">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="danger" plain @click="handleDelete">删除策略</el-button>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button
          type="primary"
          :loading="editing"
          style="background:#C8102E;border-color:#C8102E"
          @click="handleEdit"
        >保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { strategyApi, type Strategy, type StrategyCreate } from '@/api/strategy'

const props = defineProps<{
  modelValue: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [val: number | null]
  'change': [strategy: Strategy | null]
}>()

const strategies = ref<Strategy[]>([])
const selectedId = ref<number | null>(props.modelValue)
const showCreate = ref(false)
const showEdit = ref(false)
const creating = ref(false)
const editing = ref(false)

const selectedStrategy = computed(() =>
  strategies.value.find(s => s.id === selectedId.value) || null
)

const createForm = ref<StrategyCreate>({
  name: '', category: 'trend',
  description: '', entry_signal: '',
  stop_loss_rule: '', take_profit_rule: '',
  applicable_market: '',
})

const editForm = ref<Partial<StrategyCreate>>({})

watch(() => props.modelValue, val => { selectedId.value = val })

watch(selectedId, val => {
  emit('update:modelValue', val)
  emit('change', selectedStrategy.value)
})

watch(showEdit, val => {
  if (val && selectedStrategy.value) {
    const s = selectedStrategy.value
    editForm.value = {
      name: s.name,
      entry_signal: s.entry_signal,
      stop_loss_rule: s.stop_loss_rule,
      take_profit_rule: s.take_profit_rule,
      description: s.description,
    }
  }
})

async function loadStrategies() {
  try {
    strategies.value = await strategyApi.getAll()
  } catch (e: any) {
    ElMessage.error(e.message || '加载策略列表失败')
  }
}

function onSelect(val: number | null) {
  selectedId.value = val
}

async function handleCreate() {
  if (!createForm.value.name.trim()) {
    ElMessage.warning('请填写策略名称')
    return
  }
  creating.value = true
  try {
    const created = await strategyApi.create(createForm.value)
    strategies.value.unshift(created)
    selectedId.value = created.id
    showCreate.value = false
    createForm.value = {
      name: '', category: 'trend', description: '',
      entry_signal: '', stop_loss_rule: '',
      take_profit_rule: '', applicable_market: '',
    }
    ElMessage.success(`策略「${created.name}」已创建`)
  } catch (e: any) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    creating.value = false
  }
}

async function handleEdit() {
  if (!selectedStrategy.value) return
  editing.value = true
  try {
    const updated = await strategyApi.update(selectedStrategy.value.id, editForm.value)
    const idx = strategies.value.findIndex(s => s.id === updated.id)
    if (idx !== -1) strategies.value[idx] = updated
    showEdit.value = false
    ElMessage.success('策略已更新')
  } catch (e: any) {
    ElMessage.error(e.message || '更新失败')
  } finally {
    editing.value = false
  }
}

async function handleDelete() {
  if (!selectedStrategy.value) return
  try {
    await ElMessageBox.confirm(
      `确认删除策略「${selectedStrategy.value.name}」？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
    await strategyApi.delete(selectedStrategy.value.id)
    strategies.value = strategies.value.filter(s => s.id !== selectedStrategy.value!.id)
    selectedId.value = null
    showEdit.value = false
    ElMessage.success('已删除')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

onMounted(loadStrategies)
</script>

<style scoped>
.strategy-selector { display: flex; flex-direction: column; gap: 8px; }

.select-row { display: flex; gap: 8px; align-items: center; }

.opt-row { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.opt-name { font-size: 13px; }
.opt-stat { font-size: 11px; color: var(--el-text-color-secondary); }

.strategy-preview {
  padding: 10px 13px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color);
  border-left: 3px solid #C8102E;
  border-radius: 3px;
  font-size: 12.5px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.preview-name { font-weight: 600; font-size: 13px; color: var(--el-text-color-primary); }

.preview-field {
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  line-height: 1.5;
}
.pf-label { color: var(--el-text-color-primary); font-weight: 500; }

.preview-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.stat-val { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 500; }
.stat-val.pos { color: #1A7C3E; }
.stat-val.neg { color: #C8102E; }
.stat-sep { color: var(--el-text-color-secondary); }
</style>