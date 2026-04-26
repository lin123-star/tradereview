<template>
  <div class="audit-page">

    <div class="page-header">
      <div>
        <h2 class="page-title">AI 审讯室</h2>
        <div class="page-sub">苏格拉底式追问 · 发现认知盲区</div>
      </div>
    </div>

    <div class="audit-layout">

      <!-- 左侧：待审讯列表 -->
      <div class="trade-list-col">
        <div class="col-title">
          待审讯交易
          <el-badge
            v-if="pendingTrades.length"
            :value="pendingTrades.length"
            type="danger"
            style="margin-left:6px"
          />
        </div>

        <div v-if="loadingTrades" class="list-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
        </div>

        <div v-else-if="!pendingTrades.length" class="list-empty">
          <el-empty :image-size="60" description="暂无待审讯交易" />
        </div>

        <div
          v-for="t in pendingTrades"
          :key="t.id"
          class="trade-card"
          :class="{ active: selectedTrade?.id === t.id }"
          @click="selectTrade(t)"
        >
          <div class="tc-top">
            <span class="tc-symbol">{{ t.symbol }}</span>
            <span class="tc-name">{{ t.name }}</span>
            <span
              :class="['tc-pnl', (t.pnl_amount ?? 0) >= 0 ? 'pos' : 'neg']"
            >
              {{ (t.pnl_amount ?? 0) >= 0 ? '+' : '' }}{{ t.pnl_amount?.toFixed(0) ?? '持仓中' }}元
            </span>
          </div>
          <div class="tc-bottom">
            <el-tag size="small" :type="dirType(t.direction)">{{ dirLabel(t.direction) }}</el-tag>
            <span class="tc-meta">{{ emotionLabel(t.emotion) }}</span>
            <span class="tc-meta">{{ formatDate(t.entry_time) }}</span>
          </div>
          <div class="tc-status">
            <el-tag
              size="small"
              :type="t.review_status === 'reviewing' ? 'warning' : 'info'"
            >
              {{ t.review_status === 'reviewing' ? '审讯中' : '待开始' }}
            </el-tag>
          </div>
        </div>

        <!-- 已完成的审讯 -->
        <div class="col-title" style="margin-top:16px">
          已完成审讯
        </div>
        <div
          v-for="t in doneTrades"
          :key="t.id"
          class="trade-card done"
          @click="selectTrade(t)"
        >
          <div class="tc-top">
            <span class="tc-symbol">{{ t.symbol }}</span>
            <span class="tc-name">{{ t.name }}</span>
            <span :class="['tc-pnl', (t.pnl_amount ?? 0) >= 0 ? 'pos' : 'neg']">
              {{ (t.pnl_amount ?? 0) >= 0 ? '+' : '' }}{{ t.pnl_amount?.toFixed(0) }}元
            </span>
          </div>
          <div class="tc-bottom">
            <el-tag size="small" type="success">已完成</el-tag>
            <span class="tc-meta">{{ formatDate(t.entry_time) }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：审讯对话区 -->
      <div class="chat-col">

        <!-- 未选择交易时的提示 -->
        <div v-if="!selectedTrade" class="chat-empty">
          <div class="chat-empty-icon">⚡</div>
          <div class="chat-empty-title">选择一笔交易开始审讯</div>
          <div class="chat-empty-sub">AI将基于你的交易记录发起苏格拉底式质疑</div>
        </div>

        <template v-else>
          <!-- 交易信息条 -->
          <div class="trade-info-bar">
            <div class="tib-left">
              <span class="tib-symbol">{{ selectedTrade.symbol }}</span>
              <span class="tib-name">{{ selectedTrade.name }}</span>
              <el-tag size="small" :type="dirType(selectedTrade.direction)">
                {{ dirLabel(selectedTrade.direction) }}
              </el-tag>
            </div>
            <div class="tib-right">
              <span class="tib-price">入场 ¥{{ selectedTrade.entry_price }}</span>
              <span v-if="selectedTrade.exit_price" class="tib-price">
                出场 ¥{{ selectedTrade.exit_price }}
              </span>
              <span
                v-if="selectedTrade.pnl_amount != null"
                :class="['tib-pnl', selectedTrade.pnl_amount >= 0 ? 'pos' : 'neg']"
              >
                {{ selectedTrade.pnl_amount >= 0 ? '+' : '' }}{{ selectedTrade.pnl_amount.toFixed(0) }}元
              </span>
            </div>
          </div>

          <!-- 聊天区域 -->
          <div class="chat-area" ref="chatAreaRef">

            <!-- 开始提示 -->
            <div v-if="!currentSession && !starting" class="start-tip">
              <el-button
                type="primary"
                size="large"
                :loading="starting"
                style="background:#C8102E;border-color:#C8102E"
                @click="startAudit"
              >
                ⚡ 开始审讯
              </el-button>
              <div style="font-size:12px;color:var(--el-text-color-secondary);margin-top:8px">
                AI将分析你的入场逻辑并提出第一个质疑性问题
              </div>
            </div>

            <div v-if="starting" class="msg-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              AI正在分析交易记录...
            </div>

            <!-- 对话消息 -->
            <template v-if="currentSession">
              <div
                v-for="(msg, idx) in currentSession.messages"
                :key="idx"
                :class="['msg-wrap', msg.role === 'ai' ? 'ai' : 'user']"
              >
                <div class="msg-role">
                  {{ msg.role === 'ai' ? 'AI · 苏格拉底' : '我的回答' }}
                </div>
                <div :class="['msg-bubble', msg.role]">
                  {{ msg.content }}
                </div>
              </div>

              <!-- AI 回复中 -->
              <div v-if="replying" class="msg-wrap ai">
                <div class="msg-role">AI · 苏格拉底</div>
                <div class="msg-bubble ai thinking">
                  <span class="dot-1">●</span>
                  <span class="dot-2">●</span>
                  <span class="dot-3">●</span>
                </div>
              </div>
            </template>
          </div>

          <!-- 已识别盲区 -->
          <div
            v-if="currentSession?.blind_spots?.length"
            class="blind-spots-bar"
          >
            <span class="bs-label">⚠ 已识别盲区：</span>
            <el-tag
              v-for="bs in currentSession.blind_spots"
              :key="bs"
              type="warning"
              size="small"
              style="margin-right:6px"
            >{{ bs }}</el-tag>
          </div>

          <!-- 审讯完成总结 -->
          <div
            v-if="currentSession?.status === 'completed'"
            class="summary-bar"
          >
            <div class="summary-title">✅ 审讯完成 · 认知盲区总结</div>
            <div class="summary-content">{{ currentSession.summary }}</div>
            <div style="margin-top:10px;display:flex;gap:8px">
              <el-button size="small" @click="restartAudit">重新审讯</el-button>
            </div>
          </div>

          <!-- 输入区 -->
          <div
            v-if="currentSession?.status === 'active'"
            class="input-area"
          >
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="3"
              placeholder="输入你的回答..."
              :disabled="replying"
              @keydown.ctrl.enter="sendReply"
            />
            <div class="input-footer">
              <span class="input-hint">Ctrl + Enter 发送</span>
              <el-button
                type="primary"
                :loading="replying"
                style="background:#C8102E;border-color:#C8102E"
                @click="sendReply"
              >发送回答</el-button>
            </div>
          </div>

        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { tradeApi, type TradeOut } from '@/api/trade'
import { socraticApi, type SessionOut } from '@/api/socratic'

// ── 状态 ──────────────────────────────────────────────
const allTrades = ref<TradeOut[]>([])
const loadingTrades = ref(false)
const selectedTrade = ref<TradeOut | null>(null)
const currentSession = ref<SessionOut | null>(null)
const starting = ref(false)
const replying = ref(false)
const userInput = ref('')
const chatAreaRef = ref<HTMLElement>()

// ── 计算属性 ──────────────────────────────────────────
const pendingTrades = computed(() =>
  allTrades.value.filter(t =>
    t.status === 'closed' && ['pending', 'reviewing'].includes(t.review_status)
  )
)

const doneTrades = computed(() =>
  allTrades.value.filter(t => t.review_status === 'done')
)

// ── 加载交易列表 ──────────────────────────────────────
async function loadTrades() {
  loadingTrades.value = true
  try {
    const res = await tradeApi.list({ status: 'closed', limit: 100 })
    allTrades.value = res.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载交易列表失败')
  } finally {
    loadingTrades.value = false
  }
}

// ── 选择交易 ──────────────────────────────────────────
async function selectTrade(trade: TradeOut) {
  selectedTrade.value = trade
  currentSession.value = null

  // 加载已有的审讯会话
  try {
    const sessions = await socraticApi.getByTrade(trade.id)
    if (sessions.length) {
      currentSession.value = sessions[0]
      await scrollToBottom()
    }
  } catch {}
}

// ── 开始审讯 ──────────────────────────────────────────
async function startAudit() {
  if (!selectedTrade.value) return
  starting.value = true
  try {
    const session = await socraticApi.start(selectedTrade.value.id)
    currentSession.value = session
    // 刷新交易状态
    await loadTrades()
    await scrollToBottom()
  } catch (e: any) {
    ElMessage.error(e.message || '启动审讯失败')
  } finally {
    starting.value = false
  }
}

// ── 发送回答 ──────────────────────────────────────────
async function sendReply() {
  if (!userInput.value.trim() || !currentSession.value) return
  if (replying.value) return

  const msg = userInput.value.trim()
  userInput.value = ''

  // 乐观更新：先把用户消息加进去
  currentSession.value.messages.push({ role: 'user', content: msg })
  await scrollToBottom()

  replying.value = true
  try {
    const result = await socraticApi.reply(currentSession.value.id, msg)

    // 更新会话状态
    currentSession.value.messages.push({ role: 'ai', content: result.ai_message })
    currentSession.value.blind_spots = result.blind_spots
    currentSession.value.status = result.status as any
    if (result.summary) {
      currentSession.value.summary = result.summary
    }

    // 刷新交易列表（review_status 会变化）
    if (result.status === 'completed') {
      await loadTrades()
    }

    await scrollToBottom()
  } catch (e: any) {
    ElMessage.error(e.message || '发送失败')
    // 回滚乐观更新
    currentSession.value.messages.pop()
  } finally {
    replying.value = false
  }
}

// ── 重新审讯 ──────────────────────────────────────────
async function restartAudit() {
  if (!selectedTrade.value) return
  currentSession.value = null
}

// ── 工具函数 ──────────────────────────────────────────
async function scrollToBottom() {
  await nextTick()
  if (chatAreaRef.value) {
    chatAreaRef.value.scrollTop = chatAreaRef.value.scrollHeight
  }
}

function dirLabel(d: string) {
  return { buy: '买入', sell: '卖出', add: '加仓', reduce: '减仓' }[d] || d
}

function dirType(d: string): 'success' | 'danger' | 'info' {
  return ['buy', 'add'].includes(d) ? 'success' : 'danger'
}

function emotionLabel(e: string) {
  return { calm: '冷静', greedy: '贪婪', panic: '恐慌', hesitant: '犹豫', impulsive: '冲动' }[e] || e
}

function formatDate(t: string) {
  return t ? t.slice(0, 10) : ''
}

onMounted(() => loadTrades())
</script>

<style scoped>
.audit-page { padding: 20px 24px; height: calc(100vh - 102px); display: flex; flex-direction: column; }

.page-header { margin-bottom: 16px; flex-shrink: 0; }
.page-title { font-family: 'Noto Serif SC', serif; font-size: 20px; font-weight: 700; margin: 0; }
.page-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

.audit-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  flex: 1;
  overflow: hidden;
}

/* 左侧列表 */
.trade-list-col {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  gap: 8px;
}
.trade-list-col::-webkit-scrollbar { width: 4px; }
.trade-list-col::-webkit-scrollbar-thumb { background: var(--el-border-color); border-radius: 2px; }

.col-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 4px 0;
  flex-shrink: 0;
}

.list-loading, .list-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: var(--el-text-color-secondary);
  gap: 8px;
}

.trade-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all .15s;
  flex-shrink: 0;
}

.trade-card:hover { border-color: #C8102E; }
.trade-card.active { border-color: #C8102E; background: #FEF0F0; }
.trade-card.done { opacity: 0.7; }

.tc-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tc-symbol { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 13px; }
.tc-name { font-size: 11px; color: var(--el-text-color-secondary); flex: 1; }
.tc-pnl { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; }
.tc-pnl.pos { color: #1A7C3E; }
.tc-pnl.neg { color: #C8102E; }

.tc-bottom { display: flex; align-items: center; gap: 6px; }
.tc-meta { font-size: 10px; color: var(--el-text-color-secondary); }
.tc-status { margin-top: 5px; }

/* 右侧聊天区 */
.chat-col {
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
}

.chat-empty-icon { font-size: 48px; margin-bottom: 12px; }
.chat-empty-title { font-size: 16px; font-weight: 500; color: var(--el-text-color-primary); margin-bottom: 6px; }
.chat-empty-sub { font-size: 13px; }

/* 交易信息条 */
.trade-info-bar {
  padding: 10px 16px;
  background: #FEF0F0;
  border-bottom: 1px solid #FBC4C4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.tib-left { display: flex; align-items: center; gap: 8px; }
.tib-symbol { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 14px; }
.tib-name { font-size: 12px; color: var(--el-text-color-secondary); }
.tib-right { display: flex; align-items: center; gap: 12px; }
.tib-price { font-size: 12px; color: var(--el-text-color-secondary); }
.tib-pnl { font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 13px; }
.tib-pnl.pos { color: #1A7C3E; }
.tib-pnl.neg { color: #C8102E; }

/* 聊天区域 */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #FAFBFC;
}

.chat-area::-webkit-scrollbar { width: 4px; }
.chat-area::-webkit-scrollbar-thumb { background: var(--el-border-color); border-radius: 2px; }

.start-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 8px;
  padding: 40px;
}

.msg-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 20px;
}

.msg-wrap { display: flex; flex-direction: column; gap: 4px; }
.msg-wrap.user { align-items: flex-end; }

.msg-role {
  font-size: 10px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
  padding: 0 2px;
}

.msg-wrap.ai .msg-role { color: #C8102E; }

.msg-bubble {
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.7;
  border-radius: 4px;
  font-family: 'Noto Serif SC', serif;
  max-width: 90%;
  white-space: pre-wrap;
}

.msg-bubble.ai {
  background: white;
  border: 1px solid var(--el-border-color);
  border-left: 3px solid #C8102E;
}

.msg-bubble.user {
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-7);
}

.msg-bubble.thinking {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px;
}

.dot-1, .dot-2, .dot-3 {
  font-size: 8px;
  color: #C8102E;
  animation: bounce 1.2s infinite;
}
.dot-2 { animation-delay: 0.2s; }
.dot-3 { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { opacity: 0.3; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-4px); }
}

/* 盲区栏 */
.blind-spots-bar {
  padding: 8px 16px;
  background: #FFFAF0;
  border-top: 1px solid #FFE4B5;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  flex-shrink: 0;
}

.bs-label {
  font-size: 11px;
  color: #B8860B;
  font-weight: 600;
  white-space: nowrap;
}

/* 审讯总结 */
.summary-bar {
  padding: 14px 16px;
  background: #F0F9F0;
  border-top: 1px solid #A8D5B8;
  flex-shrink: 0;
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: #1A7C3E;
  margin-bottom: 8px;
}

.summary-content {
  font-size: 13px;
  line-height: 1.7;
  color: var(--el-text-color-primary);
  font-family: 'Noto Serif SC', serif;
  white-space: pre-wrap;
}

/* 输入区 */
.input-area {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color);
  background: white;
  flex-shrink: 0;
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.input-hint { font-size: 11px; color: var(--el-text-color-secondary); }
</style>
