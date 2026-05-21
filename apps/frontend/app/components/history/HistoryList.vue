<template>
  <div class="history-list">
    <div class="history-header">
      <span class="list-title">Query History</span>
      <button class="refresh-btn" @click="history.loadHistory()" title="Refresh">↺</button>
    </div>

    <div v-if="history.isLoading" class="list-loading">Loading…</div>

    <div v-else-if="history.items.length === 0" class="list-empty">No queries yet</div>

    <div
      v-else
      class="history-items"
    >
      <div
        v-for="item in history.items"
        :key="item.id"
        class="history-item"
        @click="loadIntoEditor(item)"
      >
        <div class="item-top">
          <span class="item-sql">{{ item.sql_text.slice(0, 80) }}</span>
        </div>
        <div class="item-meta">
          <span class="status-dot" :class="item.execution_status">●</span>
          <span class="item-time">{{ formatTime(item.created_at) }}</span>
          <span v-if="item.execution_time_ms" class="item-duration">{{ item.execution_time_ms }}ms</span>
          <span v-if="item.row_count != null" class="item-rows">{{ item.row_count }} rows</span>
          <button
            v-if="item.has_undo && !item.undo_executed_at"
            class="undo-mini"
            @click.stop="history.previewUndo(item.id)"
            :title="`Undo available`"
          >↩ Undo</button>
        </div>
        <div v-if="item.error_message" class="item-error">{{ item.error_message.slice(0, 100) }}</div>
      </div>

      <button
        v-if="history.items.length < history.total"
        class="load-more"
        @click="history.loadMore()"
      >
        Load more
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDistanceToNow } from "date-fns"

const history = useHistoryStore()
const editor = useEditorStore()

function loadIntoEditor(item: any) {
  const tab = editor.activeTab
  if (tab) editor.setTabSql(tab.id, item.sql_text)
}

function formatTime(ts: string) {
  return formatDistanceToNow(new Date(ts), { addSuffix: true })
}
</script>

<style scoped>
.history-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--stratum-border);
  flex-shrink: 0;
}
.list-title { font-size: 0.75rem; font-weight: 600; color: var(--stratum-text-secondary); text-transform: uppercase; letter-spacing: 0.04em; }
.refresh-btn { border: none; background: none; cursor: pointer; color: var(--stratum-text-muted); font-size: 0.875rem; }
.refresh-btn:hover { color: var(--stratum-accent); }
.list-loading, .list-empty { padding: 1rem; font-size: 0.8125rem; color: var(--stratum-text-muted); text-align: center; }
.history-items { flex: 1; overflow-y: auto; }
.history-item {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--stratum-border);
  cursor: pointer;
}
.history-item:hover { background: var(--stratum-bg-tertiary); }
.item-top { margin-bottom: 0.25rem; }
.item-sql { font-size: 0.75rem; font-family: "JetBrains Mono", monospace; color: var(--stratum-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.item-meta { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.status-dot { font-size: 0.5rem; }
.status-dot.success { color: var(--stratum-success); }
.status-dot.error { color: var(--stratum-error); }
.status-dot.running { color: var(--stratum-accent); animation: pulse 1.5s infinite; }
.status-dot.pending, .status-dot.queued { color: var(--stratum-warning); }
.status-dot.cancelled { color: var(--stratum-text-muted); }
@keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.4 } }
.item-time, .item-duration, .item-rows { font-size: 0.6875rem; color: var(--stratum-text-muted); }
.undo-mini {
  padding: 0.0625rem 0.375rem;
  border: 1px solid var(--stratum-warning);
  border-radius: 3px;
  background: rgba(245,158,11,0.08);
  color: var(--stratum-warning);
  font-size: 0.6875rem;
  cursor: pointer;
}
.item-error { font-size: 0.6875rem; color: var(--stratum-error); margin-top: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.load-more {
  width: 100%;
  padding: 0.5rem;
  border: none;
  background: none;
  color: var(--stratum-accent);
  font-size: 0.8125rem;
  cursor: pointer;
}
.load-more:hover { background: var(--stratum-bg-tertiary); }
</style>
