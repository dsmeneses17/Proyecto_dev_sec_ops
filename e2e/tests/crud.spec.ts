import { test, expect } from '@playwright/test';
import { gotoAndExpectOk, uiLogin, uniqueSuffix } from './helpers';

/**
 * Admin CRUD flows:
 * - create category
 * - create dish in that category
 * - toggle dish availability
 * - delete dish
 * - delete category
 *
 * This test creates a fresh owner/admin each run via /registro, then uses UI.
 */

test('CRUD happy path (category + dish)', async ({ page }) => {
    const suffix = uniqueSuffix();
    const usuario = `e2e_admin_${suffix}`;
    const password = 'E2E_Test_12345!';
    const email = `e2e_${suffix}@example.com`;
    const slug = `e2e-${suffix}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');

    // Register
    await gotoAndExpectOk(page, '/registro');
    await page.locator('input[name="nombre_completo"]').fill('E2E Admin');
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="usuario"]').fill(usuario);
    await page.locator('input[name="password"]').fill(password);
    await page.locator('input[name="restaurant_nombre"]').fill('Restaurante E2E');
    await page.locator('input[name="restaurant_slug"]').fill(slug);
    await page.getByRole('button', { name: /crear cuenta/i }).click();
    await page.waitForLoadState('domcontentloaded');

    // Login
    await uiLogin(page, usuario, password);
    await expect(page).toHaveURL(/\/restaurants/i);

    // Create category
    await gotoAndExpectOk(page, '/categories');
    await page.locator('#mostrarFormBtn').click();

    const catName = `Cat ${suffix}`;
    await page.locator('#nombre').fill(catName);
    await page.locator('#descripcion').fill('Categoria creada por Playwright');
    await page.locator('#posicion').fill('1');
    await page.getByRole('button', { name: /guardar/i }).click();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('#categoriasTable')).toContainText(catName);

    // Create dish
    await gotoAndExpectOk(page, '/platos');
    await page.locator('#btnCrearPlato').click();
    await expect(page.locator('#modalPlato')).toBeVisible();

    const dishName = `Plato ${suffix}`;
    await page.locator('#modalPlato #nombre').fill(dishName);
    await page.locator('#modalPlato #descripcion').fill('Plato creado por Playwright');
    await page.locator('#modalPlato #precio').fill('10');

    // Choose the category by visible name if possible.
    await page.locator('#modalPlato #categoria_id').selectOption({ label: catName });
    await page.locator('#modalPlato #posicion').fill('1');
    await page.locator('#modalPlato button[type="submit"]').click();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('.plato-card')).toContainText(dishName);

    // Toggle availability (should change the button label)
    const card = page.locator('.plato-card', { hasText: dishName }).first();
    const toggle = card.locator('.btn-toggle-disponibilidad');
    await toggle.click();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('.alert.alert-success')).toContainText(/disponibilidad actualizada/i);

    // Delete dish via UI button (confirm dialog)
    page.once('dialog', (d) => d.accept());
    await card.locator('.btn-eliminar').click();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('.plato-card', { hasText: dishName })).toHaveCount(0);

    // Delete category using the delete form (confirm dialog)
    await gotoAndExpectOk(page, '/categories');
    page.once('dialog', (d) => d.accept());
    const row = page.locator('#categoriasTable tr', { hasText: catName }).first();
    await row.locator('form[action^="/categories/eliminar/"] button').click();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('#categoriasTable')).not.toContainText(catName);
});
