export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,

  modules: [
    "@nuxtjs/tailwindcss",
    "shadcn-nuxt",
    "@pinia/nuxt",
    "@pinia-plugin-persistedstate/nuxt",
    "@vueuse/nuxt",
  ],

  shadcn: {
    prefix: "",
    componentDir: "./app/components/ui",
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || "ws://localhost:8000",
    },
  },

  app: {
    head: {
      title: "Stratum — PostgreSQL Workspace",
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "The professional PostgreSQL workspace for teams who take data seriously." },
      ],
      link: [
        {
          rel: "stylesheet",
          href: "https://fonts.bunny.net/css?family=jetbrains-mono:400,500,600,700&display=swap",
        },
      ],
    },
  },

  css: ["~/assets/css/main.css"],

  typescript: {
    shim: false,
    tsConfig: {
      compilerOptions: {
        types: ["node"],
      },
    },
  },

  vite: {
    optimizeDeps: {
      include: ["monaco-editor"],
    },
  },
})
