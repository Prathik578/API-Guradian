'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';
import { useState } from 'react';
import { apiClient } from '../../api/client';

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const res = await apiClient.POST('/api/v1/auth/forgot-password', {
        body: { email }
      });
      
      if (res.error) {
        const errorDetail = res.error?.detail;
        const errorMessage = Array.isArray(errorDetail) 
          ? errorDetail.map((err: any) => err.msg).join(', ') 
          : (typeof errorDetail === 'string' ? errorDetail : 'Failed to request reset');
        throw new Error(errorMessage);
      }
      
      setSuccess('If an account exists, a reset link has been sent.');
    } catch (err: any) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px', textAlign: 'center', padding: '48px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>Reset Password</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Enter your email to receive a password reset link.</p>
        
        {error && <div style={{ padding: '12px', background: 'rgba(255,0,0,0.1)', color: 'var(--error)', borderRadius: '6px', marginBottom: '16px' }}>{error}</div>}
        {success && <div style={{ padding: '12px', background: 'rgba(0,255,0,0.1)', color: 'var(--success)', borderRadius: '6px', marginBottom: '16px' }}>{success}</div>}

        <form onSubmit={handleReset} style={{ display: 'flex', flexDirection: 'column', gap: '16px', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 500 }}>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="input-field"
              required
            />
          </div>
          
          <button 
            type="submit"
            className="btn btn-primary" 
            style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '8px' }}
            disabled={loading || !email}
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
        
        <div style={{ marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          <Link href="/login" style={{ color: 'var(--primary)' }}>Back to login</Link>
        </div>
      </div>
    </div>
  );
}
