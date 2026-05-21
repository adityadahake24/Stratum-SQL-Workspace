import { defineStore } from "pinia"
import { useAuthStore } from "./auth.store"

export interface HistoryItem {
  id: string
  connection_id: string | null
  sql_text: string
  query_type: string
  execution_status: string
  execution_time_ms: number | null
  rows_affected: number | null
  row_count: number | null
  error_message: string | null
  has_undo: boolean
  undo_snapshot_id: string | null
  undo_executed_at: string | null
  created_at: string
}

export const useHistoryStore = defineStore("history", {
  state: () => ({
    items: [] as HistoryItem[],
    page: 1,
    total: 0,
    isLoading: false,
    undoPreview: null as any,
    isUndoModalOpen: false,
    undoHistoryId: null as string | null,
  }),

  actions: {
    async loadHistory(connectionId?: string) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      this.isLoading = true
      this.page = 1
      try {
        const params = new URLSearchParams({ page: "1", page_size: "50" })
        if (connectionId) params.set("connection_id", connectionId)
        const data: any = await $fetch(`${config.public.apiBase}/api/v1/history?${params}`, {
          headers: { Authorization: `Bearer ${auth.accessToken}` },
        })
        this.items = data.items
        this.total = data.total
      } finally {
        this.isLoading = false
      }
    },

    async loadMore() {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      this.page++
      const params = new URLSearchParams({ page: String(this.page), page_size: "50" })
      const data: any = await $fetch(`${config.public.apiBase}/api/v1/history?${params}`, {
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      this.items.push(...data.items)
    },

    async previewUndo(historyId: string) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      const preview = await $fetch(`${config.public.apiBase}/api/v1/undo/${historyId}/preview`, {
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      this.undoPreview = preview
      this.undoHistoryId = historyId
      this.isUndoModalOpen = true
    },

    async executeUndo(historyId: string) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      const result: any = await $fetch(`${config.public.apiBase}/api/v1/undo/${historyId}/execute`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      this.isUndoModalOpen = false
      this.undoPreview = null
      await this.loadHistory()
      return result
    },

    closeUndoModal() {
      this.isUndoModalOpen = false
      this.undoPreview = null
      this.undoHistoryId = null
    },

    prependItem(item: HistoryItem) {
      this.items.unshift(item)
    },
  },
})
