/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';
import { apiClient, fetchApi } from '@/api/client';
import CaseActions from './CaseActions';
import type { components } from '@/api/schema';

type MigrationResponse = components["schemas"]["MigrationAttemptResponse"];
type VerificationResponse = components["schemas"]["VerificationRunResponse"];

export default async function CaseDetailPage({ params }: { params: { case_id: string } }) {
  const caseId = params.case_id;

  let caseDetail = null;
  let migrations: MigrationResponse[] = [];
  let verifications: VerificationResponse[] = [];

  try {
    caseDetail = await fetchApi(apiClient.GET('/api/v1/cases/{case_id}', { params: { path: { case_id: caseId } } }));
    migrations = await fetchApi(apiClient.GET('/api/v1/cases/{case_id}/migrations', { params: { path: { case_id: caseId } } }));
    verifications = await fetchApi(apiClient.GET('/api/v1/cases/{case_id}/verifications', { params: { path: { case_id: caseId } } }));
  } catch (err) {
    console.error(err);
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
      case 'SUCCESS':
      case 'PASSED':
        return 'success';
      case 'ACTION_REQUIRED':
      case 'FAILED':
        return 'error';
      default:
        return 'default';
    }
  };

  if (!caseDetail) {
    return (
      <div className="empty-state">
        <h2 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Case not found or API error</h2>
        <Link href="/cases" className="btn btn-secondary" style={{ marginTop: '16px' }}>Back to Cases</Link>
      </div>
    );
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Case {caseDetail.id.substring(0, 8)}</h1>
          <p className="page-subtitle">Repository: {caseDetail.repository_id}</p>
        </div>
        <span className={`badge ${getBadgeClass(caseDetail.state)}`} style={{ fontSize: '1rem', padding: '6px 12px' }}>
          {caseDetail.state}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <div className="card">
          <h3 style={{ marginBottom: '16px', fontSize: '1.25rem', fontWeight: 600 }}>Details</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.875rem' }}>
            <div><span style={{ color: 'var(--text-muted)' }}>Provider Change ID:</span> {caseDetail.provider_change_id}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Base Revision SHA:</span> <code className="text-mono">{caseDetail.base_revision_sha}</code></div>
            <div><span style={{ color: 'var(--text-muted)' }}>Created At:</span> {caseDetail.created_at ? new Date(caseDetail.created_at).toLocaleString() : 'N/A'}</div>
          </div>
          <div style={{ marginTop: '24px' }}>
            <CaseActions caseId={caseId} currentState={caseDetail.state} />
          </div>
        </div>
      </div>

      <h3 style={{ marginBottom: '16px', fontSize: '1.25rem', fontWeight: 600 }}>Migration Attempts</h3>
      {migrations.length === 0 ? (
        <div className="empty-state" style={{ marginBottom: '32px' }}>
          <p>No migration attempts found.</p>
        </div>
      ) : (
        <div className="table-container" style={{ marginBottom: '32px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Model Name</th>
                <th>Error Reason</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {migrations.map((m) => (
                <tr key={m.id}>
                  <td className="text-mono">{m.id.substring(0, 8)}...</td>
                  <td>{m.model_name}</td>
                  <td style={{ color: 'var(--error)' }}>{m.error_reason || '-'}</td>
                  <td>{m.created_at ? new Date(m.created_at).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h3 style={{ marginBottom: '16px', fontSize: '1.25rem', fontWeight: 600 }}>Verification Runs</h3>
      {verifications.length === 0 ? (
        <div className="empty-state">
          <p>No verification runs found.</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>State</th>
                <th>Audit Result</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {verifications.map((v) => (
                <tr key={v.id}>
                  <td className="text-mono">{v.id.substring(0, 8)}...</td>
                  <td>
                    <span className={`badge ${getBadgeClass(v.state)}`}>
                      {v.state}
                    </span>
                  </td>
                  <td>
                    {v.audit_passed === true && <span className="badge success">PASSED</span>}
                    {v.audit_passed === false && <span className="badge error">FAILED</span>}
                    {v.audit_passed === null && <span className="badge default">PENDING</span>}
                  </td>
                  <td>{v.created_at ? new Date(v.created_at).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
