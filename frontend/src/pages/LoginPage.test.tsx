import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { AuthProvider } from '../auth/AuthProvider';
import App from '../App';
import LoginPage from './LoginPage';
const { dashboardMock, loginMock, membersMock } = vi.hoisted(() => ({ dashboardMock: vi.fn(), loginMock: vi.fn(), membersMock: vi.fn() }));
vi.mock('../api/client', () => ({ login: loginMock, dashboard: dashboardMock, members: membersMock }));

afterEach(() => {
  cleanup();
  localStorage.clear();
  loginMock.mockReset();
});

test('shows an accessible authentication error for rejected credentials', async () => {
  loginMock.mockRejectedValueOnce(new Error('Invalid email or password'));
  render(<AuthProvider><LoginPage /></AuthProvider>);
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password');
});

test('persists a successful seeded staff login and renders the authenticated shell', async () => {
  loginMock.mockResolvedValueOnce({ access_token: 'test-token', token_type: 'bearer', user: { coordinator_id: 'COORD-001', name: 'Avery Chen', email: 'coordinator@meridian.example.com', role: 'coordinator' } });
  dashboardMock.mockResolvedValue({ metrics: [], attention: [], activity: [], chart: [0, 0, 0] });
  membersMock.mockResolvedValue({ items: [], total: 0 });
  render(<AuthProvider><App /></AuthProvider>);
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  expect(await screen.findByText('Avery Chen', { exact: true })).toBeVisible();
  expect(localStorage.getItem('meridian-token')).toBe('test-token');
});
