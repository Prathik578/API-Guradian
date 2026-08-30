/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import Link from 'next/link';

export default async function NoticesPage() {
  let noticesData;
  try {
    noticesData = await fetchApi(apiClient.GET('/api/v1/notices/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    noticesData = { items: [], total: 0, page: 1, size: 50 };
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Provider Notices</h1>
        <p className="page-subtitle">Announcements, sunsets, and breaking change notices from your API providers.</p>
      </div>
      
      {noticesData.items.length > 0 ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Title</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Effective At</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {noticesData.items.map((n: any) => (
                <tr key={n.id}>
                  <td style={{ fontWeight: 500 }}>{n.provider}</td>
                  <td style={{ fontWeight: 500 }}>
                    <Link href={`/notices/${n.id}`}>{n.title}</Link>
                  </td>
                  <td><span className="badge default">{n.notice_type}</span></td>
                  <td><span className={`badge ${n.severity === 'CRITICAL' ? 'error' : n.severity === 'WARNING' ? 'warning' : 'default'}`}>{n.severity}</span></td>
                  <td style={{ color: 'var(--text-muted)' }}>{n.effective_at ? new Date(n.effective_at).toLocaleDateString() : 'TBD'}</td>
                  <td><span className={`badge ${n.status === 'ACTION_REQUIRED' ? 'error' : n.status === 'RESOLVED' ? 'success' : 'default'}`}>{n.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path>
          </svg>
          <h2 className="empty-state-title">No provider notices</h2>
          <p className="empty-state-description">
            API Guardian continuously monitors your configured providers. Any important announcements or deprecation notices will appear here.
          </p>
        </div>
      )}
    </>
  );
}
