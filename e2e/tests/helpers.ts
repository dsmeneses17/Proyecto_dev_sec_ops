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

    // CI sometimes takes longer to process auth (DB warmup, slow container start).
    // Wait until either we leave the login URL OR an error alert appears.
    await expect
        .poll(
            async () => {
                const onLogin = /\/api\/v1\/auth\/login/i.test(page.url());
                if (!onLogin) return 'ok';
                const hasError = await page.locator('.alert.alert-danger').isVisible();
                return hasError ? 'error' : 'pending';
            },
            { timeout: 30_000 },
        )
        .not.toBe('pending');

    // CI-safe proof-of-login:
    // Don't rely on cookies (could be httpOnly, path-scoped, or otherwise not visible).
    // Also don't rely on where the app redirects after login (it may be '/', '/restaurants', etc).
    // Instead: if we didn't stay on the login page, probe a protected page.
    if (/\/api\/v1\/auth\/login/i.test(page.url())) {
        await expect(page.locator('.alert.alert-danger')).toBeVisible({ timeout: 5_000 });
        throw new Error('Login did not succeed (still on /api/v1/auth/login)');
    }

    // Now validate we can reach a protected page.
    await gotoAndExpectOk(page, '/restaurants');

    // After probing, we expect either:
    // - to be on /restaurants (authenticated), or
    // - redirected back to login (not authenticated).
    await expect(page).not.toHaveURL(/\/api\/v1\/auth\/login/i);
    await expect(page).toHaveURL(/\/restaurants\/?/i);
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
