/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';
import { apiClient, fetchApi } from '@/api/client';

export default async function ApiDetailsPage({ params }: { params: { api_id: string } }) {
  // Mocking details for MVP, as backend detail endpoint for API is not strictly defined yet.
  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Stripe PaymentIntent API</h1>
          <p className="page-subtitle">Provider: Stripe | Version: v1 | Risk Level: <span className="badge warning">MEDIUM</span></p>
        </div>
        <button className="btn btn-primary">Refresh Analysis</button>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Dependency Impact</h2>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Affected Repositories</span>
              <span style={{ fontWeight: 500 }}>3</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Total Call Sites</span>
              <span style={{ fontWeight: 500 }}>14</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Open Maintenance Cases</span>
              <span style={{ fontWeight: 500 }}>1</span>
            </li>
          </ul>
        </section>
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Recent Changes</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            <div style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 500, color: 'var(--foreground)' }}>Deprecation: Charge.create()</div>
              <div>Sunset scheduled for 2026-12-01. Replacement: PaymentIntent.create()</div>
            </div>
          </div>
        </section>
      </div>

      <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '16px' }}>Affected Repositories</h2>
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Repository</th>
              <th>Call Sites</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontWeight: 500 }}>backend-monorepo</td>
              <td>7</td>
              <td><span className="badge warning">Needs Migration</span></td>
              <td><Link href="/cases" className="btn btn-secondary btn-sm">View Case</Link></td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}
