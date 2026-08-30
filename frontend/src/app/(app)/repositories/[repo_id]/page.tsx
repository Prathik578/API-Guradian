/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';

export default async function RepositoryDetailsPage({ params }: { params: { repo_id: string } }) {
  let repo: any;
  try {
    repo = await fetchApi(apiClient.GET('/api/v1/repositories/{repo_id}' as any, {
      params: { path: { repo_id: params.repo_id } }
    }));
  } catch (err) {
    console.error(err);
    repo = { id: params.repo_id, name: 'Unknown Repo', github_full_name: 'unknown/repo', default_branch: 'main' };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">{repo.name}</h1>
          <p className="page-subtitle">GitHub: <span className="text-mono">{repo.github_full_name}</span></p>
        </div>
        <span className="badge default" style={{ fontSize: '1rem', padding: '8px 16px' }}>
          Branch: {repo.default_branch}
        </span>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Repository Status</h2>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Guarded APIs Detected</span>
              <span style={{ fontWeight: 500 }}>12</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Open Maintenance Cases</span>
              <span style={{ fontWeight: 500, color: 'var(--warning)' }}>2</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Pending Pull Requests</span>
              <span style={{ fontWeight: 500, color: 'var(--primary)' }}>1</span>
            </li>
          </ul>
        </section>
        
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Recent Activity</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            <div style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 500, color: 'var(--foreground)' }}>Snapshot Generated</div>
              <div>Analyzed 124 files on branch <code className="text-mono">{repo.default_branch}</code></div>
            </div>
            <div style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 500, color: 'var(--foreground)' }}>Maintenance Case Opened</div>
              <div>Impact identified for Stripe API deprecation</div>
            </div>
          </div>
        </section>
      </div>

      <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '16px' }}>Maintenance Cases</h2>
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Provider Change</th>
              <th>State</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                No open maintenance cases.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}
