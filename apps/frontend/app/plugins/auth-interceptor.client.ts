export default defineNuxtPlugin(() => {
  const auth = useAuthStore()

  addRouteMiddleware("auth-refresh", async (to) => {
    if (!auth.accessToken) return
    const publicRoutes = ["/login", "/register"]
    if (publicRoutes.includes(to.path)) return

    // Eagerly refresh if token looks expired (decode exp claim without a library)
    try {
      const [, payload] = auth.accessToken.split(".")
      const decoded = JSON.parse(atob(payload))
      const expiresAt = decoded.exp * 1000
      if (Date.now() >= expiresAt - 60_000) {
        const ok = await auth.refreshToken()
        if (!ok) return navigateTo("/login")
      }
    } catch {}
  })
})
