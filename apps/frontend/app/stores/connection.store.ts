import { defineStore } from "pinia"
import { useAuthStore } from "./auth.store"

export interface DbConnection {
  id: string
  name: string
  host: string
  port: number
  database: string
  ssl_mode: string
  is_active: boolean
  last_used_at: string | null
  created_at: string
}

export const useConnectionStore = defineStore("connection", {
  state: () => ({
    connections: [] as DbConnection[],
    activeConnectionId: null as string | null,
    isLoading: false,
  }),

  getters: {
    activeConnection: (state) => state.connections.find((c) => c.id === state.activeConnectionId) ?? null,
  },

  actions: {
    async loadConnections() {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      this.isLoading = true
      try {
        const data = await $fetch<DbConnection[]>(`${config.public.apiBase}/api/v1/connections`, {
          headers: { Authorization: `Bearer ${auth.accessToken}` },
        })
        this.connections = data
        if (data.length > 0 && !this.activeConnectionId) {
          this.activeConnectionId = data[0].id
        }
      } finally {
        this.isLoading = false
      }
    },

    selectConnection(id: string) {
      this.activeConnectionId = id
    },

    async createConnection(payload: object) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      const conn = await $fetch<DbConnection>(`${config.public.apiBase}/api/v1/connections`, {
        method: "POST",
        body: payload,
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      this.connections.unshift(conn)
      this.activeConnectionId = conn.id
      return conn
    },

    async updateConnection(id: string, payload: object) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      const conn = await $fetch<DbConnection>(`${config.public.apiBase}/api/v1/connections/${id}`, {
        method: "PUT",
        body: payload,
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      const idx = this.connections.findIndex((c) => c.id === id)
      if (idx !== -1) this.connections[idx] = conn
      return conn
    },

    async deleteConnection(id: string) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      await $fetch(`${config.public.apiBase}/api/v1/connections/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      this.connections = this.connections.filter((c) => c.id !== id)
      if (this.activeConnectionId === id) {
        this.activeConnectionId = this.connections[0]?.id ?? null
      }
    },

    async testConnection(id: string) {
      const auth = useAuthStore()
      const config = useRuntimeConfig()
      return $fetch(`${config.public.apiBase}/api/v1/connections/${id}/test`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
    },
  },

  persist: {
    paths: ["activeConnectionId"],
  },
})
