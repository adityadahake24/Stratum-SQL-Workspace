import { VueQueryPlugin, QueryClient, type VueQueryPluginOptions } from "@tanstack/vue-query"

export default defineNuxtPlugin((nuxtApp) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  })

  const options: VueQueryPluginOptions = { queryClient }
  nuxtApp.vueApp.use(VueQueryPlugin, options)
})
