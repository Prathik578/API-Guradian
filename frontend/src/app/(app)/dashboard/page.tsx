/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import Link from 'next/link';

export default async function DashboardPage() {
  let overview: any, guarded: any, changes: any, cases: any, notices: any, activity: any;
  
  try {
    const [oRes, gRes, chRes, caRes, nRes, aRes] = await Promise.all([
      fetchApi(apiClient.GET('/api/v1/analytics/overview' as any, {})),
      fetchApi(apiClient.GET('/api/v1/guarded-apis' as any, { params: { query: { page: 1, size: 5 } } })),
      fetchApi(apiClient.GET('/api/v1/api-changes' as any, { params: { query: { page: 1, size: 5 } } })),
      fetchApi(apiClient.GET('/api/v1/cases' as any, { params: { query: { page: 1, size: 5 } } })),
      fetchApi(apiClient.GET('/api/v1/notices' as any, { params: { query: { page: 1, size: 5 } } })),
      fetchApi(apiClient.GET('/api/v1/activity' as any, { params: { query: { page: 1, size: 5 } } }))
    ]);
    
    overview = oRes;
    guarded = gRes;
    changes = chRes;
    cases = caRes;
    notices = nRes;
    activity = aRes;
  } catch (err) {
    console.error(err);
    overview = { active_repositories: 0, active_cases: 0, pending_api_changes: 0, migrations_in_progress: 0, open_prs: 0, failed_verifications: 0, recent_notices: 0 };
    guarded = { items: [], total: 0 };
    changes = { items: [], total: 0 };
    cases = { items: [], total: 0 };
    notices = { items: [], total: 0 };
    activity = { items: [], total: 0 };
  }

  const hasData = overview.active_repositories > 0 || overview.active_cases > 0 || overview.pending_api_changes > 0 || guarded.total > 0;

  if (!hasData) {
    return (
      <>
        <div className="page-header" style={{ marginBottom: '24px' }}>
          <h1 className="page-title">API Guardian</h1>
          <p className="page-subtitle">Your API reliability control plane</p>
        </div>
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          <h2 className="empty-state-title">No APIs configured</h2>
          <p className="empty-state-description">
            Connect your GitHub repositories and start guarding API dependencies to see metrics and automated maintenance activity.
          </p>
          <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link href="/integrations" className="btn btn-primary">Connect Integrations</Link>
            <Link href="/apis" className="btn btn-secondary">Guard New API</Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title">API Guardian</h1>
        <p className="page-subtitle">Your API reliability control plane</p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Total Guarded APIs</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          </div>
          <div className="stat-value">{guarded.total}</div>
        </div>
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Active Repositories</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
          </div>
          <div className="stat-value">{overview.active_repositories}</div>
        </div>
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Pending API Changes</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          </div>
          <div className="stat-value" style={{ color: overview.pending_api_changes > 0 ? 'var(--warning)' : 'inherit' }}>{overview.pending_api_changes}</div>
        </div>
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Open Maintenance Cases</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          </div>
          <div className="stat-value" style={{ color: overview.active_cases > 0 ? 'var(--primary)' : 'inherit' }}>{overview.active_cases}</div>
        </div>
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Open GitHub PRs</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><line x1="6" y1="9" x2="6" y2="21"></line></svg>
          </div>
          <div className="stat-value">{overview.open_prs ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="flex-between">
            <div className="stat-title">Failed Verifications</div>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--text-muted)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
          </div>
          <div className="stat-value" style={{ color: overview.failed_verifications > 0 ? 'var(--error)' : 'inherit' }}>{overview.failed_verifications ?? 0}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '40px' }}>
        <div>
          <div className="flex-between" style={{ marginBottom: '16px' }}>
            <h2 className="section-title" style={{ margin: 0 }}>Active Maintenance Cases</h2>
            <Link href="/cases" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div className="table-container">
            {cases.items.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Repository</th>
                    <th>Change ID</th>
                    <th>State</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {cases.items.map((c: any) => (
                    <tr key={c.id}>
                      <td><Link href={`/cases/${c.id}`} style={{ fontWeight: 500, color: 'var(--primary)' }}>{c.repository_id.substring(0, 8)}...</Link></td>
                      <td className="text-mono">{c.provider_change_id.substring(0, 8)}</td>
                      <td>
                        <span className={`badge ${c.state === 'RESOLVED' ? 'success' : (c.state === 'FAILED' ? 'error' : 'warning')}`}>
                          {c.state}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-muted)' }}>{new Date(c.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No active maintenance cases.</div>
            )}
          </div>
          
          <div className="flex-between" style={{ marginBottom: '16px', marginTop: '32px' }}>
            <h2 className="section-title" style={{ margin: 0 }}>Recent API Changes</h2>
            <Link href="/api-changes" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div className="table-container">
            {changes.items.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Provider</th>
                    <th>API Name</th>
                    <th>Severity</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {changes.items.map((c: any) => (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 500 }}>{c.provider}</td>
                      <td><Link href={`/api-changes/${c.id}`}>{c.api_name}</Link></td>
                      <td>
                        <span className={`badge ${c.severity === 'CRITICAL' || c.severity === 'HIGH' ? 'error' : (c.severity === 'MEDIUM' ? 'warning' : 'default')}`}>
                          {c.severity}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${c.status === 'DETECTED' ? 'warning' : 'default'}`}>
                          {c.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No recent API changes.</div>
            )}
          </div>
        </div>
        
        <div>
          <div className="flex-between" style={{ marginBottom: '16px' }}>
            <h2 className="section-title" style={{ margin: 0 }}>Provider Notices</h2>
            <Link href="/notices" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '32px' }}>
            {notices.items.length > 0 ? (
              notices.items.map((n: any) => (
                <div key={n.id} className="card" style={{ padding: '16px' }}>
                  <div className="flex-between" style={{ marginBottom: '8px' }}>
                    <span className="badge default">{n.provider}</span>
                    <span className={`badge ${n.severity === 'CRITICAL' ? 'error' : 'warning'}`}>{n.severity}</span>
                  </div>
                  <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                    <Link href={`/notices/${n.id}`}>{n.title}</Link>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Effective: {n.effective_date ? new Date(n.effective_date).toLocaleDateString() : 'Unknown'}</div>
                </div>
              ))
            ) : (
              <div className="card" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No active provider notices.</div>
            )}
          </div>
          
          <div className="flex-between" style={{ marginBottom: '16px' }}>
            <h2 className="section-title" style={{ margin: 0 }}>Recent Activity</h2>
            <Link href="/activity" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div className="card" style={{ padding: '0' }}>
            {activity.items.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {activity.items.map((a: any, idx: number) => (
                  <div key={a.id} style={{ padding: '16px', borderBottom: idx < activity.items.length - 1 ? '1px solid var(--border)' : 'none' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)', marginTop: '6px', flexShrink: 0 }}></div>
                      <div>
                        <div style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '2px' }}>{a.action}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {a.actor_id} • {new Date(a.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No recent activity.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
