import type { Config } from "tailwindcss"

export default {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./app/**/*.{vue,ts,tsx}",
    "./components/**/*.{vue,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ["JetBrains Mono", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        stratum: {
          accent: "var(--stratum-accent)",
          "accent-hover": "var(--stratum-accent-hover)",
          success: "var(--stratum-success)",
          error: "var(--stratum-error)",
          warning: "var(--stratum-warning)",
          "bg-primary": "var(--stratum-bg-primary)",
          "bg-secondary": "var(--stratum-bg-secondary)",
          "bg-tertiary": "var(--stratum-bg-tertiary)",
          "bg-elevated": "var(--stratum-bg-elevated)",
          border: "var(--stratum-border)",
          "text-primary": "var(--stratum-text-primary)",
          "text-secondary": "var(--stratum-text-secondary)",
          "text-muted": "var(--stratum-text-muted)",
        },
      },
    },
  },
  plugins: [],
} satisfies Config
