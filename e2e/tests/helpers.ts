import { expect, type Page } from '@playwright/test';

export const TEST_TIMEOUT = 20_000;

export async function gotoAndExpectOk(page: Page, url: string) {
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded' });
    // SSR pages might redirect; still ensure we didn't 500.
    if (resp) expect(resp.status(), `HTTP ${resp.status()} for ${url}`).toBeLessThan(500);
}

export async function uiLogin(page: Page, usuario: string, password: string) {
    // In this app, the UI login page is served at /api/v1/auth/login.
    await gotoAndExpectOk(page, '/api/v1/auth/login');
    await page.locator('input[name="usuario"]').fill(usuario);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForLoadState('domcontentloaded');
}

export async function logout(page: Page) {
    await gotoAndExpectOk(page, '/api/v1/auth/logout');
}

export async function expectRedirectToLogin(page: Page) {
    // Depending on how the frontend handles missing token, it may:
    // - render a 401 error page at the same URL, or
    // - redirect to /login.
    const url = page.url();
    if (/\/api\/v1\/auth\/login/i.test(url)) {
        await expect(page.getByRole('heading', { name: /iniciar sesi/i })).toBeVisible();
        return;
    }

    await expect(page.locator('body')).toContainText(/401|token requerido|iniciar sesi/i);
}

export function uniqueSuffix() {
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
