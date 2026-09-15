import LoginPage from './pages/LoginPage';
import { useAuth } from './auth/AuthProvider';
import DashboardPage from './pages/DashboardPage';
import MemberPanelPage from './pages/MemberPanelPage';
export default function App(): JSX.Element { const { user, signOut } = useAuth(); if (!user) return <LoginPage />; return <><nav className="app-nav"><span>Meridian Care</span><span>{user.name}</span><button className="button button-secondary" onClick={signOut}>Sign out</button></nav><DashboardPage /><MemberPanelPage /></>; }
