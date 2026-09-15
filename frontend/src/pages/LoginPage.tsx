import { useState, type FormEvent } from 'react';
import { login } from '../api/client';
import { useAuth } from '../auth/AuthProvider';
import { Button, Card } from '../components/ui';

export default function LoginPage(): JSX.Element {
  const { signIn } = useAuth(); const [email, setEmail] = useState('coordinator@meridian.example.com'); const [password, setPassword] = useState('DemoPass123!'); const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> { event.preventDefault(); setLoading(true); setError(''); try { const result = await login(email, password); signIn(result.user, result.access_token); } catch (caught) { setError(caught instanceof Error ? caught.message : 'Unable to sign in'); } finally { setLoading(false); } }
  return <main className="login-shell"><Card><p className="eyebrow">MERIDIAN CARE</p><h1>Staff console</h1><p className="muted">Use a seeded synthetic-data account to begin.</p><form onSubmit={submit}><label htmlFor="email">Email</label><input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /><label htmlFor="password">Password</label><input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} />{error && <p role="alert" className="error">{error}</p>}<Button type="submit" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</Button></form><aside><strong>Demo accounts</strong><br />coordinator@meridian.example.com<br />supervisor@meridian.example.com<br />auditor@meridian.example.com<br /><span>All use DemoPass123!</span></aside></Card></main>;
}
