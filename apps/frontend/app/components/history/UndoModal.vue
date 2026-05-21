<template>
  <div class="modal-backdrop" @click.self="history.closeUndoModal()">
    <div class="modal">
      <div class="modal-header">
        <h2>Undo Preview</h2>
        <button @click="history.closeUndoModal()" class="close-btn">✕</button>
      </div>

      <div class="modal-body" v-if="history.undoPreview">
        <div class="undo-info">
          <span class="op-badge" :class="history.undoPreview.operation_type.toLowerCase()">
            {{ history.undoPreview.operation_type }}
          </span>
          <span class="info-text">
            {{ history.undoPreview.row_count }} rows affected in
            <strong>{{ history.undoPreview.schema_name }}.{{ history.undoPreview.table_name }}</strong>
          </span>
          <span class="ttl-text">Expires in {{ formatTtl(history.undoPreview.ttl_seconds) }}</span>
        </div>

        <div class="sql-preview">
          <div class="sql-label">Inverse SQL that will be executed:</div>
          <pre class="sql-code">{{ history.undoPreview.inverse_sql }}</pre>
        </div>

        <div v-if="history.undoPreview.is_consumed" class="consumed-warning">
          This undo has already been executed.
        </div>

        <div v-if="error" class="undo-error">{{ error }}</div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" @click="history.closeUndoModal()">Cancel</button>
        <button
          class="btn-danger"
          :disabled="executing || history.undoPreview?.is_consumed"
          @click="execute"
        >
          {{ executing ? "Executing…" : "Execute Undo" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toast } from "vue-sonner"

const history = useHistoryStore()
const executing = ref(false)
const error = ref("")

async function execute() {
  if (!history.undoHistoryId) return
  executing.value = true
  error.value = ""
  try {
    await history.executeUndo(history.undoHistoryId)
    toast.success("Undo executed successfully")
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || "Undo failed"
  }
  executing.value = false
}

function formatTtl(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { width: 100%; max-width: 640px; background: var(--stratum-bg-elevated); border: 1px solid var(--stratum-border); border-radius: 12px; overflow: hidden; max-height: 80vh; display: flex; flex-direction: column; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid var(--stratum-border); flex-shrink: 0; }
.modal-header h2 { font-size: 1rem; font-weight: 600; margin: 0; }
.close-btn { border: none; background: none; color: var(--stratum-text-muted); cursor: pointer; }
.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; flex: 1; }
.undo-info { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.op-badge { padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
.op-badge.update { background: rgba(245,158,11,0.15); color: var(--stratum-warning); }
.op-badge.delete { background: rgba(239,68,68,0.15); color: var(--stratum-error); }
.op-badge.insert { background: rgba(16,185,129,0.15); color: var(--stratum-success); }
.info-text { font-size: 0.875rem; color: var(--stratum-text-primary); }
.ttl-text { font-size: 0.8125rem; color: var(--stratum-text-muted); margin-left: auto; }
.sql-preview { background: var(--stratum-bg-secondary); border: 1px solid var(--stratum-border); border-radius: 8px; overflow: hidden; }
.sql-label { padding: 0.5rem 0.75rem; font-size: 0.75rem; font-weight: 600; color: var(--stratum-text-secondary); border-bottom: 1px solid var(--stratum-border); text-transform: uppercase; letter-spacing: 0.04em; }
.sql-code { margin: 0; padding: 0.75rem; font-family: "JetBrains Mono", monospace; font-size: 0.8125rem; color: var(--stratum-text-primary); white-space: pre-wrap; overflow-x: auto; max-height: 200px; overflow-y: auto; }
.consumed-warning { padding: 0.5rem 0.75rem; background: rgba(239,68,68,0.1); color: var(--stratum-error); border-radius: 6px; font-size: 0.875rem; }
.undo-error { color: var(--stratum-error); font-size: 0.875rem; }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; padding: 1rem 1.25rem; border-top: 1px solid var(--stratum-border); flex-shrink: 0; }
.btn-secondary { padding: 0.5rem 1rem; border: 1px solid var(--stratum-border); border-radius: 8px; background: transparent; color: var(--stratum-text-secondary); cursor: pointer; font-size: 0.875rem; }
.btn-danger { padding: 0.5rem 1rem; border: none; border-radius: 8px; background: var(--stratum-error); color: white; cursor: pointer; font-size: 0.875rem; font-weight: 600; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
