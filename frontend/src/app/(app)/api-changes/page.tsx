/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import Link from 'next/link';

export default async function ApiChangesPage() {
  let changesData;
  try {
    changesData = await fetchApi(apiClient.GET('/api/v1/provider-changes/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    changesData = { items: [], total: 0, page: 1, size: 50 };
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">API Changes</h1>
        <p className="page-subtitle">Track breaking changes and deprecations across all monitored APIs.</p>
      </div>
      
      {changesData.items.length > 0 ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Classification</th>
                <th>Summary</th>
                <th>Effective Date</th>
                <th>Sunset Date</th>
              </tr>
            </thead>
            <tbody>
              {changesData.items.map((change: any) => (
                <tr key={change.id}>
                  <td style={{ fontWeight: 500 }}>
                    <Link href={`/api-changes/${change.id}`}>{change.provider}</Link>
                  </td>
                  <td>
                    <span className={`badge ${change.classification === 'BREAKING' ? 'error' : 'warning'}`}>
                      {change.classification}
                    </span>
                  </td>
                  <td>{change.summary}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{change.effective_date ? new Date(change.effective_date).toLocaleDateString() : 'TBD'}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{change.sunset_date ? new Date(change.sunset_date).toLocaleDateString() : 'TBD'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          <h2 className="empty-state-title">No API changes detected</h2>
          <p className="empty-state-description">
            API Guardian continuously monitors your configured providers. Any breaking changes will appear here.
          </p>
        </div>
      )}
    </>
  );
}
