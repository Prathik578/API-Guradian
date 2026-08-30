'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { onboardAction } from '../actions/auth';

export default function OnboardingPage() {
  const [accountType, setAccountType] = useState('PERSONAL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleOnboard = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    const formData = new FormData(e.currentTarget);
    formData.set('accountType', accountType);

    try {
      const result = await onboardAction(null, formData);
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
      <div style={{ padding: '48px', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', width: '100%', maxWidth: '500px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>Welcome to API Guardian</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>How will you be using API Guardian?</p>
        
        {error && (
          <div style={{ padding: '12px', marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error, #ef4444)', borderRadius: '6px', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleOnboard}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div 
              style={{
                border: `2px solid ${accountType === 'PERSONAL' ? 'var(--primary)' : 'var(--border)'}`,
                borderRadius: '8px', padding: '16px', cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px'
              }}
              onClick={() => setAccountType('PERSONAL')}
            >
              <div style={{ fontWeight: 600 }}>Personal</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Free for individual developers and personal projects.</div>
            </div>
            <div 
              style={{
                border: `2px solid ${accountType === 'ENTERPRISE' ? 'var(--primary)' : 'var(--border)'}`,
                borderRadius: '8px', padding: '16px', cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px'
              }}
              onClick={() => setAccountType('ENTERPRISE')}
            >
              <div style={{ fontWeight: 600 }}>Enterprise</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>7-day free trial. For teams managing production APIs.</div>
            </div>
          </div>
          
          <div style={{ marginBottom: '32px' }}>
            <label htmlFor="orgName" style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem', fontWeight: 500 }}>
              {accountType === 'ENTERPRISE' ? 'Organization Name' : 'Project/Workspace Name'}
            </label>
            <input 
              id="orgName"
              name="orgName"
              type="text" 
              required
              className="input-field"
              style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}
              placeholder={accountType === 'ENTERPRISE' ? 'Acme Corp' : 'My Project'}
            />
          </div>
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', cursor: loading ? 'not-allowed' : 'pointer' }} disabled={loading}>
            {loading ? 'Creating...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}
