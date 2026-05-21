<template>
  <header class="navbar">
    <div class="navbar-left">
      <span class="navbar-logo">Stratum</span>

      <div class="conn-selector">
        <select
          v-if="connStore.connections.length > 0"
          :value="connStore.activeConnectionId"
          @change="connStore.selectConnection(($event.target as HTMLSelectElement).value)"
          class="conn-select"
        >
          <option v-for="c in connStore.connections" :key="c.id" :value="c.id">
            {{ c.name }} ({{ c.host }}:{{ c.port }}/{{ c.database }})
          </option>
        </select>
        <button v-else class="btn-ghost text-sm" @click="ui.openConnectionModal()">
          + Add connection
        </button>
        <button class="btn-icon ml-1" title="Add connection" @click="ui.openConnectionModal()">
          <PlusIcon :size="14" />
        </button>
      </div>
    </div>

    <div class="navbar-right">
      <button class="btn-icon" title="Toggle theme" @click="ui.toggleTheme()">
        <SunIcon v-if="ui.theme === 'dark'" :size="16" />
        <MoonIcon v-else :size="16" />
      </button>

      <button class="btn-ghost text-sm" @click="ui.isSupportModalOpen = true">
        Support
      </button>

      <div class="user-menu">
        <span class="user-email">{{ auth.user?.email }}</span>
        <button class="btn-ghost text-sm" @click="auth.logout()">Sign out</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { PlusIcon, SunIcon, MoonIcon } from "lucide-vue-next"

const ui = useUiStore()
const auth = useAuthStore()
const connStore = useConnectionStore()
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 1rem;
  border-bottom: 1px solid var(--stratum-border);
  background: var(--stratum-bg-elevated);
  flex-shrink: 0;
}
.navbar-left { display: flex; align-items: center; gap: 1rem; }
.navbar-right { display: flex; align-items: center; gap: 0.75rem; }
.navbar-logo { font-size: 1rem; font-weight: 700; color: var(--stratum-accent); letter-spacing: -0.01em; }
.conn-selector { display: flex; align-items: center; gap: 0.25rem; }
.conn-select {
  background: var(--stratum-bg-secondary);
  border: 1px solid var(--stratum-border);
  color: var(--stratum-text-primary);
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 0.8125rem;
  cursor: pointer;
  max-width: 280px;
}
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--stratum-text-secondary);
  cursor: pointer;
}
.btn-icon:hover { background: var(--stratum-bg-secondary); color: var(--stratum-text-primary); }
.btn-ghost {
  border: none;
  background: transparent;
  color: var(--stratum-text-secondary);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}
.btn-ghost:hover { background: var(--stratum-bg-secondary); color: var(--stratum-text-primary); }
.user-menu { display: flex; align-items: center; gap: 0.5rem; }
.user-email { font-size: 0.8125rem; color: var(--stratum-text-secondary); }
</style>
