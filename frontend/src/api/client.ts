import type { LoginResponse } from '../types';

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${baseUrl}/v1/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
  if (!response.ok) { throw new Error((await response.json()).detail ?? 'Unable to sign in'); }
  return response.json() as Promise<LoginResponse>;
}
