'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */


import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AddRepositoryForm() {
  const [isAdding, setIsAdding] = useState(false);
  const [name, setName] = useState('');
  const [githubFullName, setGithubFullName] = useState('');
  const [defaultBranch, setDefaultBranch] = useState('main');
  const router = useRouter();

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const res = await fetch('/api/v1/repositories/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, github_full_name: githubFullName, default_branch: defaultBranch })
      });
      if (res.ok) {
        setIsAdding(false);
        setName('');
        setGithubFullName('');
        setDefaultBranch('main');
        router.refresh();
      } else {
        alert('Failed to add repository');
      }
    } catch (err) {
      console.error(err);
      alert('Error adding repository');
    }
  };

  if (!isAdding) {
    return (
      <button className="btn btn-primary" onClick={() => setIsAdding(true)}>Connect Repository</button>
    );
  }

  return (
    <div style={{ padding: '24px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '12px', marginBottom: '24px' }}>
      <h3 style={{ marginBottom: '16px' }}>Connect Repository</h3>
      <form onSubmit={handleAdd} style={{ display: 'grid', gap: '16px', maxWidth: '400px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>Repository Name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>GitHub Full Name (org/repo)</label>
          <input type="text" value={githubFullName} onChange={(e) => setGithubFullName(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem' }}>Default Branch</label>
          <input type="text" value={defaultBranch} onChange={(e) => setDefaultBranch(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)' }} />
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button type="submit" className="btn btn-primary">Save</button>
          <button type="button" onClick={() => setIsAdding(false)} className="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  );
}
