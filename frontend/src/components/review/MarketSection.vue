<template>
  <div class="review-section">
    <div class="section-head">一、盘面梳理</div>

    <!-- 大盘情绪 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="card-title">📊 大盘情绪</span>
      </template>

      <el-form-item label="大盘整体研判">
        <el-input
          v-model="form.market_overview"
          type="textarea"
          :rows="3"
          placeholder="例：上证涨0.87%，温和放量，资金持续流入大消费和低估值蓝筹，情绪偏乐观无亢奋迹象..."
        />
      </el-form-item>

      <el-form-item label="与早盘研判对比">
        <el-radio-group v-model="form.plan_accuracy">
          <el-radio-button value="accurate">基本准确</el-radio-button>
          <el-radio-button value="partial">部分准确</el-radio-button>
          <el-radio-button value="off">有偏差</el-radio-button>
          <el-radio-button value="wrong">完全偏差</el-radio-button>
        </el-radio-group>
      </el-form-item>
    </el-card>

    <!-- 市场风格 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="card-title">🔄 市场风格</span>
      </template>

      <el-form-item label="今日主导风格">
        <el-radio-group v-model="form.market_style">
          <el-radio-button value="大盘蓝筹">大盘蓝筹</el-radio-button>
          <el-radio-button value="中小盘成长">中小盘成长</el-radio-button>
          <el-radio-button value="高股息价值">高股息价值</el-radio-button>
          <el-radio-button value="题材概念">题材概念</el-radio-button>
          <el-radio-button value="无明显主线">无明显主线</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="大小盘分化">
        <el-radio-group v-model="form.market_split">
          <el-radio-button value="大盘强/小盘弱">大盘强/小盘弱</el-radio-button>
          <el-radio-button value="小盘强/大盘弱">小盘强/大盘弱</el-radio-button>
          <el-radio-button value="同向上涨">同向上涨</el-radio-button>
          <el-radio-button value="同向下跌">同向下跌</el-radio-button>
          <el-radio-button value="分化混乱">分化混乱</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="风格描述">
        <el-input
          v-model="form.style_desc"
          type="textarea"
          :rows="3"
          placeholder="例：北向资金持续流入白马股，大盘蓝筹整体强势；前期热门题材股继续降温，中小盘资金撤离明显..."
        />
      </el-form-item>
    </el-card>

    <!-- 板块强弱 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="card-title">📈 板块强弱梳理</span>
      </template>

      <el-form-item label="今日领涨板块">
        <template #label>
          <span class="form-label-with-hint">
            今日领涨板块
            <span class="label-hint">板块名 + 涨幅 + 核心逻辑</span>
          </span>
        </template>
        <el-input
          v-model="form.leading_sectors"
          type="textarea"
          :rows="3"
          placeholder="例：白酒 +3.21%，消费数据超预期+茅台批价回升；新能源车 +2.87%，比亚迪销量数据强劲..."
        />
      </el-form-item>

      <el-form-item label="今日领跌板块">
        <template #label>
          <span class="form-label-with-hint">
            今日领跌板块
            <span class="label-hint">板块名 + 跌幅 + 原因</span>
          </span>
        </template>
        <el-input
          v-model="form.lagging_sectors"
          type="textarea"
          :rows="2"
          placeholder="例：半导体 -2.33%，获利回吐；地产 -1.87%，销售数据不及预期..."
        />
      </el-form-item>

      <el-form-item label="板块主线总结">
        <template #label>
          <span class="form-label-with-hint">
            板块主线总结
            <span class="label-hint">主线逻辑是否清晰？明日是否延续？</span>
          </span>
        </template>
        <el-input
          v-model="form.sector_summary"
          type="textarea"
          :rows="3"
          placeholder="例：今日主线是消费复苏预期，逻辑清晰有数据支撑。明日关注白酒是否继续，军工能否接棒成为次主线..."
        />
      </el-form-item>
    </el-card>
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
.section-card { margin-bottom: 12px; border-radius: 4px; }
.section-card:last-child { margin-bottom: 0; }
.card-title { font-size: 13px; font-weight: 600; }
.form-label-with-hint { display: flex; flex-direction: column; gap: 2px; }
.label-hint { font-size: 11px; color: var(--el-text-color-secondary); font-weight: 400; }
</style>
