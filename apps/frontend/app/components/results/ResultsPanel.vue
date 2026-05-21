<template>
  <div class="results-panel">
    <div class="results-meta" v-if="tab">
      <div class="meta-items">
        <span v-if="tab.executionStatus === 'running'" class="status-badge running">Running…</span>
        <span v-else-if="tab.executionStatus === 'complete'" class="status-badge success">
          ✓ {{ tab.rowCount ?? 0 }} rows
          <template v-if="tab.rowsAffected"> · {{ tab.rowsAffected }} affected</template>
          <template v-if="tab.executionTimeMs"> · {{ tab.executionTimeMs }}ms</template>
        </span>
        <span v-else-if="tab.executionStatus === 'error'" class="status-badge error">✗ Error</span>
        <span v-else-if="tab.executionStatus === 'cancelled'" class="status-badge cancelled">Cancelled</span>
        <span v-else class="status-badge empty">Ready</span>

        <button
          v-if="tab.hasUndo && tab.historyId"
          class="undo-btn"
          @click="history.previewUndo(tab.historyId!)"
        >
          ↩ Undo available
        </button>
      </div>

      <button v-if="tab.results?.length" class="export-btn" @click="exportCsv">
        ↓ Export CSV
      </button>
    </div>

    <div v-if="tab?.error" class="error-display">
      <strong>Error:</strong> {{ tab.error }}
    </div>

    <div class="results-table-wrap" v-if="tab?.columns && tab?.results">
      <div class="table-scroll" v-bind="containerProps" ref="containerRef">
        <table class="results-table">
          <thead>
            <tr>
              <th v-for="col in tab.columns" :key="col" @click="sortBy(col)">
                {{ col }}
                <span v-if="sortCol === col">{{ sortAsc ? "▲" : "▼" }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr style="height: 0">
              <td :colspan="tab.columns.length" style="padding: 0; border: none;">
                <div :style="{ height: `${offsetTop}px` }" />
              </td>
            </tr>
            <tr v-for="{ data: row, index: ri } in virtualRows" :key="ri">
              <td
                v-for="(cell, ci) in row"
                :key="ci"
                @click="copyCell(cell)"
                :title="cell === null ? 'NULL' : String(cell)"
              >
                <span v-if="cell === null" class="null-pill">NULL</span>
                <span v-else-if="typeof cell === 'object'" class="json-cell" @click.stop="openJsonModal(cell)">{ … }</span>
                <span v-else class="cell-value">{{ truncate(cell) }}</span>
              </td>
            </tr>
            <tr style="height: 0">
              <td :colspan="tab.columns.length" style="padding: 0; border: none;">
                <div :style="{ height: `${offsetBottom}px` }" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!tab?.results && !tab?.error && !tab?.executionStatus" class="results-empty">
      Run a query to see results here
    </div>
  </div>
</template>

<script setup lang="ts">
import { useVirtualList } from "@vueuse/core"
import { toast } from "vue-sonner"

const editor = useEditorStore()
const history = useHistoryStore()
const tab = computed(() => editor.activeTab)
const sortCol = ref<string | null>(null)
const sortAsc = ref(true)
const containerRef = ref<HTMLElement | null>(null)

const ROW_HEIGHT = 30

const sortedRows = computed(() => {
  if (!tab.value?.results) return []
  if (!sortCol.value || !tab.value.columns) return tab.value.results
  const idx = tab.value.columns.indexOf(sortCol.value)
  if (idx === -1) return tab.value.results
  return [...tab.value.results].sort((a: any[], b: any[]) => {
    const av = a[idx], bv = b[idx]
    if (av === null) return 1
    if (bv === null) return -1
    const cmp = av < bv ? -1 : av > bv ? 1 : 0
    return sortAsc.value ? cmp : -cmp
  })
})

const { list: virtualRows, containerProps, wrapperProps } = useVirtualList(sortedRows, {
  itemHeight: ROW_HEIGHT,
  overscan: 20,
})

const offsetTop = computed(() => (wrapperProps.value?.style as any)?.marginTop ?? 0)
const offsetBottom = computed(() => (wrapperProps.value?.style as any)?.marginBottom ?? 0)

function sortBy(col: string) {
  if (sortCol.value === col) sortAsc.value = !sortAsc.value
  else { sortCol.value = col; sortAsc.value = true }
}

function truncate(val: any, len = 200): string {
  const s = String(val)
  return s.length > len ? s.slice(0, len) + "…" : s
}

function copyCell(val: any) {
  if (val === null) return
  navigator.clipboard.writeText(String(val))
  toast.success("Copied to clipboard", { duration: 1500 })
}

function openJsonModal(val: any) {
  toast.message("JSON Value", { description: JSON.stringify(val, null, 2), duration: 10000 })
}

function exportCsv() {
  const t = tab.value
  if (!t?.columns || !t?.results) return
  const rows = [t.columns.join(","), ...t.results.map((r) => r.map((v: any) => `"${v === null ? "" : String(v).replace(/"/g, '""')}"`).join(","))]
  const blob = new Blob([rows.join("\n")], { type: "text/csv" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = "stratum-export.csv"
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.results-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--stratum-bg-primary);
}
.results-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  padding: 0 0.75rem;
  border-bottom: 1px solid var(--stratum-border);
  background: var(--stratum-bg-secondary);
  flex-shrink: 0;
}
.meta-items { display: flex; align-items: center; gap: 0.75rem; }
.status-badge { font-size: 0.8125rem; padding: 0.125rem 0.5rem; border-radius: 4px; font-weight: 500; }
.status-badge.running { color: var(--stratum-accent); animation: pulse 1.5s infinite; }
.status-badge.success { color: var(--stratum-success); }
.status-badge.error { color: var(--stratum-error); }
.status-badge.cancelled { color: var(--stratum-text-muted); }
.status-badge.empty { color: var(--stratum-text-muted); }
@keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.5 } }
.undo-btn {
  padding: 0.125rem 0.625rem;
  border: 1px solid var(--stratum-warning);
  border-radius: 4px;
  background: rgba(245,158,11,0.1);
  color: var(--stratum-warning);
  font-size: 0.75rem;
  cursor: pointer;
}
.export-btn {
  padding: 0.125rem 0.625rem;
  border: 1px solid var(--stratum-border);
  border-radius: 4px;
  background: transparent;
  color: var(--stratum-text-secondary);
  font-size: 0.75rem;
  cursor: pointer;
}
.export-btn:hover { background: var(--stratum-bg-tertiary); }
.error-display {
  padding: 0.75rem;
  color: var(--stratum-error);
  font-size: 0.875rem;
  background: rgba(239,68,68,0.05);
  border-bottom: 1px solid var(--stratum-border);
  flex-shrink: 0;
}
.results-table-wrap { flex: 1; overflow: hidden; min-height: 0; }
.table-scroll { width: 100%; height: 100%; overflow: auto; }
.results-table { width: max-content; min-width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.results-table th {
  position: sticky;
  top: 0;
  padding: 0.375rem 0.75rem;
  text-align: left;
  background: var(--stratum-bg-secondary);
  color: var(--stratum-text-secondary);
  font-weight: 600;
  border-bottom: 1px solid var(--stratum-border);
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  font-size: 0.75rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.results-table th:hover { color: var(--stratum-text-primary); }
.results-table td {
  padding: 0.3125rem 0.75rem;
  border-bottom: 1px solid var(--stratum-border);
  white-space: nowrap;
  cursor: pointer;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--stratum-text-primary);
}
.results-table td:hover { background: var(--stratum-bg-secondary); }
.null-pill { color: var(--stratum-text-muted); font-style: italic; font-size: 0.75rem; }
.json-cell { color: var(--stratum-accent); cursor: pointer; }
.cell-value { font-family: "JetBrains Mono", monospace; font-size: 0.8125rem; }
.results-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--stratum-text-muted);
  font-size: 0.875rem;
}
</style>
