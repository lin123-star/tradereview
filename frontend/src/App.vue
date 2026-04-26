<template>
  <el-container class="app-shell">

    <el-aside width="200px" class="sidebar">
      <div class="logo-area">
        <div class="logo-main"><span class="logo-red">盘</span>后 · TradeReview</div>
        <div class="logo-sub">AI增强交易复盘系统</div>
      </div>

      <el-menu
        :default-active="$route.name as string"
        router
        class="sidebar-menu"
        background-color="#1A1F2E"
        text-color="rgba(255,255,255,0.55)"
        active-text-color="#ffffff"
      >
        <div class="menu-section">主导航</div>

        <el-menu-item index="dashboard" route="/dashboard">
          <span class="menu-icon">◈</span> 仪表台
        </el-menu-item>

        <div class="menu-section">盘前</div>

        <el-menu-item index="plan" route="/plan">
          <span class="menu-icon">📋</span> 每日计划
        </el-menu-item>

        <div class="menu-section">盘中</div>

        <el-menu-item index="trade" route="/trade">
          <span class="menu-icon">⊕</span> 录入交易
        </el-menu-item>

        <div class="menu-section">盘后</div>

        <el-menu-item index="review" route="/review">
          <span class="menu-icon">🌙</span> 每日复盘
        </el-menu-item>

        <el-menu-item index="audit" route="/audit">
          <span class="menu-icon">⚡</span> AI 审讯室
          <el-badge
            v-if="pendingCount > 0"
            :value="pendingCount"
            class="menu-badge"
          />
        </el-menu-item>

        <el-menu-item index="article" route="/article">
          <span class="menu-icon">✦</span> 文章工坊
        </el-menu-item>

      </el-menu>

      <div class="sidebar-footer">
        <div><span class="online-dot"></span>系统运行中</div>
      </div>
    </el-aside>

    <el-container class="main-container">
      <el-header class="top-header" height="50px">
        <div class="header-brand">TradeReview Pro</div>
        <div class="header-date">{{ todayStr }}</div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>

      <div class="ticker-bar">
        <span v-for="t in tickers" :key="t.name" class="tick">
          <span class="tick-name">{{ t.name }}</span>
          <span class="tick-val">{{ t.val }}</span>
          <span :class="['tick-chg', t.up ? 'up' : 'down']">{{ t.chg }}</span>
        </span>
        <span class="tick" style="margin-left:auto" v-if="pendingCount > 0">
          <span class="tick-name">待复盘</span>
          <span class="tick-val" style="color:#C8102E">{{ pendingCount }} 笔</span>
        </span>
      </div>
    </el-container>

  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { tradeApi } from '@/api/trade'

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
})

const pendingCount = ref(0)

async function loadPending() {
  try {
    const res = await tradeApi.list({ status: 'closed', review_status: 'pending', limit: 1 })
    pendingCount.value = res.total
  } catch {}
}

const tickers: any[] = []

onMounted(loadPending)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
html, body, #app { height: 100%; margin: 0; }
body { font-family: 'Noto Sans SC', sans-serif; }
</style>

<style scoped>
.app-shell { height: 100vh; overflow: hidden; }

.sidebar {
  background: #1A1F2E;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-area {
  padding: 18px 16px 14px;
  border-bottom: 1px solid rgba(255,255,255,.07);
  flex-shrink: 0;
}

.logo-main {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px; font-weight: 700; color: #fff;
}

.logo-red { color: #C8102E; }

.logo-sub {
  font-size: 10px;
  color: rgba(255,255,255,.3);
  margin-top: 3px;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(200,16,46,.18) !important;
  border-left: 3px solid #C8102E;
}

.sidebar-menu :deep(.el-menu-item) {
  display: flex;
  align-items: center;
}

.menu-section {
  font-size: 9px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: rgba(255,255,255,.25);
  padding: 10px 20px 4px;
  margin-top: 4px;
}

.menu-icon { margin-right: 6px; }

.menu-badge {
  margin-left: auto;
}

.menu-badge :deep(.el-badge__content) {
  background: #C8102E;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,.07);
  font-size: 10px;
  color: rgba(255,255,255,.3);
  flex-shrink: 0;
}

.online-dot {
  display: inline-block;
  width: 5px; height: 5px; border-radius: 50%;
  background: #1A7C3E;
  box-shadow: 0 0 6px #1A7C3E;
  margin-right: 5px;
}

.main-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.top-header {
  background: #fff;
  border-bottom: 2px solid #C8102E;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-brand {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px; font-weight: 700; color: #C8102E;
}

.header-date { font-size: 12px; color: #8A95A3; }

.main-content {
  flex: 1; overflow-y: auto;
  background: #F5F6F8; padding: 0;
}

.ticker-bar {
  background: #1A1F2E;
  padding: 7px 24px;
  display: flex; gap: 24px;
  overflow: hidden; flex-shrink: 0;
}

.tick { display: flex; gap: 6px; align-items: center; font-size: 11px; white-space: nowrap; }
.tick-name { color: rgba(255,255,255,.4); }
.tick-val  { color: rgba(255,255,255,.85); font-family: 'JetBrains Mono', monospace; }
.tick-chg  { font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.up   { color: #1A7C3E; }
.down { color: #C8102E; }
</style>