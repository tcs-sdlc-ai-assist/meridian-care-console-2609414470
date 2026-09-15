import { expect, test, type Page } from '@playwright/test';

function captureBrowserErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  return errors;
}

async function signIn(page: Page): Promise<void> {
  await page.goto('/');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Avery Chen', { exact: true })).toBeVisible();
}

test('renders real dashboard data, handles an empty member search, and persists the selected theme', async ({ page }, testInfo) => {
  const browserErrors = captureBrowserErrors(page);

  const dashboardResponse = page.waitForResponse((response) => response.url().includes('/api/v1/dashboard') && response.request().method() === 'GET');
  await signIn(page);
  const response = await dashboardResponse;
  expect(response.status()).toBe(200);
  await expect(response.json()).resolves.toMatchObject({
    metrics: expect.arrayContaining([
      expect.objectContaining({ label: 'Members assigned', value: expect.any(Number) }),
      expect.objectContaining({ label: 'Open care gaps', value: expect.any(Number) }),
    ]),
    attention: ['Rosa Diaz'],
    activity: ['Demo environment seeded'],
  });
  await expect(page.getByRole('heading', { name: 'Care management overview' })).toBeVisible();
  await expect(page.getByText('Members assigned')).toBeVisible();
  await expect(page.getByText('Demo environment seeded', { exact: true })).toBeVisible();

  const memberSearch = page.waitForResponse((searchResponse) => searchResponse.url().includes('/api/v1/members?search=NoSuchMember') && searchResponse.request().method() === 'GET');
  await page.getByLabel('Search members').fill('NoSuchMember');
  expect((await memberSearch).status()).toBe(200);
  await expect(page.getByText('No members match these filters.')).toBeVisible();

  await page.getByRole('button', { name: 'Dark mode' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.getByRole('button', { name: 'Light mode' })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('dashboard-dark-theme.png'), fullPage: true });
  expect(browserErrors).toEqual([]);
});
