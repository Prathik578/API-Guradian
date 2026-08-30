'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AddGuardedAPIForm({ integrations }: { integrations: any[] }) {
  const [isAdding, setIsAdding] = useState(false);
  const [integrationId, setIntegrationId] = useState('');
  const [name, setName] = useState('');
  const [version, setVersion] = useState('');
  const router = useRouter();

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!integrationId) return alert('Select an integration');
    
    try {
      const res = await fetch('/api/v1/apis/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ integration_id: integrationId, name, version, risk_level: 'LOW' })
      });
      if (res.ok) {
        setIsAdding(false);
        setIntegrationId('');
        setName('');
        setVersion('');
        router.refresh();
      } else {
        alert('Failed to add Guarded API');
      }
    } catch (err) {
      console.error(err);
      alert('Error adding Guarded API');
    }
  };

  if (!isAdding) {
    return (
      <button className="btn btn-primary" onClick={() => setIsAdding(true)}>Add Guarded API</button>
    );
  }

  return (
    <div style={{ padding: '24px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '12px', marginBottom: '24px' }}>
      <h3 style={{ marginBottom: '16px' }}>Add Guarded API</h3>
      <form onSubmit={handleAdd} style={{ display: 'grid', gap: '16px', maxWidth: '400px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>Integration</label>
          <select value={integrationId} onChange={(e) => setIntegrationId(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--foreground)' }}>
            <option value="">Select an integration...</option>
            {integrations.map((i) => (
              <option key={i.id} value={i.id}>{i.provider}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>API Name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>Version</label>
          <input type="text" value={version} onChange={(e) => setVersion(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} />
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button type="submit" className="btn btn-primary">Save</button>
          <button type="button" onClick={() => setIsAdding(false)} className="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  );
}
