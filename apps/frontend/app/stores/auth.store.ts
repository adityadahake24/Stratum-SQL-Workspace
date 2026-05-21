import { defineStore } from "pinia"

interface User {
  id: string
  email: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(email: string, password: string) {
      const config = useRuntimeConfig()
      const response = await $fetch<{ access_token: string }>(`${config.public.apiBase}/api/v1/auth/login`, {
        method: "POST",
        body: { email, password },
        credentials: "include",
      })
      this.accessToken = response.access_token
      await this.fetchMe()
    },

    async register(email: string, password: string) {
      const config = useRuntimeConfig()
      await $fetch(`${config.public.apiBase}/api/v1/auth/register`, {
        method: "POST",
        body: { email, password },
      })
    },

    async refreshToken() {
      const config = useRuntimeConfig()
      try {
        const response = await $fetch<{ access_token: string }>(`${config.public.apiBase}/api/v1/auth/refresh`, {
          method: "POST",
          credentials: "include",
        })
        this.accessToken = response.access_token
        return true
      } catch {
        this.accessToken = null
        this.user = null
        return false
      }
    },

    async fetchMe() {
      if (!this.accessToken) return
      const config = useRuntimeConfig()
      try {
        const user = await $fetch<User>(`${config.public.apiBase}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.user = user
      } catch {
        this.accessToken = null
        this.user = null
      }
    },

    async logout() {
      const config = useRuntimeConfig()
      try {
        await $fetch(`${config.public.apiBase}/api/v1/auth/logout`, {
          method: "POST",
          credentials: "include",
          headers: this.accessToken ? { Authorization: `Bearer ${this.accessToken}` } : {},
        })
      } finally {
        this.accessToken = null
        this.user = null
        await navigateTo("/login")
      }
    },
  },

  persist: {
    paths: ["accessToken"],
  },
})
