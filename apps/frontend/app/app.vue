<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <Toaster rich-colors position="top-right" />
</template>

<script setup lang="ts">
import { Toaster } from "vue-sonner"
import { useUiStore } from "~/stores/ui.store"

const ui = useUiStore()

useHead({
  htmlAttrs: {
    "data-theme": ui.theme === "system" ? undefined : ui.theme,
  },
})

watchEffect(() => {
  if (ui.theme === "system") {
    document.documentElement.removeAttribute("data-theme")
  } else {
    document.documentElement.setAttribute("data-theme", ui.theme)
  }
})
</script>
