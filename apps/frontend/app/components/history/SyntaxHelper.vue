<template>
  <div class="syntax-helper">
    <div class="syntax-header">
      <input v-model="search" placeholder="Search snippets…" class="syntax-search" />
    </div>
    <div class="snippets">
      <div
        v-for="s in filtered"
        :key="s.title"
        class="snippet-item"
        @click="insert(s.sql)"
      >
        <div class="snippet-title">{{ s.title }}</div>
        <pre class="snippet-code">{{ s.sql }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const editor = useEditorStore()
const search = ref("")

const snippets = [
  { title: "SELECT", sql: "SELECT *\nFROM table_name\nWHERE condition\nLIMIT 100;" },
  { title: "INSERT", sql: "INSERT INTO table_name (col1, col2)\nVALUES ('val1', 'val2');" },
  { title: "UPDATE", sql: "UPDATE table_name\nSET col1 = 'value'\nWHERE id = 1;" },
  { title: "DELETE", sql: "DELETE FROM table_name\nWHERE id = 1;" },
  { title: "CTE", sql: "WITH cte AS (\n  SELECT * FROM table_name\n)\nSELECT * FROM cte;" },
  { title: "Window function", sql: "SELECT\n  name,\n  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank\nFROM employees;" },
  { title: "JOIN", sql: "SELECT a.*, b.name\nFROM table_a a\nJOIN table_b b ON a.id = b.a_id;" },
  { title: "EXPLAIN ANALYZE", sql: "EXPLAIN ANALYZE\nSELECT * FROM table_name WHERE id = 1;" },
  { title: "CREATE INDEX", sql: "CREATE INDEX idx_name ON table_name (column_name);" },
  { title: "Table size", sql: "SELECT\n  relname AS table,\n  pg_size_pretty(pg_total_relation_size(relid)) AS size\nFROM pg_catalog.pg_statio_user_tables\nORDER BY pg_total_relation_size(relid) DESC;" },
]

const filtered = computed(() =>
  snippets.filter((s) => !search.value || s.title.toLowerCase().includes(search.value.toLowerCase()) || s.sql.toLowerCase().includes(search.value.toLowerCase()))
)

function insert(sql: string) {
  const tab = editor.activeTab
  if (tab) editor.setTabSql(tab.id, tab.sql ? tab.sql + "\n\n" + sql : sql)
}
</script>

<style scoped>
.syntax-helper { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
.syntax-header { padding: 0.5rem; border-bottom: 1px solid var(--stratum-border); flex-shrink: 0; }
.syntax-search { width: 100%; padding: 0.25rem 0.5rem; border: 1px solid var(--stratum-border); border-radius: 4px; background: var(--stratum-bg-primary); color: var(--stratum-text-primary); font-size: 0.8125rem; outline: none; }
.snippets { flex: 1; overflow-y: auto; }
.snippet-item { padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--stratum-border); cursor: pointer; }
.snippet-item:hover { background: var(--stratum-bg-tertiary); }
.snippet-title { font-size: 0.75rem; font-weight: 600; color: var(--stratum-accent); margin-bottom: 0.25rem; }
.snippet-code { font-size: 0.6875rem; color: var(--stratum-text-secondary); font-family: "JetBrains Mono", monospace; white-space: pre-wrap; margin: 0; }
</style>
