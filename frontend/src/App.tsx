import LoginPage from './pages/LoginPage';
import { useAuth } from './auth/AuthProvider';
export default function App(): JSX.Element { const { user, signOut } = useAuth(); return user ? <main className="login-shell"><h1>Welcome, {user.name}</h1><p>You are signed in as {user.role}.</p><button className="button button-secondary" onClick={signOut}>Sign out</button></main> : <LoginPage />; }
