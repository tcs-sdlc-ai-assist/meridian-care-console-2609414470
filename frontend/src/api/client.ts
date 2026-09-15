import type { DashboardData, LoginResponse, MemberList } from '../types';
export type { DashboardData } from '../types';

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${baseUrl}/v1/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
  if (!response.ok) { throw new Error((await response.json()).detail ?? 'Unable to sign in'); }
  return response.json() as Promise<LoginResponse>;
}
async function authenticated<T>(path: string): Promise<T> { const response=await fetch(`${baseUrl}${path}`,{headers:{Authorization:`Bearer ${localStorage.getItem('meridian-token') ?? ''}`}}); if(!response.ok) throw new Error('Unable to load care data'); return response.json() as Promise<T>; }
export function dashboard(): Promise<DashboardData> { return authenticated<DashboardData>('/v1/dashboard'); }
export function members(search: string): Promise<MemberList> { return authenticated<MemberList>(`/v1/members?search=${encodeURIComponent(search)}`); }
