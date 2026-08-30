import Link from 'next/link';

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  const sections = [
    {
      title: "Getting Started",
      links: [
        { label: "Introduction", href: "/docs/introduction" },
        { label: "Quickstart", href: "/docs/quickstart" },
        { label: "How it Works", href: "/docs/how-it-works" },
        { label: "Core Concepts", href: "/docs/core-concepts" },
      ]
    },
    {
      title: "Features",
      links: [
        { label: "Guarded APIs", href: "/docs/guarded-apis" },
        { label: "Repositories", href: "/docs/repositories" },
        { label: "Provider Changes", href: "/docs/provider-changes" },
        { label: "Provider Notices", href: "/docs/provider-notices" },
        { label: "Impact Analysis", href: "/docs/impact-analysis" },
        { label: "Replacement Mapping", href: "/docs/replacement-mapping" },
        { label: "Migration", href: "/docs/migration" },
        { label: "Verification", href: "/docs/verification" },
        { label: "Evidence", href: "/docs/evidence" },
      ]
    },
    {
      title: "Platform",
      links: [
        { label: "GitHub Integration", href: "/docs/github-integration" },
        { label: "Pull Requests", href: "/docs/pull-requests" },
        { label: "Authentication", href: "/docs/authentication" },
        { label: "Organizations", href: "/docs/organizations" },
        { label: "Members", href: "/docs/members" },
        { label: "RBAC", href: "/docs/rbac" },
        { label: "MFA", href: "/docs/mfa" },
        { label: "Activity Logs", href: "/docs/activity-logs" },
        { label: "Notifications", href: "/docs/notifications" },
        { label: "Usage and Quotas", href: "/docs/usage-and-quotas" },
        { label: "Integrations", href: "/docs/integrations" },
      ]
    },
    {
      title: "Architecture & Ops",
      links: [
        { label: "Security", href: "/docs/security" },
        { label: "Architecture", href: "/docs/architecture" },
        { label: "API Reference", href: "/docs/api-reference" },
        { label: "Configuration", href: "/docs/configuration" },
        { label: "Environment Variables", href: "/docs/environment-variables" },
        { label: "Local Development", href: "/docs/local-development" },
        { label: "Deployment", href: "/docs/deployment" },
        { label: "AWS Runtime", href: "/docs/aws-runtime" },
        { label: "Troubleshooting", href: "/docs/troubleshooting" },
        { label: "Known Limitations", href: "/docs/known-limitations" },
      ]
    }
  ];

  return (
    <div style={{ display: 'flex', gap: '48px' }}>
      <div style={{ width: '250px', flexShrink: 0, borderRight: '1px solid var(--border)', paddingRight: '24px' }}>
        {sections.map((section, idx) => (
          <div key={idx} style={{ marginBottom: '24px' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
              {section.title}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {section.links.map((link, lidx) => (
                <Link key={lidx} href={link.href} style={{ textDecoration: 'none', color: 'var(--foreground)', fontSize: '0.9rem' }}>
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div style={{ flex: 1, minWidth: 0, maxWidth: '800px' }}>
        {children}
      </div>
    </div>
  );
}
