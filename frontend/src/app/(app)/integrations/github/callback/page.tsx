'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient, fetchApi } from '@/api/client';

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!code || !state) {
      setTimeout(() => setError('Invalid callback URL: missing code or state.'), 0);
      return;
    }

    const completeAuth = async () => {
      try {
        await fetchApi(apiClient.GET('/api/v1/integrations/github/oauth/callback' as any, {
          params: { query: { code, state } as any }
        }));
        
        router.push('/integrations');
      } catch (err: any) {
        setError(err.message || 'Failed to complete OAuth setup.');
      }
    };

    completeAuth();
  }, [code, state, router]);

  if (error) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '48px', maxWidth: '500px', width: '100%' }}>
        <h2 style={{ color: 'var(--error)', marginBottom: '16px' }}>OAuth Error</h2>
        <p style={{ marginBottom: '24px' }}>{error}</p>
        <button className="btn btn-primary" onClick={() => router.push('/integrations')}>Back to Integrations</button>
      </div>
    );
  }

  return (
    <div className="card" style={{ textAlign: 'center', padding: '48px', maxWidth: '500px', width: '100%' }}>
      <h2 style={{ marginBottom: '16px' }}>Connecting to GitHub...</h2>
      <p style={{ color: 'var(--text-muted)' }}>Please wait while we complete the integration.</p>
    </div>
  );
}

export default function GitHubCallbackPage() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <Suspense fallback={<div>Loading...</div>}>
        <CallbackHandler />
      </Suspense>
    </div>
  );
}
