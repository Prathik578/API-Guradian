
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';

export default async function UsagePage() {
  let usage = null;
  try {
    usage = await fetchApi(apiClient.GET('/api/v1/usage/'));
  } catch (err) {
    console.error(err);
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Usage & Quotas</h1>
        <p className="page-subtitle">Monitor your API Guardian usage against your plan limits.</p>
      </div>
      
      {usage ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '24px' }}>
          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Repositories Monitored</div>
            <div style={{ fontSize: '2rem', fontWeight: 600, display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              {usage.repositories_monitored} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {usage.repositories_limit}</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: 'var(--background)', borderRadius: '4px', marginTop: '16px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, (usage.repositories_monitored / usage.repositories_limit) * 100)}%`, height: '100%', background: 'var(--primary)' }}></div>
            </div>
          </div>

          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Guarded APIs</div>
            <div style={{ fontSize: '2rem', fontWeight: 600, display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              {usage.guarded_apis} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {usage.guarded_apis_limit}</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: 'var(--background)', borderRadius: '4px', marginTop: '16px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, (usage.guarded_apis / usage.guarded_apis_limit) * 100)}%`, height: '100%', background: 'var(--primary)' }}></div>
            </div>
          </div>

          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Provider Changes Detected</div>
            <div style={{ fontSize: '2rem', fontWeight: 600 }}>{usage.api_changes_detected}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '16px' }}>Unlimited on all plans</div>
          </div>

          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Maintenance Cases</div>
            <div style={{ fontSize: '2rem', fontWeight: 600 }}>{usage.maintenance_cases}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '16px' }}>Unlimited on all plans</div>
          </div>

          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Migration Attempts</div>
            <div style={{ fontSize: '2rem', fontWeight: 600 }}>{usage.migration_attempts}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '16px' }}>Metered based on AI usage</div>
          </div>

          <div className="card">
            <div style={{ color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 500 }}>Verification Runs</div>
            <div style={{ fontSize: '2rem', fontWeight: 600 }}>{usage.verification_runs}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '16px' }}>Metered based on compute</div>
          </div>
        </div>
      ) : (
        <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>Could not load usage data</div>
      )}
    </>
  );
}
