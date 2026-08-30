'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

export default function MembersPage() {
  const [members, setMembers] = useState<any[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('MEMBER');
  const [inviteLoading, setInviteLoading] = useState(false);

  const fetchMembers = async () => {
    try {
      const res = await apiClient.GET('/api/v1/organizations/members');
      if (res.data) setMembers(res.data as any[]);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMe = async () => {
    try {
      const res = await apiClient.GET('/api/v1/auth/me');
      if (res.data) setCurrentUser(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    const load = async () => {
      await Promise.all([fetchMembers(), fetchMe()]);
      setLoading(false);
    };
    load();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteLoading(true);
    try {
      const res = await apiClient.POST('/api/v1/organizations/members', {
        body: { email: inviteEmail, role: inviteRole }
      });
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Failed to invite');
      await fetchMembers();
      setShowInviteModal(false);
      setInviteEmail('');
      setInviteRole('MEMBER');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setInviteLoading(false);
    }
  };

  const handleUpdateRole = async (memberId: string, role: string) => {
    try {
      const res = await apiClient.PATCH('/api/v1/organizations/members/{member_id}/role', {
        params: { path: { member_id: memberId as any } },
        body: { role }
      });
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Failed to update role');
      await fetchMembers();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this member?')) return;
    try {
      const res = await apiClient.DELETE('/api/v1/organizations/members/{member_id}', {
        params: { path: { member_id: memberId as any } }
      });
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Failed to remove member');
      await fetchMembers();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const currentUserRole = currentUser ? members.find(m => m.user.id === currentUser.id)?.role : null;
  const canManageMembers = currentUserRole === 'OWNER' || currentUserRole === 'ADMIN';
  const canUpdateRole = currentUserRole === 'OWNER';

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Organization Members</h1>
          <p className="page-subtitle">Manage access to your organization.</p>
        </div>
        {canManageMembers && (
          <button className="btn btn-primary" onClick={() => setShowInviteModal(true)}>Invite Member</button>
        )}
      </div>
      
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</td>
              </tr>
            ) : members.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>No members found</td>
              </tr>
            ) : members.map((member) => {
              const isSelf = currentUser && member.user.id === currentUser.id;
              
              return (
                <tr key={member.id}>
                  <td style={{ fontWeight: 500 }}>
                    {member.user.name} {isSelf && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '8px' }}>(You)</span>}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{member.user.email}</td>
                  <td>
                    {canUpdateRole && !isSelf ? (
                      <select 
                        value={member.role}
                        onChange={(e) => handleUpdateRole(member.id, e.target.value)}
                        className="input-field"
                        style={{ padding: '4px 8px' }}
                      >
                        <option value="OWNER">OWNER</option>
                        <option value="ADMIN">ADMIN</option>
                        <option value="MEMBER">MEMBER</option>
                        <option value="VIEWER">VIEWER</option>
                      </select>
                    ) : (
                      <span className="badge default">{member.role}</span>
                    )}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {member.created_at ? new Date(member.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td>
                    {canManageMembers && !isSelf && (
                      <button 
                        className="btn btn-sm btn-secondary" 
                        style={{ color: 'var(--error)' }}
                        onClick={() => handleRemove(member.id)}
                      >
                        Remove
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {showInviteModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>Invite Member</h3>
            <form onSubmit={handleInvite} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px' }}>Email Address</label>
                <input 
                  type="email" 
                  value={inviteEmail} 
                  onChange={e => setInviteEmail(e.target.value)} 
                  required 
                  className="input-field" 
                  style={{ width: '100%' }} 
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px' }}>Role</label>
                <select 
                  value={inviteRole} 
                  onChange={e => setInviteRole(e.target.value)}
                  className="input-field"
                  style={{ width: '100%' }}
                >
                  {canUpdateRole && <option value="OWNER">OWNER</option>}
                  <option value="ADMIN">ADMIN</option>
                  <option value="MEMBER">MEMBER</option>
                  <option value="VIEWER">VIEWER</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '8px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowInviteModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={inviteLoading || !inviteEmail}>
                  {inviteLoading ? 'Inviting...' : 'Send Invite'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
