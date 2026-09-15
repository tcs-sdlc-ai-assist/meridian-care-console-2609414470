import { expect, test, type Page } from '@playwright/test';

function captureBrowserErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  return errors;
}

test('uses the tablet layout and saves outreach through the live backend', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  const browserErrors = captureBrowserErrors(page);

  const detailResponse = page.waitForResponse((response) => response.url().includes('/api/v1/members/MEM-1001') && response.request().method() === 'GET');
  await page.goto('/');
  await page.getByRole('button', { name: 'Sign in' }).click();
  expect((await detailResponse).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Rosa Diaz' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Care plan' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Member panel' })).toBeVisible();

  await page.getByRole('button', { name: 'Log outreach' }).click();
  const note = `E2E tablet outreach ${Date.now()}`;
  await page.getByLabel('Notes').fill(note);
  const outreachResponse = page.waitForResponse((response) => response.url().includes('/api/v1/members/MEM-1001/outreach') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Save outreach' }).click();
  expect((await outreachResponse).status()).toBe(201);
  await expect(page.getByText(note)).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('member-workflow-tablet.png'), fullPage: true });
  expect(browserErrors).toEqual([]);
});

test('auditor sees member detail but no mutation controls', async ({ page }) => {
  const browserErrors = captureBrowserErrors(page);
  await page.goto('/');
  await page.getByLabel('Email').fill('auditor@meridian.example.com');
  await page.getByLabel('Password').fill('DemoPass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Rosa Diaz' })).toBeVisible();
  await expect(page.getByText(/SSN \*\*\*-\*\*-6789/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Log outreach' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Close' })).toHaveCount(0);
  expect(browserErrors).toEqual([]);
});
