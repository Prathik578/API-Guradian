'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { logoutAction } from '../app/actions/auth';
import { useState, useEffect } from 'react';

const NAV_SECTIONS = [
  {
    title: 'Overview',
    items: [{ href: '/dashboard', label: 'Dashboard' }]
  },
  {
    title: 'Inventory',
    items: [
      { href: '/apis', label: 'Guarded APIs' },
      { href: '/repositories', label: 'Repositories' },
      { href: '/integrations', label: 'Integrations' }
    ]
  },
  {
    title: 'Intelligence',
    items: [
      { href: '/api-changes', label: 'API Changes' },
      { href: '/notices', label: 'Provider Notices' }
    ]
  },
  {
    title: 'Automation',
    items: [
      { href: '/cases', label: 'Maintenance Cases' },
      { href: '/pull-requests', label: 'Pull Requests' }
    ]
  },
  {
    title: 'Observability',
    items: [
      { href: '/activity', label: 'Activity Logs' },
      { href: '/notifications', label: 'Notifications' },
      { href: '/usage', label: 'Usage' }
    ]
  },
  {
    title: 'Administration',
    items: [
      { href: '/members', label: 'Members' },
      { href: '/security', label: 'Security' },
      { href: '/settings', label: 'Settings' }
    ]
  },
  {
    title: 'Resources',
    items: [
      { href: '/docs', label: 'Documentation' }
    ]
  }
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    import('@/api/client').then(({ apiClient }) => {
      apiClient.GET('/api/v1/notifications/').then(res => {
        if (res.data) {
          setUnreadCount((res.data as any[]).filter(n => !n.is_read).length);
        }
      });
    });
  }, [pathname]);

  const getCurrentPageTitle = () => {
    for (const section of NAV_SECTIONS) {
      for (const item of section.items) {
        if (pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/dashboard')) {
          return item.label;
        }
      }
    }
    return 'Overview';
  };

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          API Guardian
        </div>
        <nav className="sidebar-nav">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title} className="nav-section">
              <div className="nav-section-title">{section.title}</div>
              {section.items.map((item) => {
                const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/dashboard');
                return (
                  <Link 
                    key={item.href} 
                    href={item.href} 
                    className={`nav-item ${isActive ? 'active' : ''}`}
                  >
                    <span>{item.label}</span>
                    {item.href === '/notifications' && unreadCount > 0 && (
                      <span className="badge warning" style={{ padding: '0 4px', fontSize: '0.7rem' }}>
                        {unreadCount}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
        
        <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
          <form action={logoutAction}>
            <button type="submit" className="nav-item" style={{ color: 'var(--error)' }}>
              Logout
            </button>
          </form>
        </div>
      </aside>
      
      <main className="main-content">
        <header className="header">
          <div>
            <span style={{ color: 'var(--text-muted)', marginRight: '8px' }}>Organization /</span>
            <span style={{ fontWeight: 600 }}>{getCurrentPageTitle()}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Link href="/notifications" style={{ position: 'relative', color: 'var(--text-muted)' }}>
              <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              {unreadCount > 0 && (
                <div style={{ position: 'absolute', top: -2, right: -2, width: 8, height: 8, borderRadius: '50%', background: 'var(--error)' }}></div>
              )}
            </Link>
            <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 600 }}>
              U
            </div>
          </div>
        </header>
        
        <div className="content-area">
          <div className="content-container">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
