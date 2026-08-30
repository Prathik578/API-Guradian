'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { loginAction, verifyMfaLoginAction } from '../actions/auth';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    const formData = new FormData(e.currentTarget);
    
    try {
      const result = await loginAction(null, formData);
      if (result?.error) {
        setError(result.error);
        setLoading(false);
      } else if (result?.success && result.mfaRequired && result.mfaToken) {
        setMfaToken(result.mfaToken);
        setLoading(false);
      } else if (result?.success && result.redirectUrl) {
        router.push(result.redirectUrl);
      }
    } catch (err: any) {
      setError(`Error: ${(err as Error).message}`);
      setLoading(false);
    }
  };

  const handleMfaVerify = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    if (mfaToken) {
      formData.append('mfaToken', mfaToken);
    }

    try {
      const result = await verifyMfaLoginAction(null, formData);
      if (result?.error) {
        setError(result.error);
        setLoading(false);
      } else if (result?.success && result.redirectUrl) {
        router.push(result.redirectUrl);
      }
    } catch (err: any) {
      setError(`Error: ${(err as Error).message}`);
      setLoading(false);
    }
  };

  if (mfaToken) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--background)' }}>
        <div style={{ padding: '48px', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', width: '100%', maxWidth: '400px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>Two-Factor Authentication</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Enter the code from your authenticator app.</p>
          
          {error && (
            <div style={{ padding: '12px', marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error, #ef4444)', borderRadius: '6px', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}
          
          <form onSubmit={handleMfaVerify} style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label htmlFor="code" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Authentication Code</label>
              <input
                id="code"
                name="code"
                type="text"
                placeholder="6-digit code"
                className="input-field"
                style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
                required
              />
            </div>
            <button 
              type="submit"
              className="btn btn-primary" 
              style={{ width: '100%', padding: '12px', display: 'flex', justifyContent: 'center', gap: '8px', cursor: loading ? 'not-allowed' : 'pointer' }}
              disabled={loading}
            >
              {loading ? 'Verifying...' : 'Verify'}
            </button>
            <button 
              type="button"
              className="btn btn-secondary" 
              style={{ width: '100%', padding: '12px', display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '8px', cursor: loading ? 'not-allowed' : 'pointer' }}
              disabled={loading}
              onClick={() => setMfaToken(null)}
            >
              Cancel
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--background)' }}>
      <div style={{ padding: '48px', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>API Guardian</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Sign in to manage your API dependencies</p>
        
        {error && (
          <div style={{ padding: '12px', marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error, #ef4444)', borderRadius: '6px', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="email" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="you@example.com"
              className="input-field"
              style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
              required
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="password" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Password</label>
              <Link href="/forgot-password" style={{ fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none' }}>Forgot password?</Link>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="input-field"
                style={{ width: '100%', padding: '12px', paddingRight: '48px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)'
                }}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          <button 
            type="submit"
            className="btn btn-primary" 
            style={{ width: '100%', padding: '12px', display: 'flex', justifyContent: 'center', gap: '8px', cursor: loading ? 'not-allowed' : 'pointer' }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <div style={{ marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Don&apos;t have an account? <Link href="/signup" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Sign up</Link>
        </div>
      </div>
    </div>
  );
}
