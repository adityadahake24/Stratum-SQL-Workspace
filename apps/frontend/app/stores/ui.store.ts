import { defineStore } from "pinia"

type Theme = "light" | "dark" | "system"

export const useUiStore = defineStore("ui", {
  state: () => ({
    theme: "dark" as Theme,
    leftPanelSize: 20,
    rightPanelSize: 25,
    editorPanelSize: 45,
    rightPanelTab: "history" as "history" | "syntax",
    isSupportModalOpen: false,
    isConnectionModalOpen: false,
    editingConnectionId: null as string | null,
  }),

  actions: {
    setTheme(theme: Theme) {
      this.theme = theme
    },
    toggleTheme() {
      this.theme = this.theme === "dark" ? "light" : "dark"
    },
    setPanelSizes(left: number, right: number) {
      this.leftPanelSize = left
      this.rightPanelSize = right
    },
    openConnectionModal(connectionId?: string) {
      this.editingConnectionId = connectionId || null
      this.isConnectionModalOpen = true
    },
    closeConnectionModal() {
      this.isConnectionModalOpen = false
      this.editingConnectionId = null
    },
  },

  persist: {
    paths: ["theme", "leftPanelSize", "rightPanelSize", "editorPanelSize", "rightPanelTab"],
  },
})
