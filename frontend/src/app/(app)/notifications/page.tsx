'use client';
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */

import Link from 'next/link';

import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      const res = await apiClient.GET('/api/v1/notifications/');
      if (res.data) setNotifications(res.data as any[]);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const load = async () => {
      await fetchNotifications();
    };
    load();
  }, []);

  const markAllAsRead = async () => {
    try {
      await apiClient.POST('/api/v1/notifications/read-all');
      await fetchNotifications();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const markAsRead = async (id: string) => {
    try {
      await apiClient.POST('/api/v1/notifications/{notification_id}/read', {
        params: { path: { notification_id: id as any } }
      });
      await fetchNotifications();
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-subtitle">Alerts and updates for your organization.</p>
        </div>
        {notifications.length > 0 && notifications.some(n => !n.is_read) && (
          <button className="btn btn-secondary" onClick={markAllAsRead}>Mark All as Read</button>
        )}
      </div>
      
      {loading ? (
        <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
      ) : notifications.length === 0 ? (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
          <h2 className="empty-state-title">You're all caught up</h2>
          <p className="empty-state-description">
            You have no notifications. Important events like breaking API changes and automated PRs will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {notifications.map((notification) => (
            <div key={notification.id} className="card" style={{ padding: '24px', border: `1px solid ${notification.is_read ? 'var(--border)' : 'var(--primary)'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: notification.is_read ? 'var(--foreground)' : 'var(--primary)' }}>
                  {notification.title}
                </h3>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  {notification.created_at ? new Date(notification.created_at).toLocaleString() : ''}
                </span>
              </div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>{notification.message}</p>
              
              <div style={{ display: 'flex', gap: '12px' }}>
                {notification.resource_url && (
                  <Link href={notification.resource_url} onClick={() => !notification.is_read && markAsRead(notification.id)} className="btn btn-sm btn-primary">
                    View Details
                  </Link>
                )}
                {!notification.is_read && (
                  <button onClick={() => markAsRead(notification.id)} className="btn btn-sm btn-secondary">
                    Mark as Read
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
