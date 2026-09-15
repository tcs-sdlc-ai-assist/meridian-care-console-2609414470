import { test, expect } from '@playwright/test';
test('coordinator dashboard renders backend dashboard content', async ({ page }) => { await page.goto('/'); await page.getByRole('button',{name:'Sign in'}).click(); await expect(page.getByText('Care management overview')).toBeVisible(); });
