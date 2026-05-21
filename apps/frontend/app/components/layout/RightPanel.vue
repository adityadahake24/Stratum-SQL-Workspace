<template>
  <div class="right-panel">
    <div class="panel-tabs">
      <button
        class="panel-tab"
        :class="{ active: ui.rightPanelTab === 'history' }"
        @click="ui.rightPanelTab = 'history'"
      >History</button>
      <button
        class="panel-tab"
        :class="{ active: ui.rightPanelTab === 'syntax' }"
        @click="ui.rightPanelTab = 'syntax'"
      >Syntax</button>
    </div>

    <div class="panel-body">
      <HistoryList v-if="ui.rightPanelTab === 'history'" />
      <SyntaxHelper v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
const ui = useUiStore()
</script>

<style scoped>
.right-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--stratum-bg-secondary);
  border-left: 1px solid var(--stratum-border);
  overflow: hidden;
}
.panel-tabs {
  display: flex;
  border-bottom: 1px solid var(--stratum-border);
  flex-shrink: 0;
}
.panel-tab {
  flex: 1;
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--stratum-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
}
.panel-tab.active {
  color: var(--stratum-accent);
  border-bottom: 2px solid var(--stratum-accent);
  font-weight: 600;
}
.panel-body { flex: 1; overflow: hidden; }
</style>
