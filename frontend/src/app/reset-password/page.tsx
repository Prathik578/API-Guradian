'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';
import { useState } from 'react';
import { apiClient } from '../../api/client';
import { useRouter } from 'next/navigation';

export default function ResetPasswordPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const [token, setToken] = useState('mock-token-123'); // Usually from URL query params
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const res = await apiClient.POST('/api/v1/auth/reset-password', {
        body: { token, new_password: password, confirm_password: confirmPassword }
      });
      
      if (res.error) {
        const errorDetail = res.error?.detail;
        const errorMessage = Array.isArray(errorDetail) 
          ? errorDetail.map((err: any) => err.msg).join(', ') 
          : (typeof errorDetail === 'string' ? errorDetail : 'Failed to reset password');
        throw new Error(errorMessage);
      }
      
      setSuccess('Password reset successfully! You can now log in.');
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } catch (err: any) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px', textAlign: 'center', padding: '48px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>Create New Password</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Enter your new password below.</p>
        
        {error && <div style={{ padding: '12px', background: 'rgba(255,0,0,0.1)', color: 'var(--error)', borderRadius: '6px', marginBottom: '16px' }}>{error}</div>}
        {success && <div style={{ padding: '12px', background: 'rgba(0,255,0,0.1)', color: 'var(--success)', borderRadius: '6px', marginBottom: '16px' }}>{success}</div>}

        <form onSubmit={handleReset} style={{ display: 'flex', flexDirection: 'column', gap: '16px', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 500 }}>New Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="input-field"
              required
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 500 }}>Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              className="input-field"
              required
            />
          </div>
          
          <button 
            type="submit"
            className="btn btn-primary" 
            style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '8px' }}
            disabled={loading || !password || !confirmPassword}
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
        
        <div style={{ marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          <Link href="/login" style={{ color: 'var(--primary)' }}>Back to login</Link>
        </div>
      </div>
    </div>
  );
}
