/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';

export default function DocsPage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Welcome to API Guardian Documentation</h1>
        <p className="page-subtitle">The autonomous third-party API dependency maintenance platform.</p>
      </div>
      
      <div style={{ lineHeight: '1.6' }}>
        <div className="card" style={{ marginBottom: '32px' }}>
          <h2 style={{ marginBottom: '16px', fontSize: '1.25rem', fontWeight: 600 }}>What is API Guardian?</h2>
          <p>
            API Guardian monitors the third-party APIs your application depends on. When a provider announces a breaking change, deprecation, or sunset, API Guardian automatically detects it, maps it to your codebase, generates a migration patch, tests the patch deterministically, and opens a Pull Request with cryptographic proof of safety.
          </p>
        </div>

        <h2 style={{ marginBottom: '16px', fontSize: '1.5rem', fontWeight: 600 }}>Navigation</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '24px', marginBottom: '32px' }}>
          <Link href="/docs/quickstart" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Quickstart</h3>
            <p style={{ color: 'var(--text-muted)' }}>Set up your organization, connect integrations, and guard your first API.</p>
          </Link>
          <Link href="/docs/how-it-works" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>How it Works</h3>
            <p style={{ color: 'var(--text-muted)' }}>Understand the deterministic end-to-end workflow from detection to PR.</p>
          </Link>
          <Link href="/docs/guarded-apis" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Guarded APIs</h3>
            <p style={{ color: 'var(--text-muted)' }}>Monitor and protect external API dependencies.</p>
          </Link>
          <Link href="/docs/provider-notices" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Provider Notices</h3>
            <p style={{ color: 'var(--text-muted)' }}>Automated detection of upstream breaking changes.</p>
          </Link>
          <Link href="/docs/migration" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Migrations</h3>
            <p style={{ color: 'var(--text-muted)' }}>How LLM-assisted code migrations are performed securely.</p>
          </Link>
          <Link href="/docs/verification" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Verification</h3>
            <p style={{ color: 'var(--text-muted)' }}>Deterministic verification and testing of patches.</p>
          </Link>
          <Link href="/docs/security" className="card" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <h3 style={{ marginBottom: '8px', color: 'var(--primary)', fontSize: '1.125rem', fontWeight: 600 }}>Security</h3>
            <p style={{ color: 'var(--text-muted)' }}>Architecture, RBAC, tenant isolation, and credentials.</p>
          </Link>
        </div>
      </div>
    </>
  );
}
