/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';

export default async function ChangeDetailsPage({ params }: { params: { change_id: string } }) {
  let change: any;
  try {
    change = await fetchApi(apiClient.GET('/api/v1/provider-changes/{change_id}', {
      params: { path: { change_id: params.change_id } }
    }));
  } catch (err) {
    console.error(err);
    change = { id: params.change_id, provider: 'Unknown', summary: 'Failed to load change details' };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">{change.provider} API Change</h1>
          <p className="page-subtitle">{change.summary}</p>
        </div>
        <span className={`badge ${change.classification === 'BREAKING' ? 'error' : 'warning'}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
          {change.classification || 'UNKNOWN'}
        </span>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px', marginBottom: '32px' }}>
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>What needs replacement?</h2>
          
          <div style={{ background: 'var(--background)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
            <div style={{ display: 'flex', borderBottom: '1px solid var(--border)' }}>
              <div style={{ flex: 1, padding: '16px', background: 'rgba(255, 68, 68, 0.05)', borderRight: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--error)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Deprecated Usage</div>
                <pre style={{ margin: 0, fontSize: '0.875rem', color: 'var(--foreground)' }} className="text-mono"><code>stripe.charges.create(&#123;
  amount: 2000,
  currency: 'usd',
  source: 'tok_visa'
&#125;)</code></pre>
              </div>
              <div style={{ flex: 1, padding: '16px', background: 'rgba(0, 200, 83, 0.05)' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--success)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Recommended Replacement</div>
                <pre style={{ margin: 0, fontSize: '0.875rem', color: 'var(--foreground)' }} className="text-mono"><code>stripe.paymentIntents.create(&#123;
  amount: 2000,
  currency: 'usd',
  payment_method: 'pm_card_visa'
&#125;)</code></pre>
              </div>
            </div>
            <div style={{ padding: '16px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              Confidence Level: <strong style={{ color: 'var(--foreground)' }}>High</strong>. The Charge.create endpoint is deprecated and will be removed. All implementations should migrate to PaymentIntents.
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
              <th>Affected Files</th>
              <th>Migration Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                No repositories identified yet. Running impact analysis...
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}
