'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import { useState, useEffect } from 'react';

export default function SettingsPage() {
  const [user, setUser] = useState<{name: string, email: string} | null>(null);
  const [org, setOrg] = useState<{name: string, account_type: string} | null>(null);
  
  useEffect(() => {
    try {
      const u = localStorage.getItem('user');
      const o = localStorage.getItem('current_org');
      // eslint-disable-next-line
      if (u) setUser(JSON.parse(u));
      // eslint-disable-next-line
      if (o) setOrg(JSON.parse(o));
    } catch (_) {
      // ignore
    }
  }, []);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account, organization, and preferences.</p>
      </div>
      
      <div style={{ display: 'grid', gap: '32px', maxWidth: '800px' }}>
        {/* General Settings */}
        <section className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '16px' }}>Organization Profile</h2>
          <div style={{ display: 'grid', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px', color: 'var(--text-muted)' }}>Organization Name</label>
              <input type="text" defaultValue={org?.name || ''} className="input-field" style={{ width: '100%' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px', color: 'var(--text-muted)' }}>Account Type</label>
              <div style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}>
                {org?.account_type || 'Loading...'}
              </div>
            </div>
          </div>
        </section>
        
        {/* User Profile */}
        <section className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '16px' }}>Your Profile</h2>
          <div style={{ display: 'grid', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px', color: 'var(--text-muted)' }}>Name</label>
              <input type="text" defaultValue={user?.name || ''} className="input-field" style={{ width: '100%' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '8px', color: 'var(--text-muted)' }}>Email</label>
              <input type="email" defaultValue={user?.email || ''} readOnly className="input-field" style={{ width: '100%', color: 'var(--text-muted)', cursor: 'not-allowed' }} />
            </div>
          </div>
        </section>
        
        <section className="card flex-between">
          <div>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '4px' }}>Danger Zone</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Permanently delete this organization and all data.</p>
          </div>
          <button className="btn btn-secondary" style={{ color: 'var(--error)' }}>Delete Organization</button>
        </section>
      </div>
    </>
  );
}
