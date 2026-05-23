<template>
  <div class="modal-backdrop" @click.self="ui.closeConnectionModal()">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ isEditing ? "Edit Connection" : "New Connection" }}</h2>
        <button @click="ui.closeConnectionModal()" class="close-btn">✕</button>
      </div>

      <form @submit.prevent="save" class="modal-body">
        <div class="field">
          <label>Connection Name</label>
          <input v-model="form.name" required placeholder="e.g. Production DB" class="input" />
        </div>

        <div class="fields-row">
          <div class="field flex-3">
            <label>Host</label>
            <input v-model="form.host" required placeholder="localhost" class="input" />
          </div>
          <div class="field flex-1">
            <label>Port</label>
            <input v-model.number="form.port" required type="number" placeholder="5432" class="input" />
          </div>
        </div>

        <div class="field">
          <label>Database</label>
          <input v-model="form.database" required placeholder="mydb" class="input" />
        </div>

        <div class="fields-row">
          <div class="field flex-1">
            <label>Username</label>
            <input v-model="form.username" required placeholder="postgres" class="input" />
          </div>
          <div class="field flex-1">
            <label>Password</label>
            <input v-model="form.password" type="password" :placeholder="isEditing ? '(unchanged)' : 'password'" class="input" />
          </div>
        </div>

        <div class="field">
          <label>SSL Mode</label>
          <select v-model="form.ssl_mode" class="input">
            <option value="disable">Disable</option>
            <option value="require">Require</option>
            <option value="verify-ca">Verify CA</option>
            <option value="verify-full">Verify Full</option>
          </select>
        </div>

        <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
          {{ testResult.success ? `✓ Connected — ${testResult.pg_version?.split(' ').slice(0,2).join(' ')}` : `✗ ${testResult.message}` }}
          <span v-if="testResult.latency_ms"> · {{ testResult.latency_ms }}ms</span>
        </div>

        <div v-if="error" class="test-result error">{{ error }}</div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="testConnection" :disabled="testing">
            {{ testing ? "Testing…" : "Test Connection" }}
          </button>
          <button type="submit" class="btn-primary" :disabled="saving">
            {{ saving ? "Saving…" : "Save" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toast } from "vue-sonner"
import type { DbConnection } from "~/stores/connection.store"

const ui = useUiStore()
const connStore = useConnectionStore()
const auth = useAuthStore()
const config = useRuntimeConfig()

const DRAFT_KEY = "stratum:conn-draft"

const isEditing = computed(() => !!ui.editingConnectionId)
const form = reactive({
  name: "",
  host: "localhost",
  port: 5432,
  database: "",
  username: "postgres",
  password: "",
  ssl_mode: "disable",
})

const testResult = ref<any>(null)
const testing = ref(false)
const saving = ref(false)
const error = ref("")

onMounted(() => {
  if (ui.editingConnectionId) {
    const conn = connStore.connections.find((c) => c.id === ui.editingConnectionId)
    if (conn) {
      form.name = conn.name
      form.host = conn.host
      form.port = conn.port
      form.database = conn.database
      form.ssl_mode = conn.ssl_mode
    }
  } else {
    const saved = localStorage.getItem(DRAFT_KEY)
    if (saved) {
      try {
        const draft = JSON.parse(saved)
        Object.assign(form, draft)
      } catch {}
    }
  }
})

watch(form, () => {
  if (!isEditing.value) {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ ...form, password: "" }))
  }
}, { deep: true })

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    const payload = { ...form }
    if (!payload.password && isEditing.value) {
      toast.error("Enter password to test")
      testing.value = false
      return
    }
    const result: any = await $fetch(`${config.public.apiBase}/api/v1/connections/test-temp`, {
      method: "POST",
      headers: { Authorization: `Bearer ${auth.accessToken}` },
      body: payload,
    })
    testResult.value = result
  } catch (e: any) {
    testResult.value = { success: false, message: e?.data?.message || e?.message || "Connection failed" }
  }
  testing.value = false
}

async function save() {
  saving.value = true
  error.value = ""
  try {
    if (isEditing.value) {
      await connStore.updateConnection(ui.editingConnectionId!, form)
      toast.success("Connection updated")
    } else {
      await connStore.createConnection(form)
      localStorage.removeItem(DRAFT_KEY)
      toast.success("Connection saved")
    }
    ui.closeConnectionModal()
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || "Save failed"
  }
  saving.value = false
}
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { width: 100%; max-width: 520px; background: var(--stratum-bg-elevated); border: 1px solid var(--stratum-border); border-radius: 12px; overflow: hidden; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid var(--stratum-border); }
.modal-header h2 { font-size: 1rem; font-weight: 600; color: var(--stratum-text-primary); margin: 0; }
.close-btn { border: none; background: none; color: var(--stratum-text-muted); cursor: pointer; font-size: 1rem; }
.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 0.875rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field label { font-size: 0.8125rem; font-weight: 500; color: var(--stratum-text-secondary); }
.fields-row { display: flex; gap: 0.75rem; }
.flex-1 { flex: 1; }
.flex-3 { flex: 3; }
.input { padding: 0.5rem 0.75rem; border: 1px solid var(--stratum-border); border-radius: 8px; background: var(--stratum-bg-primary); color: var(--stratum-text-primary); font-size: 0.875rem; outline: none; width: 100%; }
.input:focus { border-color: var(--stratum-accent); }
.test-result { padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.8125rem; }
.test-result.success { background: rgba(16,185,129,0.1); color: var(--stratum-success); }
.test-result.error { background: rgba(239,68,68,0.1); color: var(--stratum-error); }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 0.25rem; }
.btn-primary { padding: 0.5rem 1.25rem; border: none; border-radius: 8px; background: var(--stratum-accent); color: white; font-size: 0.875rem; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { padding: 0.5rem 1.25rem; border: 1px solid var(--stratum-border); border-radius: 8px; background: transparent; color: var(--stratum-text-secondary); font-size: 0.875rem; cursor: pointer; }
.btn-secondary:disabled { opacity: 0.5; }
</style>
