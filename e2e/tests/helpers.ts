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

    // Click and wait for navigation (some environments redirect to /restaurants,
    // others may land on another protected page; in CI we've seen it stay on the
    // login URL but still set the cookie slightly later).
    await Promise.all([
        page.waitForLoadState('domcontentloaded'),
        page.getByRole('button', { name: /entrar/i }).click(),
    ]);

    // Robust proof-of-login: the session cookie should exist after successful login.
    // (Cookie name inferred from common patterns; we also accept any cookie containing
    // 'token' to avoid coupling to implementation.)
    await expect
        .poll(
            async () => {
                const cookies = await page.context().cookies();
                const hasSession = cookies.some(
                    (c) =>
                        c.name.toLowerCase().includes('access') ||
                        c.name.toLowerCase().includes('session') ||
                        c.name.toLowerCase().includes('token'),
                );
                return hasSession;
            },
            { timeout: 10_000 },
        )
        .toBeTruthy();
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
