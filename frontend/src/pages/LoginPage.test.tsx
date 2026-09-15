import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { AuthProvider } from '../auth/AuthProvider';
import LoginPage from './LoginPage';
vi.mock('../api/client', () => ({ login: vi.fn().mockRejectedValue(new Error('Invalid email or password')) }));
test('shows an accessible authentication error for rejected credentials', async () => { render(<AuthProvider><LoginPage /></AuthProvider>); fireEvent.click(screen.getByRole('button', { name: 'Sign in' })); expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password'); });
