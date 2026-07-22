import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/useAuthStore';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Members from './pages/Members';
import Loans from './pages/Loans';
import { Users, History, LayoutDashboard, LogOut, Bell, AlertTriangle } from 'lucide-react';

function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, role, initialize } = useAuthStore();
  
  useEffect(() => {
    initialize();
  }, []);

  const token = localStorage.getItem('lms_token');
  const userRole = localStorage.getItem('lms_role');

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && requiredRole !== role && requiredRole !== userRole) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function Navbar() {
  const { logout, role, email, token } = useAuthStore();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!token) return;

    const eventSource = new EventSource(`${API_URL}/api/v1/notifications/stream`);

    eventSource.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(event.data);
        setNotifications(prev => [payload, ...prev].slice(0, 10));
        setUnreadCount(prev => prev + 1);
      } catch (err) {
        console.error("Error reading event payload:", err);
      }
    });

    eventSource.addEventListener('error', (err) => {
      console.log("SSE stream closed or encountered error. Reconnecting...");
    });

    return () => {
      eventSource.close();
    };
  }, [token]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="glass-panel" style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      padding: '12px 32px', 
      margin: '20px 40px 10px 40px', 
      borderRadius: '16px',
      background: 'var(--bg-card)',
      borderColor: 'var(--border-color)',
      position: 'relative',
      zIndex: 1000
    }}>
      {/* Brand logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '38px', height: '38px', background: 'var(--primary)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: '800', fontSize: '1.2rem' }}>L</div>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', margin: 0, fontWeight: '700' }}>LMS Portal</h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: '800' }}>{role}</span>
        </div>
      </div>

      {/* Centered Portal Title */}
      <div style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: '800', background: 'linear-gradient(135deg, var(--text-primary) 30%, var(--primary) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
          Library Dashboard
        </h1>
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* SSE Notifications Bell */}
        <div style={{ position: 'relative' }}>
          <button 
            onClick={() => { setShowDropdown(!showDropdown); setUnreadCount(0); }}
            className="btn" 
            style={{ 
              padding: '0', 
              borderRadius: '50%', 
              width: '46px', 
              height: '46px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              position: 'relative',
              background: 'rgba(79, 70, 229, 0.1)',
              color: 'var(--primary)',
              border: '2px solid rgba(79, 70, 229, 0.25)',
              cursor: 'pointer'
            }}
          >
            <Bell size={22} />
            {unreadCount > 0 && (
              <span style={{ position: 'absolute', top: '-2px', right: '-2px', background: 'var(--danger)', width: '18px', height: '18px', borderRadius: '50%', color: 'white', fontSize: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '800' }}>
                {unreadCount}
              </span>
            )}
          </button>

          {showDropdown && (
            <div className="glass-panel animate-fade-in" style={{ position: 'absolute', right: 0, top: '48px', width: '320px', padding: '20px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', boxShadow: 'var(--glass-shadow)', zIndex: 100, maxHeight: '400px', overflowY: 'auto' }}>
              <h5 style={{ fontSize: '0.95rem', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Notifications</span>
                {notifications.length > 0 && (
                  <button onClick={() => setNotifications([])} style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '0.75rem', cursor: 'pointer', fontWeight: '600' }}>
                    Clear
                  </button>
                )}
              </h5>
              {notifications.length === 0 ? (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>No recent notifications</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {notifications.map((n, i) => (
                    <div key={i} style={{ display: 'flex', gap: '10px', borderBottom: i < notifications.length - 1 ? '1px solid rgba(255,255,255,0.02)' : 'none', paddingBottom: '10px' }}>
                      <div style={{ color: n.type === 'overdue' ? 'var(--danger)' : 'var(--primary)', marginTop: '2px', flexShrink: 0 }}>
                        {n.type === 'overdue' ? <AlertTriangle size={14} /> : <Bell size={14} />}
                      </div>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: '1.4', margin: 0 }}>{n.message}</p>
                        <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{new Date(n.timestamp || Date.now()).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* User parameters & LogOut */}
        <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '20px', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.2' }}>Logged in:</span>
            <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: '600', lineHeight: '1.2' }}>{email}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0', width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '10px' }}>
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* Floating Toast Notification */}
    </header>
  );
}

function MainAppLayout() {
  const location = useLocation();
  const { role } = useAuthStore();
  const isActive = (path) => location.pathname === path;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
      <Navbar />
      
      {/* Horizontal Page Tabs Switcher */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px', marginBottom: '8px' }}>
        <div className="glass-panel" style={{ display: 'flex', gap: '8px', padding: '6px', borderRadius: '14px', background: 'rgba(0, 0, 0, 0.03)', borderColor: 'var(--border-color)' }}>
          <Link 
            to="/" 
            className="btn" 
            style={{ 
              padding: '10px 24px', 
              borderRadius: '10px',
              background: isActive('/') ? 'var(--primary)' : 'transparent',
              color: isActive('/') ? 'white' : 'var(--text-secondary)',
              boxShadow: isActive('/') ? '0 4px 14px var(--primary-glow)' : 'none',
              fontWeight: '600'
            }}
          >
            <LayoutDashboard size={16} />
            Book Catalog
          </Link>
          <Link 
            to="/loans" 
            className="btn" 
            style={{ 
              padding: '10px 24px', 
              borderRadius: '10px',
              background: isActive('/loans') ? 'var(--primary)' : 'transparent',
              color: isActive('/loans') ? 'white' : 'var(--text-secondary)',
              boxShadow: isActive('/loans') ? '0 4px 14px var(--primary-glow)' : 'none',
              fontWeight: '600'
            }}
          >
            <History size={16} />
            History Log
          </Link>
          {role === 'Librarian' && (
            <Link 
              to="/members" 
              className="btn" 
              style={{ 
                padding: '10px 24px', 
                borderRadius: '10px',
                background: isActive('/members') ? 'var(--primary)' : 'transparent',
                color: isActive('/members') ? 'white' : 'var(--text-secondary)',
                boxShadow: isActive('/members') ? '0 4px 14px var(--primary-glow)' : 'none',
                fontWeight: '600'
              }}
            >
              <Users size={16} />
              Members
            </Link>
          )}
        </div>
      </div>

      <main className="main-content" style={{ flex: 1, padding: '20px 40px 40px 40px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        <Routes>
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/loans" element={<ProtectedRoute><Loans /></ProtectedRoute>} />
          <Route path="/members" element={<ProtectedRoute requiredRole="Librarian"><Members /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/*" element={<ProtectedRoute><MainAppLayout /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}
