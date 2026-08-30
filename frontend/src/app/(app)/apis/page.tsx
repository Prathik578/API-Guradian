/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import AddGuardedAPIForm from './AddGuardedAPIForm';
import Link from 'next/link';

export default async function ApisPage() {
  let apisData;
  try {
    apisData = await fetchApi(apiClient.GET('/api/v1/apis/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    apisData = { items: [], total: 0, page: 1, size: 50 };
  }

  let integrationsData;
  try {
    integrationsData = await fetchApi(apiClient.GET('/api/v1/integrations/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    integrationsData = { items: [] };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Guarded APIs</h1>
          <p className="page-subtitle">Track the third-party APIs and libraries your organization depends on.</p>
        </div>
        <AddGuardedAPIForm integrations={integrationsData.items} />
      </div>
      
      {apisData.items.length > 0 ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>API Name</th>
                <th>Version</th>
                <th>Status</th>
                <th>Risk Level</th>
                <th>Connected At</th>
              </tr>
            </thead>
            <tbody>
              {apisData.items.map((api: any) => (
                <tr key={api.id}>
                  <td style={{ fontWeight: 500 }}>
                    <Link href={`/apis/${api.id}`}>{api.name}</Link>
                  </td>
                  <td className="text-mono">{api.version}</td>
                  <td>
                    <span className={`badge ${api.status === 'ACTIVE' ? 'success' : 'default'}`}>
                      {api.status}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${api.risk_level === 'HIGH' ? 'error' : api.risk_level === 'MEDIUM' ? 'warning' : 'success'}`}>
                      {api.risk_level}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{api.created_at ? new Date(api.created_at).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <h2 className="empty-state-title">No APIs Guarded</h2>
          <p className="empty-state-description">
            Register APIs you want API Guardian to monitor for breaking changes and deprecations.
          </p>
        </div>
      )}
    </>
  );
}
