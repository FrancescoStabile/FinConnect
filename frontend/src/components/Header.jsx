import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          FinConnect
        </Link>
        
        <nav className="nav">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/transfer">Bonifici</Link>
              <Link to="/investments">Investimenti</Link>
              <div className="nav-divider" />
              <div className="user-info">
                <div className="user-avatar">
                  {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U'}
                </div>
                <span className="user-name">{user?.full_name?.split(' ')[0]}</span>
                <button onClick={handleLogout} className="btn-logout">Esci</button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login">Accedi</Link>
              <Link to="/register">Registrati</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
