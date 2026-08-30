'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';

export default function IntegrationCard({ integration }: { integration: any }) {
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch(`/api/v1/integrations/${integration.id}/sync`, { method: 'POST' });
      if (res.ok) {
        alert('Sync triggered successfully! Check Activity or Dashboard shortly.');
      } else {
        alert('Failed to trigger sync');
      }
    } catch (err) {
      console.error(err);
      alert('Error triggering sync');
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '12px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{integration.provider}</h3>
        <span className={`badge ${integration.status === 'CONNECTED' ? 'success' : 'default'}`}>{integration.status}</span>
      </div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '24px' }}>
        Last synced: {integration.last_synced_at ? new Date(integration.last_synced_at).toLocaleString() : 'Never'}
      </div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <button className="btn btn-secondary" style={{ flex: 1 }}>Configure</button>
        <button onClick={handleSync} disabled={isSyncing} className="btn btn-primary" style={{ flex: 1 }}>
          {isSyncing ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>
    </div>
  );
}
