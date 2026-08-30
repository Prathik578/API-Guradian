/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '24px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)' }}>
        <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>API Guardian</div>
        <nav style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <Link href="#features" style={{ color: 'var(--text-muted)' }}>Features</Link>
          <Link href="#security" style={{ color: 'var(--text-muted)' }}>Security</Link>
          <Link href="/login" style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Sign In</Link>
          <Link href="/login" className="btn btn-primary" style={{ textDecoration: 'none' }}>Get Started</Link>
        </nav>
      </header>

      <main style={{ flex: 1 }}>
        <section style={{ padding: '120px 48px', textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '4rem', fontWeight: 800, lineHeight: 1.1, marginBottom: '24px', letterSpacing: '-0.02em' }}>
            Know when APIs change. <br/>
            Know what breaks. <br/>
            <span style={{ color: 'var(--primary)' }}>Fix it before production does.</span>
          </h1>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-muted)', marginBottom: '48px', lineHeight: 1.6 }}>
            The autonomous API maintenance control plane. API Guardian monitors upstream deprecations, identifies affected call sites in your repositories, and generates verified patches.
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <Link href="/login" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: '1.125rem' }}>Start Free Trial</Link>
            <Link href="#how-it-works" className="btn btn-secondary" style={{ padding: '16px 32px', fontSize: '1.125rem' }}>See How It Works</Link>
          </div>
        </section>

        <section id="features" style={{ padding: '80px 48px', background: 'var(--surface)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '48px', textAlign: 'center' }}>Key Capabilities</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px' }}>
              <div style={{ background: 'var(--background)', padding: '32px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Provider Notices</h3>
                <p style={{ color: 'var(--text-muted)' }}>Automatically ingest deprecation announcements and breaking changes directly from providers.</p>
              </div>
              <div style={{ background: 'var(--background)', padding: '32px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Impact Analysis</h3>
                <p style={{ color: 'var(--text-muted)' }}>Pinpoint the exact files, lines, and call sites affected by a breaking change across all repositories.</p>
              </div>
              <div style={{ background: 'var(--background)', padding: '32px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Deterministic Verification</h3>
                <p style={{ color: 'var(--text-muted)' }}>Generated migrations are verified in isolated sandboxes to guarantee they pass your test suite.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="security" style={{ padding: '120px 48px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '24px' }}>Enterprise-Grade Security</h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--text-muted)', marginBottom: '48px', lineHeight: 1.6 }}>
            Your code never leaves your VPC. Deep tenant isolation, Postgres RLS, dropped capabilities, and non-root sandboxes ensure absolute security. No secrets are ever exposed to the verification engine.
          </p>
          <Link href="/login" className="btn btn-primary" style={{ padding: '12px 24px' }}>Secure Your Infrastructure</Link>
        </section>
      </main>

      <footer style={{ padding: '48px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
        <div>&copy; 2026 API Guardian Inc.</div>
        <div style={{ display: 'flex', gap: '24px' }}>
          <Link href="#">Privacy</Link>
          <Link href="#">Terms</Link>
        </div>
      </footer>
    </div>
  );
}
