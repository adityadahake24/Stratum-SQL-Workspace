<template>
  <div class="tab-bar">
    <div class="tabs-scroll">
      <div
        v-for="tab in editor.tabs"
        :key="tab.id"
        class="tab"
        :class="{ active: tab.id === editor.activeTabId }"
        @click="editor.setActiveTab(tab.id)"
        @mousedown.middle.prevent="editor.closeTab(tab.id)"
      >
        <span class="tab-name" :title="tab.name">{{ tab.name }}</span>
        <span v-if="tab.isDirty" class="tab-dirty" title="Unsaved changes">●</span>
        <button
          class="tab-close"
          @click.stop="editor.closeTab(tab.id)"
          title="Close tab"
          v-if="editor.tabs.length > 1"
        >✕</button>
      </div>
    </div>

    <button
      class="tab-add"
      @click="editor.addTab()"
      title="New tab"
      :disabled="editor.tabs.length >= 10"
    >+</button>
  </div>
</template>

<script setup lang="ts">
const editor = useEditorStore()
</script>

<style scoped>
.tab-bar {
  display: flex;
  align-items: center;
  height: 36px;
  background: var(--stratum-bg-secondary);
  border-bottom: 1px solid var(--stratum-border);
  flex-shrink: 0;
  overflow: hidden;
}
.tabs-scroll {
  display: flex;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
}
.tabs-scroll::-webkit-scrollbar { display: none; }
.tab {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 0.75rem;
  height: 36px;
  min-width: 80px;
  max-width: 160px;
  font-size: 0.8125rem;
  cursor: pointer;
  border-right: 1px solid var(--stratum-border);
  color: var(--stratum-text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}
.tab:hover { background: var(--stratum-bg-tertiary); color: var(--stratum-text-primary); }
.tab.active { background: var(--stratum-bg-primary); color: var(--stratum-text-primary); border-bottom: 2px solid var(--stratum-accent); }
.tab-name { overflow: hidden; text-overflow: ellipsis; flex: 1; }
.tab-dirty { color: var(--stratum-warning); font-size: 0.625rem; }
.tab-close {
  border: none;
  background: transparent;
  color: var(--stratum-text-muted);
  cursor: pointer;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  padding: 0;
  flex-shrink: 0;
}
.tab-close:hover { background: var(--stratum-bg-tertiary); color: var(--stratum-error); }
.tab-add {
  padding: 0 0.75rem;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--stratum-text-secondary);
  cursor: pointer;
  font-size: 1rem;
  border-left: 1px solid var(--stratum-border);
  flex-shrink: 0;
}
.tab-add:hover { color: var(--stratum-text-primary); background: var(--stratum-bg-tertiary); }
.tab-add:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
