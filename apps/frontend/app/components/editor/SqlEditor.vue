<template>
  <div ref="editorContainer" class="monaco-container" />
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor"

const editorContainer = ref<HTMLElement | null>(null)
const editor = useEditorStore()
const ui = useUiStore()

let monacoEditor: monaco.editor.IStandaloneCodeEditor | null = null

const STRATUM_DARK: monaco.editor.IStandaloneThemeData = {
  base: "vs-dark",
  inherit: true,
  rules: [
    { token: "keyword", foreground: "818cf8" },
    { token: "string", foreground: "a8cc7c" },
    { token: "number", foreground: "f0a05a" },
    { token: "comment", foreground: "656d76", fontStyle: "italic" },
    { token: "identifier", foreground: "e6edf3" },
  ],
  colors: {
    "editor.background": "#0f1117",
    "editor.foreground": "#e6edf3",
    "editor.lineHighlightBackground": "#161b22",
    "editorLineNumber.foreground": "#656d76",
    "editorCursor.foreground": "#818cf8",
    "editor.selectionBackground": "#264f78",
  },
}

const STRATUM_LIGHT: monaco.editor.IStandaloneThemeData = {
  base: "vs",
  inherit: true,
  rules: [
    { token: "keyword", foreground: "5B6CF2" },
    { token: "string", foreground: "2e7d32" },
    { token: "number", foreground: "c62828" },
    { token: "comment", foreground: "9ca3af", fontStyle: "italic" },
  ],
  colors: {
    "editor.background": "#ffffff",
    "editor.foreground": "#1a1c1e",
    "editor.lineHighlightBackground": "#f8f9fa",
    "editorCursor.foreground": "#5B6CF2",
    "editor.selectionBackground": "#c5cae9",
  },
}

onMounted(() => {
  monaco.editor.defineTheme("stratum-dark", STRATUM_DARK)
  monaco.editor.defineTheme("stratum-light", STRATUM_LIGHT)

  monacoEditor = monaco.editor.create(editorContainer.value!, {
    value: editor.activeTab?.sql ?? "",
    language: "pgsql",
    theme: ui.theme === "dark" ? "stratum-dark" : "stratum-light",
    fontFamily: "JetBrains Mono, monospace",
    fontSize: 14,
    tabSize: 2,
    minimap: { enabled: false },
    wordWrap: "off",
    bracketPairColorization: { enabled: true },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    padding: { top: 8 },
    lineNumbers: "on",
    renderLineHighlight: "line",
    suggest: { showWords: false },
  })

  monacoEditor.onDidChangeModelContent(() => {
    const tab = editor.activeTab
    if (tab) editor.setTabSql(tab.id, monacoEditor!.getValue())
  })
})

onUnmounted(() => {
  monacoEditor?.dispose()
})

watch(() => editor.activeTabId, () => {
  const tab = editor.activeTab
  if (monacoEditor && tab) {
    const current = monacoEditor.getValue()
    if (current !== tab.sql) monacoEditor.setValue(tab.sql)
  }
})

watch(() => ui.theme, (theme) => {
  monaco.editor.setTheme(theme === "dark" ? "stratum-dark" : "stratum-light")
})
</script>

<style scoped>
.monaco-container {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}
</style>
