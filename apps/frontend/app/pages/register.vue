<template>
  <div class="auth-card">
    <div class="auth-logo">
      <span class="text-2xl font-bold" style="color: var(--stratum-accent)">Stratum</span>
      <p class="text-sm mt-1" style="color: var(--stratum-text-secondary)">Create your account</p>
    </div>

    <form @submit.prevent="handleRegister" class="mt-8 space-y-4">
      <div>
        <label class="auth-label">Email</label>
        <input v-model="email" type="email" required placeholder="you@company.com" class="auth-input" />
      </div>
      <div>
        <label class="auth-label">Password</label>
        <input v-model="password" type="password" required placeholder="Min 8 characters" class="auth-input" minlength="8" />
      </div>

      <div v-if="error" class="text-sm p-3 rounded-md" style="background: rgba(239,68,68,0.1); color: var(--stratum-error)">
        {{ error }}
      </div>

      <button type="submit" :disabled="loading" class="auth-btn">
        <span v-if="loading">Creating account…</span>
        <span v-else>Create account</span>
      </button>

      <p class="text-center text-sm" style="color: var(--stratum-text-secondary)">
        Already have an account?
        <NuxtLink to="/login" style="color: var(--stratum-accent)" class="hover:underline">Sign in</NuxtLink>
      </p>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "auth", middleware: "auth" })

const auth = useAuthStore()
const router = useRouter()
const email = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")

async function handleRegister() {
  loading.value = true
  error.value = ""
  try {
    await auth.register(email.value, password.value)
    await auth.login(email.value, password.value)
    await router.push("/workspace")
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || "Registration failed"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-card { width: 100%; max-width: 400px; background: var(--stratum-bg-elevated); border: 1px solid var(--stratum-border); border-radius: 12px; padding: 2rem; }
.auth-logo { text-align: center; }
.auth-label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.375rem; color: var(--stratum-text-secondary); }
.auth-input { width: 100%; padding: 0.625rem 0.875rem; border: 1px solid var(--stratum-border); border-radius: 8px; background: var(--stratum-bg-primary); color: var(--stratum-text-primary); font-size: 0.875rem; outline: none; transition: border-color 0.15s; }
.auth-input:focus { border-color: var(--stratum-accent); }
.auth-btn { width: 100%; padding: 0.625rem; border: none; border-radius: 8px; background: var(--stratum-accent); color: white; font-weight: 600; font-size: 0.875rem; cursor: pointer; }
.auth-btn:hover { background: var(--stratum-accent-hover); }
.auth-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
