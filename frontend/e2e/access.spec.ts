import { expect, test, type Page } from '@playwright/test';

function captureBrowserErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (message) => {
    const text = message.text();
    if (message.type() === 'error' && !text.includes('401 (Unauthorized)')) errors.push(`console: ${text}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  return errors;
}

test('shows the real API error for invalid credentials and signs in with the seeded account', async ({ page }, testInfo) => {
  const browserErrors = captureBrowserErrors(page);

  await page.goto('/');
  await page.getByLabel('Email').fill('coordinator@meridian.example.com');
  await page.getByLabel('Password').fill('not-the-demo-password');
  const invalidLogin = page.waitForResponse((response) => response.url().includes('/api/v1/auth/login') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Sign in' }).click();
  expect((await invalidLogin).status()).toBe(401);
  await expect(page.getByRole('alert')).toHaveText('Invalid email or password');

  await page.getByLabel('Password').fill('DemoPass123!');
  const validLogin = page.waitForResponse((response) => response.url().includes('/api/v1/auth/login') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Sign in' }).click();
  const loginResponse = await validLogin;
  expect(loginResponse.status()).toBe(200);
  await expect(page.getByText('Avery Chen', { exact: true })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('authenticated-access.png'), fullPage: true });
  expect(browserErrors).toEqual([]);
});

test('keeps protected operational content hidden before authentication', async ({ page }) => {
  const browserErrors = captureBrowserErrors(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Staff console' })).toBeVisible();
  await expect(page.getByText('Care management overview')).toHaveCount(0);
  await expect(page.getByText('Member panel')).toHaveCount(0);
  expect(browserErrors).toEqual([]);
});
