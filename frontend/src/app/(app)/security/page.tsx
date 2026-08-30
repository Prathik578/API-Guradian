'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

export default function SecurityPage() {
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [mfaData, setMfaData] = useState<{ secret: string, uri: string } | null>(null);
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await apiClient.GET('/api/v1/auth/me');
        if (res.data) {
          setMfaEnabled(res.data.mfa_enabled || false);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setInitialLoading(false);
      }
    };
    fetchUser();
  }, []);

  const enableMfa = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.POST('/api/v1/mfa/enable');
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Failed to enable MFA');
      if (res.data) setMfaData(res.data as any);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const verifyMfa = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.POST('/api/v1/mfa/verify', { body: { code } });
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Invalid code');
      setSuccess('MFA successfully enabled!');
      setMfaData(null);
      setMfaEnabled(true);
      setCode('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const disableMfa = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.POST('/api/v1/mfa/disable', { body: { code } });
      if ((res as any).error) throw new Error(((res as any).error as any).detail || 'Invalid code');
      setSuccess('MFA successfully disabled!');
      setMfaEnabled(false);
      setCode('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }
    
    try {
      const res = await apiClient.POST('/api/v1/auth/change-password', {
        body: { current_password: currentPassword, new_password: newPassword, confirm_password: confirmPassword }
      });
      if (res.error) {
        const errorDetail = res.error?.detail;
        const errorMessage = Array.isArray(errorDetail) 
          ? errorDetail.map((err: any) => err.msg).join(', ') 
          : (typeof errorDetail === 'string' ? errorDetail : 'Failed to change password');
        throw new Error(errorMessage);
      }
      setSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Security Settings</h1>
        <p className="page-subtitle">Manage your account security and authentication.</p>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div className="card" style={{ maxWidth: '600px' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>Change Password</h3>
          <form onSubmit={changePassword} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <input type="password" placeholder="Current Password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} required className="input-field" />
            <input type="password" placeholder="New Password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required className="input-field" />
            <input type="password" placeholder="Confirm New Password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required className="input-field" />
            <button type="submit" className="btn btn-primary" disabled={loading || !currentPassword || !newPassword || !confirmPassword}>Change Password</button>
          </form>
        </div>

        <div className="card" style={{ maxWidth: '600px' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>Two-Factor Authentication (MFA)</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
            Add an extra layer of security to your account by enabling Multi-Factor Authentication. 
          </p>

          {error && <div style={{ padding: '12px', background: 'rgba(255,0,0,0.1)', color: 'var(--error)', borderRadius: '6px', marginBottom: '16px' }}>{error}</div>}
          {success && <div style={{ padding: '12px', background: 'rgba(0,255,0,0.1)', color: 'var(--success)', borderRadius: '6px', marginBottom: '16px' }}>{success}</div>}

          {!mfaData && !mfaEnabled && (
            <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
              <button className="btn btn-primary" onClick={enableMfa} disabled={loading || initialLoading} style={{ width: 'fit-content' }}>
                Set up MFA
              </button>
            </div>
          )}

          {mfaEnabled && !mfaData && (
            <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
              <div style={{ padding: '12px', background: 'rgba(0,255,0,0.1)', color: 'var(--success)', borderRadius: '6px', marginBottom: '16px' }}>
                MFA is currently enabled on your account.
              </div>
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '24px' }}>
                <h4 style={{ marginBottom: '8px' }}>Disable MFA</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '12px' }}>Enter a code to disable.</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input type="text" placeholder="6-digit code" className="input-field" value={code} onChange={e => setCode(e.target.value)} />
                  <button className="btn btn-secondary" onClick={disableMfa} disabled={loading || !code}>Disable</button>
                </div>
              </div>
            </div>
          )}

          {mfaData && (
            <div>
              <div style={{ marginBottom: '24px' }}>
                <p style={{ marginBottom: '8px' }}><strong>1. Scan this URI or enter the secret in your authenticator app:</strong></p>
                <code style={{ display: 'block', padding: '12px', background: 'var(--background)', borderRadius: '6px', marginBottom: '16px', wordBreak: 'break-all' }}>
                  {mfaData.secret}
                </code>
              </div>
              <div>
                <p style={{ marginBottom: '8px' }}><strong>2. Verify your code:</strong></p>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input type="text" placeholder="6-digit code" className="input-field" value={code} onChange={e => setCode(e.target.value)} />
                  <button className="btn btn-primary" onClick={verifyMfa} disabled={loading || !code}>Verify</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
