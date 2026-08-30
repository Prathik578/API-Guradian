'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signupAction } from '../actions/auth';

export default function SignupPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    const formData = new FormData(e.currentTarget);
    
    try {
      const result = await signupAction(null, formData);
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

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--background)' }}>
      <div style={{ padding: '48px', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>Create an Account</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Start managing your API dependencies today.</p>
        
        {error && (
          <div style={{ padding: '12px', marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error, #ef4444)', borderRadius: '6px', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="name" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Full Name</label>
            <input
              id="name"
              name="name"
              type="text"
              placeholder="Jane Doe"
              className="input-field"
              style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
              required
            />
          </div>
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="password" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Password</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="••••••••"
              className="input-field"
              style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
              required
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '8px' }}>
            <label htmlFor="confirmPassword" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="••••••••"
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
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <div style={{ marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link href="/login" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Log in</Link>
        </div>
      </div>
    </div>
  );
}
