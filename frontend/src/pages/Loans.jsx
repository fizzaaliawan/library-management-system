import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { Search, Clock, Calendar, AlertTriangle, RefreshCw } from 'lucide-react';

export default function Loans() {
  const { role, token } = useAuthStore();
  const [loans, setLoans] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const loadLoans = async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      let endpoint = role === 'Librarian' ? '/api/v1/loans/' : '/api/v1/loans/my-history';
      if (role === 'Librarian' && searchQuery) {
        endpoint = `/api/v1/loans/search?q=${encodeURIComponent(searchQuery)}`;
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to load borrowing logs');
      const data = await res.json();
      setLoans(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLoans();
  }, [searchQuery]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Pending';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '4px' }}>Borrowing History</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Track active loans, returns, and overdue timelines</p>
        </div>
      </div>

      {error && (
        <div className="glass-panel" style={{ display: 'flex', gap: '10px', padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.9rem', color: '#fca5a5' }}>{error}</p>
        </div>
      )}

      {/* Searchbar - librarian only */}
      {role === 'Librarian' && (
        <div className="glass-panel" style={{ padding: '16px', display: 'flex', gap: '12px', marginBottom: '32px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
            <input
              type="text"
              className="input-field"
              placeholder="Search loans by book title, ISBN, member email, or status..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '44px' }}
            />
          </div>
          <button onClick={loadLoans} className="btn btn-secondary">
            <RefreshCw size={18} />
          </button>
        </div>
      )}

      {/* Loans Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ color: 'var(--text-secondary)', padding: '20px' }}>Loading loans metrics...</div>
        ) : loans.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No borrowing history records found.</div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  {role === 'Librarian' && <th>Borrower</th>}
                  <th>Book Title</th>
                  <th>ISBN</th>
                  <th>Borrow Date</th>
                  <th>Due Date</th>
                  <th>Returned Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => (
                  <tr key={loan.id}>
                    {role === 'Librarian' && (
                      <td>
                        <div style={{ fontWeight: '600' }}>{loan.member_name}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{loan.member_email}</div>
                      </td>
                    )}
                    <td>
                      <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{loan.book_title}</span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>{loan.book_isbn}</td>
                    <td>{formatDate(loan.borrow_date)}</td>
                    <td>{formatDate(loan.due_date)}</td>
                    <td>{loan.return_date ? formatDate(loan.return_date) : 'Pending'}</td>
                    <td>
                      <span className={`badge ${
                        loan.status === 'Returned' ? 'badge-returned' : 
                        loan.status === 'Overdue' ? 'badge-overdue' : 'badge-active'
                      }`}>
                        {loan.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
