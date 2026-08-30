/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';

export default async function ActivityPage() {
  let activityData: any;
  try {
    activityData = await fetchApi(apiClient.GET('/api/v1/activity/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    activityData = { items: [], total: 0, page: 1, size: 50 };
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Activity Logs</h1>
        <p className="page-subtitle">Complete audit trail of system events, API changes, and automated actions.</p>
      </div>
      
      {activityData.items.length > 0 ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Entity</th>
                <th>Result</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {activityData.items.map((log: any) => (
                <tr key={log.id}>
                  <td style={{ fontWeight: 500 }}>{log.event_type}</td>
                  <td className="text-mono" style={{ color: 'var(--text-muted)' }}>{log.actor}</td>
                  <td><span className="badge default">{log.entity}</span></td>
                  <td>
                    <span className={`badge ${log.result === 'SUCCESS' ? 'success' : log.result === 'FAILED' ? 'error' : 'default'}`}>
                      {log.result}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{log.created_at ? new Date(log.created_at).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
          <h2 className="empty-state-title">No activity logs</h2>
          <p className="empty-state-description">
            Audit logs will appear here when actions are performed in your organization.
          </p>
        </div>
      )}
    </>
  );
}
