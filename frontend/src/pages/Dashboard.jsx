import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { Book, Users, BookOpen, Clock, Activity, CheckCircle, RefreshCw, Search, Plus, Trash2, Edit } from 'lucide-react';

export default function Dashboard() {
  const { role, token, email } = useAuthStore();
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    totalBooks: 0,
    availableBooks: 0,
    totalMembers: 0,
    activeLoans: 0
  });
  const [books, setBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('All');
  const [showOnlyAvailable, setShowOnlyAvailable] = useState(false);
  const [loading, setLoading] = useState(true);
  const [triggerStatus, setTriggerStatus] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal / Form state for Add/Edit Book
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [bookForm, setBookForm] = useState({
    title: '',
    author: '',
    isbn: '',
    genre: '',
    total_copies: 1
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchData = async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      // 1. Fetch books (either all or filtered by search)
      let booksUrl = `${API_URL}/api/v1/books/`;
      if (searchQuery) {
        booksUrl = `${API_URL}/api/v1/books/search?q=${encodeURIComponent(searchQuery)}`;
      }
      const booksRes = await fetch(booksUrl, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!booksRes.ok) throw new Error('Failed to load books catalog');
      const booksData = await booksRes.json();
      setBooks(booksData);

      // 2. Fetch stats parameters
      let fullBooks = booksData;
      if (searchQuery) {
        const fullRes = await fetch(`${API_URL}/api/v1/books/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        fullBooks = await fullRes.json();
      }

      const totalBooksCount = fullBooks.reduce((acc, b) => acc + b.total_copies, 0);
      const availCount = fullBooks.reduce((acc, b) => acc + b.available_copies, 0);

      let membersCount = 0;
      let loansCount = 0;

      if (role === 'Librarian') {
        const memRes = await fetch(`${API_URL}/api/v1/members/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const members = await memRes.json();
        membersCount = members.length;

        const loansRes = await fetch(`${API_URL}/api/v1/loans/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const loans = await loansRes.json();
        loansCount = loans.filter(l => l.status === 'Active' || l.status === 'Overdue').length;
      } else {
        const myLoansRes = await fetch(`${API_URL}/api/v1/loans/my-history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const myLoans = await myLoansRes.json();
        loansCount = myLoans.filter(l => l.status === 'Active' || l.status === 'Overdue').length;
        membersCount = 1;
      }

      setStats({
        totalBooks: totalBooksCount,
        availableBooks: availCount,
        totalMembers: membersCount,
        activeLoans: loansCount
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token, role, searchQuery]);

  const handleTriggerOverdue = async () => {
    setTriggerStatus('Dispatched...');
    try {
      const res = await fetch(`${API_URL}/api/v1/loans/trigger-overdue-check`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 202) {
        setTriggerStatus('Scan active');
        setTimeout(() => setTriggerStatus(''), 4000);
        fetchData();
      } else {
        setTriggerStatus('Failed');
      }
    } catch (err) {
      setTriggerStatus('Error');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const method = editingBook ? 'PUT' : 'POST';
      const endpoint = editingBook ? `/api/v1/books/${editingBook.id}` : '/api/v1/books/';

      const res = await fetch(`${API_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(bookForm)
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to save book');
      }

      setSuccess(`Book successfully ${editingBook ? 'updated' : 'added'}!`);
      setShowAddModal(false);
      setEditingBook(null);
      setBookForm({ title: '', author: '', isbn: '', genre: '', total_copies: 1 });
      fetchData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to soft-delete this book?')) return;
    setError('');
    setSuccess('');

    try {
      const res = await fetch(`${API_URL}/api/v1/books/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to delete book');
      }

      setSuccess('Book deleted successfully!');
      fetchData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBorrow = async (book) => {
    setError('');
    setSuccess('');

    let borrowEmail = email;
    
    if (role === 'Librarian') {
      const customEmail = prompt("Enter Member Email address:", '');
      if (!customEmail) return;
      borrowEmail = customEmail;
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/loans/borrow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          member_email: borrowEmail,
          isbn: book.isbn,
          days: 14
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Borrow operation failed');
      }

      setSuccess(`Book borrow completed to ${borrowEmail}!`);
      fetchData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReturn = async (book) => {
    setError('');
    setSuccess('');

    let returnEmail = email;

    if (role === 'Librarian') {
      const customEmail = prompt("Enter Member Email returning this book:", '');
      if (!customEmail) return;
      returnEmail = customEmail;
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/loans/return`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          member_email: returnEmail,
          isbn: book.isbn
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Return operation failed');
      }

      setSuccess(`Book returned successfully from ${returnEmail}!`);
      fetchData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message);
    }
  };

  const startEdit = (book) => {
    setEditingBook(book);
    setBookForm({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      genre: book.genre || '',
      total_copies: book.total_copies
    });
    setShowAddModal(true);
  };

  let filteredBooks = selectedSubject === 'All'
    ? books
    : books.filter(book => book.genre === selectedSubject);

  if (showOnlyAvailable) {
    filteredBooks = filteredBooks.filter(book => book.available_copies > 0);
  }

  return (
    <div className="animate-fade-in" style={{ paddingTop: '10px' }}>
      {success && (
        <div className="glass-panel" style={{ display: 'flex', gap: '10px', padding: '12px 16px', background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.2)', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.9rem', color: '#a7f3d0', fontWeight: '600' }}>{success}</p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ display: 'flex', gap: '10px', padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.9rem', color: '#fca5a5', fontWeight: '600' }}>{error}</p>
        </div>
      )}

      {/* Grid counters (Interactive Switchers) */}
      <div className="dashboard-grid" style={{ marginBottom: '32px' }}>
        <div 
          onClick={() => {
            setShowOnlyAvailable(false);
            setSelectedSubject('All');
            setSearchQuery('');
            document.getElementById('catalog-section')?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="glass-panel stats-card" 
          style={{ 
            cursor: 'pointer',
            transition: 'var(--transition)',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, var(--bg-card) 100%)', 
            border: '1px solid rgba(99, 102, 241, 0.15)' 
          }}
        >
          <div className="stats-icon" style={{ background: 'rgba(99, 102, 241, 0.12)', color: 'var(--primary)' }}>
            <Book size={20} />
          </div>
          <div>
            <h4 style={{ fontSize: '1.7rem', fontWeight: '800' }}>{stats.totalBooks}</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Catalog</p>
          </div>
        </div>

        <div 
          onClick={() => {
            setShowOnlyAvailable(true);
            setSelectedSubject('All');
            setSearchQuery('');
            document.getElementById('catalog-section')?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="glass-panel stats-card" 
          style={{ 
            cursor: 'pointer',
            transition: 'var(--transition)',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, var(--bg-card) 100%)', 
            border: '1px solid rgba(16, 185, 129, 0.15)' 
          }}
        >
          <div className="stats-icon" style={{ background: 'rgba(16, 185, 129, 0.12)', color: 'var(--accent)' }}>
            <BookOpen size={20} />
          </div>
          <div>
            <h4 style={{ fontSize: '1.7rem', fontWeight: '800' }}>{stats.availableBooks}</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Available</p>
          </div>
        </div>

        <div 
          onClick={() => navigate('/loans')}
          className="glass-panel stats-card" 
          style={{ 
            cursor: 'pointer',
            transition: 'var(--transition)',
            background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, var(--bg-card) 100%)', 
            border: '1px solid rgba(236, 72, 153, 0.15)' 
          }}
        >
          <div className="stats-icon" style={{ background: 'rgba(236, 72, 153, 0.12)', color: 'var(--secondary)' }}>
            <Clock size={20} />
          </div>
          <div>
            <h4 style={{ fontSize: '1.7rem', fontWeight: '800' }}>{stats.activeLoans}</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {role === 'Librarian' ? 'Active Loans' : 'My borrowed books'}
            </p>
          </div>
        </div>

        {role === 'Librarian' && (
          <div 
            onClick={() => navigate('/members')}
            className="glass-panel stats-card" 
            style={{ 
              cursor: 'pointer',
              transition: 'var(--transition)',
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, var(--bg-card) 100%)', 
              border: '1px solid rgba(245, 158, 11, 0.15)' 
            }}
          >
            <div className="stats-icon" style={{ background: 'rgba(245, 158, 11, 0.12)', color: 'var(--warning)' }}>
              <Users size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '1.7rem', fontWeight: '800' }}>{stats.totalMembers}</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Members</p>
            </div>
          </div>
        )}
      </div>

      {/* Database overdue scan strip */}
      {role === 'Librarian' && (
        <div className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', background: 'rgba(99, 102, 241, 0.03)', borderColor: 'rgba(99, 102, 241, 0.08)', marginBottom: '40px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Activity size={18} color="var(--primary)" />
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '500' }}>
              Database overdue scan manager daemon
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {triggerStatus && (
              <span style={{ fontSize: '0.85rem', color: 'var(--accent)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle size={14} />
                {triggerStatus}
              </span>
            )}
            <button onClick={handleTriggerOverdue} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              Run scan
            </button>
          </div>
        </div>
      )}

      {/* Catalog Title Section */}
      <div id="catalog-section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', marginTop: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h2 style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--text-primary)' }}>Book Catalog</h2>
              {showOnlyAvailable && (
                <span 
                  onClick={() => setShowOnlyAvailable(false)}
                  style={{ fontSize: '0.75rem', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent)', padding: '4px 10px', borderRadius: '12px', fontWeight: '700', cursor: 'pointer' }}
                >
                  Showing Available Only (Click to Reset)
                </span>
              )}
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Search and select items to borrow or return</p>
          </div>
          <button onClick={fetchData} className="btn btn-secondary" style={{ width: '36px', height: '36px', padding: 0, borderRadius: '50%', border: 'none', background: 'rgba(255,255,255,0.03)' }}>
            <RefreshCw size={14} />
          </button>
        </div>
        {role === 'Librarian' && (
          <button onClick={() => { setEditingBook(null); setShowAddModal(true); }} className="btn btn-primary" style={{ padding: '8px 16px', borderRadius: '10px', fontSize: '0.88rem' }}>
            <Plus size={16} />
            Add Book
          </button>
        )}
      </div>

      {/* Searchbar & Subject Filter */}
      <div className="glass-panel" style={{ padding: '12px', display: 'flex', gap: '16px', marginBottom: '32px', background: 'rgba(255,255,255,0.01)', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Search by title, author, or ISBN..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '44px', borderRadius: '10px' }}
          />
        </div>
        
        {/* Subject Filter Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: '600', whiteSpace: 'nowrap' }}>
            Filter Subject:
          </label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="input-field"
            style={{ 
              width: '200px', 
              borderRadius: '10px', 
              background: 'var(--bg-card)', 
              borderColor: 'var(--border-color)', 
              color: 'var(--text-primary)', 
              cursor: 'pointer',
              height: '42px',
              padding: '0 12px'
            }}
          >
            <option value="All">All Subjects</option>
            {[...new Set(books.map(b => b.genre).filter(Boolean))].map((genre, idx) => (
              <option key={idx} value={genre}>{genre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Books Card Grid */}
      {loading && books.length === 0 ? (
        <div style={{ color: 'var(--text-secondary)', padding: '20px' }}>Loading books database...</div>
      ) : filteredBooks.length === 0 ? (
        <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No books matching search parameters.</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
          {filteredBooks.map((book) => (
            <div key={book.id} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '260px', transition: 'var(--transition)', background: 'var(--bg-card)' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <span style={{ fontSize: '0.75rem', background: 'rgba(99, 102, 241, 0.12)', color: 'var(--primary)', padding: '4px 10px', borderRadius: '12px', fontWeight: '700', textTransform: 'uppercase' }}>
                    {book.genre || 'General'}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: book.available_copies > 0 ? 'var(--accent)' : 'var(--danger)', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: book.available_copies > 0 ? 'var(--accent)' : 'var(--danger)' }}></span>
                    {book.available_copies > 0 ? `${book.available_copies} / ${book.total_copies} Left` : 'Out of Stock'}
                  </span>
                </div>
                
                <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '6px', fontWeight: '700', lineHeight: '1.3' }}>
                  {book.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '16px', fontWeight: '500' }}>
                  by {book.author}
                </p>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginBottom: '24px' }}>
                  ISBN: {book.isbn}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '16px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    onClick={() => handleBorrow(book)} 
                    disabled={book.available_copies <= 0} 
                    className="btn btn-primary" 
                    style={{ padding: '6px 14px', fontSize: '0.8rem', borderRadius: '8px', background: book.available_copies > 0 ? 'var(--primary)' : 'rgba(255,255,255,0.05)', color: book.available_copies > 0 ? 'white' : 'var(--text-muted)' }}
                  >
                    Borrow
                  </button>
                  <button 
                    onClick={() => handleReturn(book)} 
                    className="btn btn-secondary" 
                    style={{ padding: '6px 14px', fontSize: '0.8rem', borderRadius: '8px' }}
                  >
                    Return
                  </button>
                </div>

                {role === 'Librarian' && (
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button onClick={() => startEdit(book)} className="btn btn-secondary" style={{ padding: '8px', borderRadius: '8px' }}>
                      <Edit size={14} />
                    </button>
                    <button onClick={() => handleDelete(book.id)} className="btn btn-secondary" style={{ padding: '8px', borderRadius: '8px', color: 'var(--danger)', borderColor: 'rgba(239,68,68,0.1)' }}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add / Edit Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '500px', maxHeight: '90vh', overflowY: 'auto', padding: '24px', background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '20px', fontWeight: '800' }}>
              {editingBook ? 'Edit Book Specifications' : 'Add New Catalog Book'}
            </h3>
            
            <form onSubmit={handleFormSubmit}>
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Book Title</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={bookForm.title}
                  onChange={(e) => setBookForm({ ...bookForm, title: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Author Name</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={bookForm.author}
                  onChange={(e) => setBookForm({ ...bookForm, author: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">ISBN Identifier</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={bookForm.isbn}
                  onChange={(e) => setBookForm({ ...bookForm, isbn: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Genre</label>
                <input
                  type="text"
                  className="input-field"
                  value={bookForm.genre}
                  onChange={(e) => setBookForm({ ...bookForm, genre: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Total Copies Stocked</label>
                <input
                  type="number"
                  required
                  min="1"
                  className="input-field"
                  value={bookForm.total_copies}
                  onChange={(e) => setBookForm({ ...bookForm, total_copies: parseInt(e.target.value) })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Book
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
