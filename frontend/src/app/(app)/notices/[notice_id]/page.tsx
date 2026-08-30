/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';
import { apiClient, fetchApi } from '@/api/client';

export default async function NoticeDetailsPage({ params }: { params: { notice_id: string } }) {
  let notice: any;
  try {
    notice = await fetchApi(apiClient.GET('/api/v1/notices/{notice_id}' as any, {
      params: { path: { notice_id: params.notice_id } }
    }));
  } catch (err) {
    console.error(err);
    notice = { id: params.notice_id, provider: 'Unknown', title: 'Failed to load notice details', severity: 'INFO' };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">{notice.title}</h1>
          <p className="page-subtitle">Provider: {notice.provider}</p>
        </div>
        <span className={`badge ${notice.severity === 'CRITICAL' ? 'error' : notice.severity === 'WARNING' ? 'warning' : 'default'}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
          {notice.severity || 'INFO'}
        </span>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <section className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Notice Details</h2>
          <p style={{ color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '24px' }}>
            {notice.description || "Detailed description of the provider notice. This usually includes deprecation timelines, migration steps, and specific endpoints affected."}
          </p>
          
          <div style={{ display: 'flex', gap: '16px' }}>
            <button className="btn btn-primary">Acknowledge</button>
            <button className="btn btn-secondary">Generate API Change Entry</button>
          </div>
        </section>
        
        <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Metadata</h2>
          
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Published At</div>
            <div style={{ fontWeight: 500 }}>{notice.published_at ? new Date(notice.published_at).toLocaleDateString() : 'Unknown'}</div>
          </div>
          
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Effective At</div>
            <div style={{ fontWeight: 500 }}>{notice.effective_at ? new Date(notice.effective_at).toLocaleDateString() : 'TBD'}</div>
          </div>
          
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Affected API</div>
            <div style={{ fontWeight: 500 }}><Link href="/apis" style={{ color: 'var(--primary)' }}>{notice.affected_api || 'Multiple'}</Link></div>
          </div>
        </section>
      </div>
    </>
  );
}
