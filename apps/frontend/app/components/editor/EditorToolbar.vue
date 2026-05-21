<template>
  <div class="toolbar">
    <button
      class="run-btn"
      :class="{ running: isRunning }"
      @click="isRunning ? cancelExecution() : runQuery()"
      :disabled="!connStore.activeConnectionId"
      :title="isRunning ? 'Cancel (Esc)' : 'Run (Ctrl+Enter)'"
    >
      <span v-if="isRunning">⬛ Cancel</span>
      <span v-else>▶ Run</span>
    </button>

    <button class="toolbar-btn" @click="formatSql" title="Format SQL (Ctrl+Shift+F)">
      ✦ Format
    </button>

    <span
      v-if="analysis && analysis.needs_transaction_wrap"
      class="badge badge-info"
      title="Query will be wrapped in BEGIN/COMMIT"
    >
      AUTO-TXN
    </span>

    <span v-if="analysis && analysis.risk_level === 'high'" class="badge badge-danger">
      ⚠ HIGH RISK
    </span>

    <span v-if="analysis && analysis.risk_level === 'medium'" class="badge badge-warn">
      ⚡ MEDIUM RISK
    </span>

    <div class="toolbar-spacer" />

    <span class="timeout-info" title="Max query runtime">
      ⏱ {{ maxTimeout }}s limit
    </span>
  </div>
</template>

<script setup lang="ts">
import { format } from "sql-formatter"

const editor = useEditorStore()
const connStore = useConnectionStore()
const auth = useAuthStore()
const config = useRuntimeConfig()

const maxTimeout = 60
const isRunning = ref(false)
const analysis = ref<any>(null)
let ws: WebSocket | null = null
let currentExecutionId = ref<string | null>(null)

async function runQuery() {
  const tab = editor.activeTab
  if (!tab || !connStore.activeConnectionId || !tab.sql.trim()) return

  isRunning.value = true
  editor.setTabResults(tab.id, {
    results: null,
    columns: null,
    executionStatus: "running",
    error: null,
    hasUndo: false,
    historyId: null,
  })

  try {
    const response: any = await $fetch(`${config.public.apiBase}/api/v1/queries/execute`, {
      method: "POST",
      headers: { Authorization: `Bearer ${auth.accessToken}` },
      body: {
        connection_id: connStore.activeConnectionId,
        sql: tab.sql,
        tab_id: tab.id,
      },
    })

    analysis.value = response.analysis
    currentExecutionId.value = response.execution_id
    editor.setTabResults(tab.id, { executionId: response.execution_id, historyId: response.history_id })

    // Open WebSocket for streaming
    ws = new WebSocket(`${config.public.wsBase}/ws/queries/${response.execution_id}`)
    ws.onmessage = (evt) => handleWsMessage(tab.id, JSON.parse(evt.data))
    ws.onerror = () => { isRunning.value = false }
    ws.onclose = () => { isRunning.value = false }
  } catch (e: any) {
    editor.setTabResults(tab.id, { executionStatus: "error", error: e?.data?.message || e?.message || "Failed" })
    isRunning.value = false
  }
}

function handleWsMessage(tabId: string, msg: any) {
  if (msg.type === "row_batch") {
    if (msg.columns) editor.setTabResults(tabId, { columns: msg.columns })
    editor.appendTabRows(tabId, msg.rows)
  } else if (msg.type === "complete") {
    editor.setTabResults(tabId, {
      executionStatus: "complete",
      executionTimeMs: msg.execution_time_ms,
      rowCount: msg.row_count,
      rowsAffected: msg.rows_affected,
      hasUndo: msg.has_undo,
    })
    isRunning.value = false
    ws?.close()
  } else if (msg.type === "error") {
    editor.setTabResults(tabId, { executionStatus: "error", error: msg.message })
    isRunning.value = false
    ws?.close()
  } else if (msg.type === "cancelled") {
    editor.setTabResults(tabId, { executionStatus: "cancelled" })
    isRunning.value = false
    ws?.close()
  }
}

async function cancelExecution() {
  if (!currentExecutionId.value) return
  await $fetch(`${config.public.apiBase}/api/v1/queries/executions/${currentExecutionId.value}/cancel`, {
    method: "POST",
    headers: { Authorization: `Bearer ${auth.accessToken}` },
  })
}

function formatSql() {
  const tab = editor.activeTab
  if (!tab) return
  try {
    const formatted = format(tab.sql, { language: "postgresql", tabWidth: 2 })
    editor.setTabSql(tab.id, formatted)
  } catch (e) {}
}

// Keyboard shortcuts
onMounted(() => {
  window.addEventListener("keydown", handleKeydown)
})
onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown)
})

function handleKeydown(e: KeyboardEvent) {
  const ctrl = e.ctrlKey || e.metaKey
  if ((ctrl && e.key === "Enter") || e.key === "F5") {
    e.preventDefault()
    if (!isRunning.value) runQuery()
  }
  if (ctrl && e.shiftKey && e.key === "F") {
    e.preventDefault()
    formatSql()
  }
  if (e.key === "Escape" && isRunning.value) {
    cancelExecution()
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 40px;
  padding: 0 0.75rem;
  background: var(--stratum-bg-secondary);
  border-bottom: 1px solid var(--stratum-border);
  flex-shrink: 0;
}
.run-btn {
  padding: 0.3rem 0.875rem;
  border: none;
  border-radius: 6px;
  background: var(--stratum-accent);
  color: white;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.run-btn:hover { background: var(--stratum-accent-hover); }
.run-btn.running { background: var(--stratum-error); }
.run-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.toolbar-btn {
  padding: 0.3rem 0.625rem;
  border: 1px solid var(--stratum-border);
  border-radius: 6px;
  background: transparent;
  color: var(--stratum-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
}
.toolbar-btn:hover { background: var(--stratum-bg-tertiary); color: var(--stratum-text-primary); }
.toolbar-spacer { flex: 1; }
.badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}
.badge-info { background: rgba(91,108,242,0.15); color: var(--stratum-accent); }
.badge-danger { background: rgba(239,68,68,0.15); color: var(--stratum-error); }
.badge-warn { background: rgba(245,158,11,0.15); color: var(--stratum-warning); }
.timeout-info { font-size: 0.75rem; color: var(--stratum-text-muted); }
</style>
