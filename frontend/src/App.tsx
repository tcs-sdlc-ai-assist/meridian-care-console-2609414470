import LoginPage from './pages/LoginPage';
import { useAuth } from './auth/AuthProvider';
import DashboardPage from './pages/DashboardPage';
import MemberPanelPage from './pages/MemberPanelPage';
import MemberDetailPage from './pages/MemberDetailPage';
import { ThemeToggle } from './components/ThemeToggle';
export default function App(): JSX.Element { const { user, signOut } = useAuth(); if (!user) return <LoginPage />; return <><nav className="app-nav"><span>Meridian Care</span><span>{user.name}</span><ThemeToggle /><button className="button button-secondary" onClick={signOut}>Sign out</button></nav><DashboardPage /><MemberPanelPage /><MemberDetailPage /></>; }
