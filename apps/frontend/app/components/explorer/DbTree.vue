<template>
  <div class="db-tree">
    <div class="tree-header">
      <span class="tree-title">Explorer</span>
      <input
        v-model="search"
        placeholder="Filter…"
        class="tree-search"
      />
    </div>

    <div class="tree-body">
      <div v-if="!connStore.activeConnectionId" class="tree-empty">
        No connection selected
      </div>

      <div v-else-if="schemasLoading" class="tree-loading">Loading schemas…</div>

      <div v-else v-for="schema in filteredSchemas" :key="schema.name">
        <div
          class="tree-node schema-node"
          @click="toggleSchema(schema.name)"
        >
          <span class="node-icon">{{ expandedSchemas.has(schema.name) ? "▼" : "▶" }}</span>
          <span class="node-label">{{ schema.name }}</span>
        </div>

        <template v-if="expandedSchemas.has(schema.name)">
          <div v-if="tablesLoading[schema.name]" class="tree-node leaf tree-loading">Loading tables…</div>
          <div
            v-else
            v-for="table in filteredTables(schema.name)"
            :key="table.name"
          >
            <div
              class="tree-node table-node"
              @click="toggleTable(schema.name, table.name)"
              @dblclick="insertSelectSnippet(table)"
              @contextmenu.prevent="openContextMenu($event, schema.name, table.name)"
            >
              <span class="node-icon">{{ expandedTables.has(`${schema.name}.${table.name}`) ? "▼" : "▶" }}</span>
              <span class="node-icon table-icon">⬜</span>
              <span class="node-label">{{ table.name }}</span>
              <span v-if="table.row_estimate" class="node-count">{{ formatCount(table.row_estimate) }}</span>
            </div>

            <template v-if="expandedTables.has(`${schema.name}.${table.name}`)">
              <div v-if="columnsLoading[`${schema.name}.${table.name}`]" class="tree-node leaf tree-loading">Loading…</div>
              <div
                v-else
                v-for="col in columns[`${schema.name}.${table.name}`] ?? []"
                :key="col.name"
                class="tree-node leaf column-node"
              >
                <span class="node-icon col-icon" :class="{ pk: col.is_primary_key }">
                  {{ col.is_primary_key ? "🔑" : "·" }}
                </span>
                <span class="node-label col-label">{{ col.name }}</span>
                <span class="node-type">{{ col.data_type }}</span>
              </div>
            </template>
          </div>
        </template>
      </div>
    </div>

    <!-- Context menu -->
    <div
      v-if="ctxMenu.visible"
      class="ctx-menu"
      :style="{ top: ctxMenu.y + 'px', left: ctxMenu.x + 'px' }"
      @mouseleave="ctxMenu.visible = false"
    >
      <button @click="selectTop100(ctxMenu.schema, ctxMenu.table)">SELECT TOP 100</button>
      <button @click="toggleTable(ctxMenu.schema, ctxMenu.table); ctxMenu.visible = false">Show columns</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const connStore = useConnectionStore()
const auth = useAuthStore()
const editor = useEditorStore()
const config = useRuntimeConfig()

const search = ref("")
const schemas = ref<any[]>([])
const schemasLoading = ref(false)
const expandedSchemas = ref(new Set<string>())
const tables = ref<Record<string, any[]>>({})
const tablesLoading = ref<Record<string, boolean>>({})
const expandedTables = ref(new Set<string>())
const columns = ref<Record<string, any[]>>({})
const columnsLoading = ref<Record<string, boolean>>({})
const ctxMenu = ref({ visible: false, x: 0, y: 0, schema: "", table: "" })

const filteredSchemas = computed(() =>
  schemas.value.filter((s) => !search.value || s.name.includes(search.value))
)

function filteredTables(schema: string) {
  return (tables.value[schema] ?? []).filter(
    (t) => !search.value || t.name.includes(search.value)
  )
}

async function loadSchemas() {
  if (!connStore.activeConnectionId) return
  schemasLoading.value = true
  try {
    const data: any[] = await $fetch(
      `${config.public.apiBase}/api/v1/schema/${connStore.activeConnectionId}/schemas`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    )
    schemas.value = data
  } catch {}
  schemasLoading.value = false
}

async function toggleSchema(name: string) {
  if (expandedSchemas.value.has(name)) {
    expandedSchemas.value.delete(name)
  } else {
    expandedSchemas.value.add(name)
    if (!tables.value[name]) await loadTables(name)
  }
}

async function loadTables(schema: string) {
  tablesLoading.value[schema] = true
  try {
    const data: any[] = await $fetch(
      `${config.public.apiBase}/api/v1/schema/${connStore.activeConnectionId}/schemas/${schema}/tables`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    )
    tables.value[schema] = data
  } catch {}
  tablesLoading.value[schema] = false
}

async function toggleTable(schema: string, table: string) {
  const key = `${schema}.${table}`
  if (expandedTables.value.has(key)) {
    expandedTables.value.delete(key)
  } else {
    expandedTables.value.add(key)
    if (!columns.value[key]) await loadColumns(schema, table)
  }
}

async function loadColumns(schema: string, table: string) {
  const key = `${schema}.${table}`
  columnsLoading.value[key] = true
  try {
    const data: any[] = await $fetch(
      `${config.public.apiBase}/api/v1/schema/${connStore.activeConnectionId}/schemas/${schema}/tables/${table}/columns`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    )
    columns.value[key] = data
  } catch {}
  columnsLoading.value[key] = false
}

function insertSelectSnippet(table: any) {
  const tab = editor.activeTab
  if (tab) {
    editor.setTabSql(tab.id, `SELECT * FROM ${table.schema}.${table.name} LIMIT 100;`)
  }
}

function selectTop100(schema: string, table: string) {
  const tab = editor.activeTab
  if (tab) editor.setTabSql(tab.id, `SELECT * FROM ${schema}.${table} LIMIT 100;`)
  ctxMenu.value.visible = false
}

function openContextMenu(e: MouseEvent, schema: string, table: string) {
  ctxMenu.value = { visible: true, x: e.clientX, y: e.clientY, schema, table }
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

watch(() => connStore.activeConnectionId, () => {
  schemas.value = []
  tables.value = {}
  columns.value = {}
  expandedSchemas.value.clear()
  expandedTables.value.clear()
  loadSchemas()
}, { immediate: true })
</script>

<style scoped>
.db-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--stratum-bg-secondary);
  border-right: 1px solid var(--stratum-border);
  overflow: hidden;
}
.tree-header {
  padding: 0.5rem;
  border-bottom: 1px solid var(--stratum-border);
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex-shrink: 0;
}
.tree-title { font-size: 0.75rem; font-weight: 600; color: var(--stratum-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
.tree-search { width: 100%; padding: 0.25rem 0.5rem; border: 1px solid var(--stratum-border); border-radius: 4px; background: var(--stratum-bg-primary); color: var(--stratum-text-primary); font-size: 0.8125rem; outline: none; }
.tree-body { flex: 1; overflow-y: auto; padding: 0.25rem 0; }
.tree-node {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
  font-size: 0.8125rem;
  color: var(--stratum-text-primary);
  user-select: none;
}
.tree-node:hover { background: var(--stratum-bg-tertiary); }
.schema-node { padding-left: 0.25rem; font-weight: 600; }
.table-node { padding-left: 1.25rem; }
.leaf { padding-left: 2.5rem; cursor: default; }
.column-node { padding-left: 3rem; }
.node-icon { font-size: 0.625rem; color: var(--stratum-text-muted); width: 14px; flex-shrink: 0; }
.table-icon { font-size: 0.5rem; }
.col-icon { font-size: 0.625rem; }
.col-icon.pk { color: var(--stratum-warning); }
.node-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-label { color: var(--stratum-text-secondary); }
.node-type { font-size: 0.6875rem; color: var(--stratum-text-muted); font-family: "JetBrains Mono", monospace; }
.node-count { font-size: 0.6875rem; color: var(--stratum-text-muted); }
.tree-empty, .tree-loading { padding: 1rem; font-size: 0.8125rem; color: var(--stratum-text-muted); text-align: center; }
.ctx-menu {
  position: fixed;
  z-index: 1000;
  background: var(--stratum-bg-elevated);
  border: 1px solid var(--stratum-border);
  border-radius: 6px;
  padding: 0.25rem 0;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.ctx-menu button {
  display: block;
  width: 100%;
  padding: 0.4rem 0.875rem;
  border: none;
  background: none;
  color: var(--stratum-text-primary);
  font-size: 0.8125rem;
  text-align: left;
  cursor: pointer;
}
.ctx-menu button:hover { background: var(--stratum-bg-secondary); }
</style>
