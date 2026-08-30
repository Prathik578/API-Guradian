'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/api/client';

export default function CaseActions({ caseId, currentState }: { caseId: string, currentState: string }) {
  const [loading, setLoading] = useState<string | null>(null);
  const router = useRouter();

  const handleAction = async (action: 'assess_impact' | 'generate_migration' | 'verify') => {
    setLoading(action);
    try {
      let res;
      if (action === 'assess_impact') {
        res = await apiClient.POST('/api/v1/cases/{case_id}/assess_impact', { params: { path: { case_id: caseId } } });
      } else if (action === 'generate_migration') {
        res = await apiClient.POST('/api/v1/cases/{case_id}/generate_migration', { params: { path: { case_id: caseId } } });
      } else if (action === 'verify') {
        res = await apiClient.POST('/api/v1/cases/{case_id}/verify', { params: { path: { case_id: caseId } } });
      }
      
      if (res?.error) {
        alert(`Error: ${res.error.detail || 'Unknown error'}`);
      } else {
        // Wait a bit to let outbox process and refresh
        setTimeout(() => {
          router.refresh();
          setLoading(null);
        }, 1000);
        return; // Don't unset loading immediately, wait for refresh
      }
    } catch (err: any) {
      alert(`Request failed: ${(err as Error).message}`);
    }
    setLoading(null);
  };

  return (
    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
      <button 
        className="btn btn-secondary" 
        onClick={() => handleAction('assess_impact')}
        disabled={loading !== null || (currentState !== 'DETECTED' && currentState !== 'STALE')}
      >
        {loading === 'assess_impact' ? 'Triggering...' : 'Assess Impact'}
      </button>
      <button 
        className="btn btn-primary" 
        onClick={() => handleAction('generate_migration')}
        disabled={loading !== null || (currentState !== 'ACTION_REQUIRED' && currentState !== 'FAILED')}
      >
        {loading === 'generate_migration' ? 'Triggering...' : 'Generate Migration'}
      </button>
      <button 
        className="btn btn-secondary" 
        onClick={() => handleAction('verify')}
        disabled={loading !== null}
      >
        {loading === 'verify' ? 'Triggering...' : 'Verify Patch'}
      </button>
    </div>
  );
}
