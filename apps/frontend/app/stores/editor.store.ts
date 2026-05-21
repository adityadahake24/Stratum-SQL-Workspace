import { defineStore } from "pinia"

export interface Tab {
  id: string
  name: string
  sql: string
  connectionId: string | null
  executionId: string | null
  isDirty: boolean
  results: any[] | null
  columns: string[] | null
  executionStatus: string | null
  executionTimeMs: number | null
  rowCount: number | null
  rowsAffected: number | null
  hasUndo: boolean
  historyId: string | null
  error: string | null
}

function newTab(index: number): Tab {
  return {
    id: crypto.randomUUID(),
    name: `Query ${index}`,
    sql: "",
    connectionId: null,
    executionId: null,
    isDirty: false,
    results: null,
    columns: null,
    executionStatus: null,
    executionTimeMs: null,
    rowCount: null,
    rowsAffected: null,
    hasUndo: false,
    historyId: null,
    error: null,
  }
}

export const useEditorStore = defineStore("editor", {
  state: () => ({
    tabs: [newTab(1)] as Tab[],
    activeTabId: null as string | null,
  }),

  getters: {
    activeTab: (state) => state.tabs.find((t) => t.id === state.activeTabId) ?? state.tabs[0] ?? null,
    tabCount: (state) => state.tabs.length,
  },

  actions: {
    init() {
      if (this.tabs.length === 0) {
        this.tabs = [newTab(1)]
      }
      if (!this.activeTabId || !this.tabs.find((t) => t.id === this.activeTabId)) {
        this.activeTabId = this.tabs[0]?.id ?? null
      }
    },

    addTab() {
      if (this.tabs.length >= 10) return
      const tab = newTab(this.tabs.length + 1)
      this.tabs.push(tab)
      this.activeTabId = tab.id
    },

    closeTab(id: string) {
      const idx = this.tabs.findIndex((t) => t.id === id)
      if (idx === -1 || this.tabs.length <= 1) return
      this.tabs.splice(idx, 1)
      if (this.activeTabId === id) {
        this.activeTabId = this.tabs[Math.max(0, idx - 1)].id
      }
    },

    setActiveTab(id: string) {
      this.activeTabId = id
    },

    setTabSql(id: string, sql: string) {
      const tab = this.tabs.find((t) => t.id === id)
      if (tab) {
        tab.sql = sql
        tab.isDirty = true
      }
    },

    setTabResults(id: string, data: Partial<Tab>) {
      const tab = this.tabs.find((t) => t.id === id)
      if (tab) Object.assign(tab, data)
    },

    appendTabRows(id: string, rows: any[]) {
      const tab = this.tabs.find((t) => t.id === id)
      if (tab) {
        if (!tab.results) tab.results = []
        tab.results.push(...rows)
      }
    },

    duplicateTab(id: string) {
      const tab = this.tabs.find((t) => t.id === id)
      if (!tab) return
      const newT: Tab = { ...tab, id: crypto.randomUUID(), name: `${tab.name} (copy)`, executionId: null }
      this.tabs.push(newT)
      this.activeTabId = newT.id
    },

    renameTab(id: string, name: string) {
      const tab = this.tabs.find((t) => t.id === id)
      if (tab) tab.name = name
    },

    setTabConnection(id: string, connectionId: string) {
      const tab = this.tabs.find((t) => t.id === id)
      if (tab) tab.connectionId = connectionId
    },
  },

  persist: {
    paths: ["tabs", "activeTabId"],
  },
})
