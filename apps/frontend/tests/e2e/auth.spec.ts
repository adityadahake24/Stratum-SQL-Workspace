import { test, expect } from "@playwright/test"

test.describe("Authentication", () => {
  test("login page loads", async ({ page }) => {
    await page.goto("/login")
    await expect(page.locator("input[type='email']")).toBeVisible()
    await expect(page.locator("input[type='password']")).toBeVisible()
  })

  test("register page loads", async ({ page }) => {
    await page.goto("/register")
    await expect(page.locator("input[type='email']")).toBeVisible()
    await expect(page.locator("input[type='password']")).toBeVisible()
  })

  test("unauthenticated redirect to login", async ({ page }) => {
    await page.goto("/workspace")
    await expect(page).toHaveURL(/\/login/)
  })

  test("register and login flow", async ({ page }) => {
    const email = `e2e-${Date.now()}@stratum.io`

    await page.goto("/register")
    await page.fill("input[type='email']", email)
    await page.fill("input[type='password']", "StrongPass1!")
    await page.click("button[type='submit']")
    await expect(page).toHaveURL(/\/workspace/, { timeout: 10000 })
  })
})
