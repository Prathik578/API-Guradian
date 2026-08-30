/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';
import { apiClient, fetchApi } from '@/api/client';

export default async function CasesPage() {
  let casesData;
  try {
    casesData = await fetchApi(apiClient.GET('/api/v1/cases/', {
      params: { query: { page: 1, size: 20 } }
    }));
  } catch (err) {
    console.error(err);
    casesData = { items: [], total: 0, page: 1, size: 20 };
  }

  const getBadgeClass = (state: string) => {
    switch(state) {
      case 'DETECTED':
      case 'ANALYZING':
        return 'warning';
      case 'MIGRATING':
      case 'VERIFYING':
        return 'primary';
      case 'RESOLVED':
        return 'success';
      case 'ACTION_REQUIRED':
      case 'FAILED':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Maintenance Cases</h1>
        <p className="page-subtitle">Track and manage API maintenance lifecycle events across your repositories.</p>
      </div>
      
      {casesData.items.length > 0 ? (
        <>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Repository ID</th>
                  <th>Change ID</th>
                  <th>State</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {casesData.items.map((c: any) => (
                  <tr key={c.id}>
                    <td className="text-mono" style={{ fontWeight: 500 }}>
                      <Link href={`/cases/${c.id}`}>{c.id.substring(0, 8)}</Link>
                    </td>
                    <td className="text-mono">{c.repository_id.substring(0, 8)}</td>
                    <td className="text-mono">{c.provider_change_id.substring(0, 8)}</td>
                    <td>
                      <span className={`badge ${getBadgeClass(c.state)}`}>
                        {c.state}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>{c.created_at ? new Date(c.created_at).toLocaleString() : 'N/A'}</td>
                    <td>
                      <Link href={`/cases/${c.id}`} className="btn btn-sm btn-secondary">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            <span>Showing {casesData.items.length} of {casesData.total} cases</span>
            <span>Page {casesData.page}</span>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <h2 className="empty-state-title">No maintenance cases</h2>
          <p className="empty-state-description">
            When an API change impacts your repositories, a maintenance case will be opened automatically to coordinate the migration and verification process.
          </p>
        </div>
      )}
    </>
  );
}
