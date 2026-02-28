import { test, expect } from '@playwright/test';
import { gotoAndExpectOk, uiLogin, logout, expectRedirectToLogin, uniqueSuffix } from './helpers';

/**
 * Auth tests:
 * - register owner (happy path)
 * - login success
 * - login failure
 * - logout
 *
 * Notes:
 * - These tests create a new user+restaurant each run to avoid relying on secrets.
 * - If your backend prevents duplicate users, this unique suffix ensures isolation.
 */

test('register owner -> can login -> logout redirects protected pages', async ({ page }) => {
    const suffix = uniqueSuffix();
    const usuario = `e2e_admin_${suffix}`;
    const password = 'E2E_Test_12345!';
    const email = `e2e_${suffix}@example.com`;
    const slug = `e2e-${suffix}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');

    await gotoAndExpectOk(page, '/registro');
    await expect(page.getByRole('heading', { name: /registro/i })).toBeVisible();

    await page.locator('input[name="nombre_completo"]').fill('E2E Admin');
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="usuario"]').fill(usuario);
    await page.locator('input[name="password"]').fill(password);
    await page.locator('input[name="restaurant_nombre"]').fill('Restaurante E2E');
    await page.locator('input[name="restaurant_slug"]').fill(slug);
    await page.getByRole('button', { name: /crear cuenta/i }).click();
    await page.waitForLoadState('domcontentloaded');

    // After registration it should either land on login or show success.
    // We'll just verify that login works.
    await uiLogin(page, usuario, password);

    // Don't couple to a single redirect target; just prove we can open a protected page.
    await gotoAndExpectOk(page, '/restaurants');
    await expect(page).toHaveURL(/\/restaurants\/?/i);

    await logout(page);

    await gotoAndExpectOk(page, '/categories');
    await expectRedirectToLogin(page);
});

test('login failure shows error', async ({ page }) => {
    await gotoAndExpectOk(page, '/api/v1/auth/login');
    await page.locator('input[name="usuario"]').fill('this-user-should-not-exist');
    await page.locator('input[name="password"]').fill('wrong-password');
    await page.getByRole('button', { name: /entrar/i }).click();

    await expect(page.locator('.alert.alert-danger')).toBeVisible();
});
