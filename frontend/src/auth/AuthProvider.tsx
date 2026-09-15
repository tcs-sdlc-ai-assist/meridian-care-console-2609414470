import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { User } from '../types';

interface AuthContextValue { user: User | null; signIn: (user: User, token: string) => void; signOut: () => void; }
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(() => JSON.parse(localStorage.getItem('meridian-user') ?? 'null'));
  const value = useMemo(() => ({ user, signIn: (nextUser: User, token: string) => { localStorage.setItem('meridian-token', token); localStorage.setItem('meridian-user', JSON.stringify(nextUser)); setUser(nextUser); }, signOut: () => { localStorage.removeItem('meridian-token'); localStorage.removeItem('meridian-user'); setUser(null); } }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth(): AuthContextValue { const context = useContext(AuthContext); if (!context) throw new Error('useAuth must be used within AuthProvider'); return context; }
