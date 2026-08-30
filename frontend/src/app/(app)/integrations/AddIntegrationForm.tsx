'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AddIntegrationForm() {
  const [isAdding, setIsAdding] = useState(false);
  const [provider, setProvider] = useState('');
  const router = useRouter();

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!provider) return;
    
    try {
      const res = await fetch('/api/v1/integrations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, configuration: {} })
      });
      if (res.ok) {
        setProvider('');
        setIsAdding(false);
        router.refresh();
      } else {
        alert('Failed to add integration');
      }
    } catch (err) {
      console.error(err);
      alert('Error adding integration');
    }
  };

  if (!isAdding) {
    return (
      <div 
        onClick={() => setIsAdding(true)}
        style={{ border: '1px dashed var(--border)', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '200px', cursor: 'pointer', background: 'var(--surface)' }} 
        className="nav-item">
        <span style={{ fontSize: '2rem', marginBottom: '16px' }}>+</span>
        <span style={{ fontWeight: 500 }}>Add Integration</span>
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: '12px', padding: '24px', background: 'var(--surface)' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>New Integration</h3>
      
      <div style={{ marginBottom: '24px' }}>
        <button 
          onClick={async () => {
            try {
              const res = await fetch('/api/v1/integrations/github/oauth/login');
              const data = await res.json();
              if (res.ok && data.url) {
                window.location.href = data.url;
              } else {
                alert(data.detail || 'Failed to initialize GitHub OAuth');
              }
            } catch (err) {
              console.error(err);
              alert('Error connecting to GitHub');
            }
          }}
          className="btn btn-primary" 
          style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', padding: '12px', background: '#24292e', color: 'white' }}
        >
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
          </svg>
          Connect GitHub
        </button>
      </div>

      <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.875rem' }}>OR ADD MANUALLY</div>

      <form onSubmit={handleAdd}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>Provider Name (e.g. Stripe)</label>
          <input 
            type="text" 
            value={provider} 
            onChange={(e) => setProvider(e.target.value)} 
            className="input-field" 
            required 
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} 
          />
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button type="submit" className="btn btn-secondary" style={{ flex: 1 }}>Add Custom</button>
          <button type="button" onClick={() => setIsAdding(false)} className="btn btn-secondary" style={{ flex: 1 }}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
