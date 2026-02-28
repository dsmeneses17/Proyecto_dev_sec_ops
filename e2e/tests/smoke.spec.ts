import { test, expect } from '@playwright/test';
import { gotoAndExpectOk, expectRedirectToLogin } from './helpers';

test('home loads and has navbar brand', async ({ page }) => {
    await gotoAndExpectOk(page, '/');
    await expect(page.getByRole('link', { name: /restaurante/i })).toBeVisible();
});

test('security: protected pages redirect to login when logged out', async ({ page }) => {
    await gotoAndExpectOk(page, '/categories');
    await expectRedirectToLogin(page);

    await gotoAndExpectOk(page, '/platos');
    await expectRedirectToLogin(page);
});

test('public menu index loads and can open menu (or shows not found gracefully)', async ({ page }) => {
    await gotoAndExpectOk(page, '/menu');
    await expect(page.getByRole('heading', { name: /menú público/i })).toBeVisible();

    // If there are restaurants available in the select, pick the first real option.
    const select = page.locator('select[name="slug"]');
    if (await select.count()) {
        const options = select.locator('option');
        const optionCount = await options.count();
        if (optionCount > 1) {
            await select.selectOption({ index: 1 });
            await page.getByRole('button', { name: /^ver$/i }).click();
            await page.waitForLoadState('domcontentloaded');
            await expect(page).toHaveURL(/\/menu\//);
            // Assert on something that will actually be present when a menu renders.
            // With our seeded DB, we expect at least the restaurant name or a category name.
            await expect(page.locator('body')).toContainText(/proyecto materia|sopas|ajiaco|preuba 12345/i);
            return;
        }
    }

    // Fallback flow: use a known example slug.
    await page.getByPlaceholder(/proyecto-materia/i).fill('proyecto-materia');
    await page.getByRole('button', { name: /^ver$/i }).click();
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveURL(/\/menu\//);
    await expect(page.locator('body')).toContainText(/proyecto materia|sopas|ajiaco|preuba 12345/i);
});

test('visual/layout sanity: login form has aligned controls', async ({ page }) => {
    await gotoAndExpectOk(page, '/api/v1/auth/login');

    // Basic layout checks: inputs should be visible and reasonably sized.
    const user = page.locator('input[name="usuario"]');
    const pass = page.locator('input[name="password"]');
    await expect(user).toBeVisible();
    await expect(pass).toBeVisible();

    const userBox = await user.boundingBox();
    const passBox = await pass.boundingBox();
    expect(userBox?.width).toBeGreaterThan(200);
    expect(passBox?.width).toBeGreaterThan(200);
});
