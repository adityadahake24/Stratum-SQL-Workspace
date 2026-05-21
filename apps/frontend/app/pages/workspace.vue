<template>
  <div class="workspace-root">
    <AppNavbar />

    <div class="workspace-body">
      <Splitpanes @resized="onResized" :dblClickSplitter="false">
        <Pane :size="ui.leftPanelSize" :min-size="15" :max-size="35">
          <DbTree />
        </Pane>

        <Pane>
          <Splitpanes horizontal :dblClickSplitter="false">
            <Pane :size="ui.editorPanelSize" :min-size="25">
              <div class="editor-pane">
                <TabBar />
                <EditorToolbar />
                <SqlEditor />
              </div>
            </Pane>
            <Pane :min-size="30">
              <ResultsPanel />
            </Pane>
          </Splitpanes>
        </Pane>

        <Pane :size="ui.rightPanelSize" :min-size="20" :max-size="35">
          <RightPanel />
        </Pane>
      </Splitpanes>
    </div>

    <ConnectionModal v-if="ui.isConnectionModalOpen" />
    <UndoModal v-if="history.isUndoModalOpen" />
  </div>
</template>

<script setup lang="ts">
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"

definePageMeta({ middleware: "auth" })

const ui = useUiStore()
const auth = useAuthStore()
const connStore = useConnectionStore()
const history = useHistoryStore()
const editor = useEditorStore()

onMounted(async () => {
  editor.init()
  if (auth.isAuthenticated) {
    await connStore.loadConnections()
    await history.loadHistory(connStore.activeConnectionId ?? undefined)
  }
})

function onResized(e: any[]) {
  if (e.length >= 3) {
    ui.setPanelSizes(e[0].size, e[2].size)
  }
}
</script>

<style scoped>
.workspace-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--stratum-bg-primary);
}

.workspace-body {
  flex: 1;
  overflow: hidden;
}

.workspace-body :deep(.splitpanes) {
  height: 100%;
}

.editor-pane {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
</style>
