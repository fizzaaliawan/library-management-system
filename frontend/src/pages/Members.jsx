import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { Search, Plus, Trash2, Edit, CheckCircle, UserPlus, RefreshCw } from 'lucide-react';

export default function Members() {
  const { role, token } = useAuthStore();
  const [members, setMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Register Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [memberForm, setMemberForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: ''
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const loadMembers = async () => {
    if (role !== 'Librarian' || !token) return;
    setLoading(true);
    setError('');
    try {
      let url = `${API_URL}/api/v1/members/`;
      if (searchQuery) {
        url = `${API_URL}/api/v1/members/search?q=${encodeURIComponent(searchQuery)}`;
      }

      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to load library members list');
      const data = await res.json();
      setMembers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, [searchQuery]);

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingMember) {
        // Update member PUT request (only editable fields: first_name, last_name, phone)
        const updateData = {
          first_name: memberForm.first_name,
          last_name: memberForm.last_name,
          phone: memberForm.phone
        };
        const res = await fetch(`${API_URL}/api/v1/members/${editingMember.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(updateData)
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Failed to update member');
        }
      } else {
        // Register member POST request
        const res = await fetch(`${API_URL}/api/v1/members/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(memberForm)
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Failed to register member');
        }
      }

      setSuccess(`Member details successfully ${editingMember ? 'updated' : 'registered'}!`);
      setShowAddModal(false);
      setEditingMember(null);
      setMemberForm({ email: '', password: '', first_name: '', last_name: '', phone: '' });
      loadMembers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to soft-delete this member account?')) return;
    setError('');
    setSuccess('');

    try {
      const res = await fetch(`${API_URL}/api/v1/members/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to delete member');
      }

      setSuccess('Member account soft-deleted successfully!');
      loadMembers();
    } catch (err) {
      setError(err.message);
    }
  };

  const startEdit = (member) => {
    setEditingMember(member);
    setMemberForm({
      email: member.email,
      password: '', // password not editable directly here
      first_name: member.first_name,
      last_name: member.last_name,
      phone: member.phone || ''
    });
    setShowAddModal(true);
  };

  if (role !== 'Librarian') {
    return <div style={{ padding: '40px', color: 'var(--text-secondary)' }}>Access denied. Regular members are not allowed to view the registry.</div>;
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '4px' }}>Member Registry</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage library memberships and details</p>
        </div>

        <button onClick={() => { setEditingMember(null); setShowAddModal(true); }} className="btn btn-primary">
          <UserPlus size={18} />
          Register Member
        </button>
      </div>

      {success && (
        <div className="glass-panel" style={{ display: 'flex', gap: '10px', padding: '12px 16px', background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.2)', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.9rem', color: '#a7f3d0' }}>{success}</p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ display: 'flex', gap: '10px', padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.9rem', color: '#fca5a5' }}>{error}</p>
        </div>
      )}

      {/* Searchbar */}
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', gap: '12px', marginBottom: '32px' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Search by name, email, or membership number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '44px' }}
          />
        </div>
        <button onClick={loadMembers} className="btn btn-secondary">
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Members List */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ color: 'var(--text-secondary)', padding: '20px' }}>Loading registry database...</div>
        ) : members.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No members registered in database.</div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Membership Card</th>
                  <th>Full Name</th>
                  <th>Email Login</th>
                  <th>Contact Phone</th>
                  <th>Account Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: '700', color: 'var(--primary)' }}>
                      {m.membership_number}
                    </td>
                    <td style={{ fontWeight: '600' }}>{`${m.first_name} ${m.last_name}`}</td>
                    <td>{m.email}</td>
                    <td>{m.phone || 'N/A'}</td>
                    <td>
                      <span className={`badge ${m.is_active ? 'badge-active' : 'badge-overdue'}`}>
                        {m.is_active ? 'Active' : 'Suspended'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={() => startEdit(m)} className="btn btn-secondary" style={{ padding: '6px' }}>
                          <Edit size={16} />
                        </button>
                        <button onClick={() => handleDelete(m.id)} className="btn btn-danger" style={{ padding: '6px' }}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Register / Update Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: '500px', maxHeight: '90vh', overflowY: 'auto', padding: '24px', background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '20px' }}>
              {editingMember ? 'Update Member Profile' : 'Register New Member'}
            </h3>

            <form onSubmit={handleFormSubmit}>
              {!editingMember && (
                <>
                  <div className="form-group" style={{ marginBottom: '14px' }}>
                    <label className="form-label">Email Address</label>
                    <input
                      type="email"
                      required
                      className="input-field"
                      value={memberForm.email}
                      onChange={(e) => setMemberForm({ ...memberForm, email: e.target.value })}
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: '14px' }}>
                    <label className="form-label">Login Password</label>
                    <input
                      type="password"
                      required
                      className="input-field"
                      placeholder="••••••••"
                      value={memberForm.password}
                      onChange={(e) => setMemberForm({ ...memberForm, password: e.target.value })}
                    />
                  </div>
                </>
              )}

              <div style={{ display: 'flex', gap: '16px' }}>
                <div className="form-group" style={{ flex: 1, marginBottom: '14px' }}>
                  <label className="form-label">First Name</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    value={memberForm.first_name}
                    onChange={(e) => setMemberForm({ ...memberForm, first_name: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 1, marginBottom: '14px' }}>
                  <label className="form-label">Last Name</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    value={memberForm.last_name}
                    onChange={(e) => setMemberForm({ ...memberForm, last_name: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Contact Phone</label>
                <input
                  type="text"
                  className="input-field"
                  value={memberForm.phone}
                  onChange={(e) => setMemberForm({ ...memberForm, phone: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingMember ? 'Update Profile' : 'Register Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
