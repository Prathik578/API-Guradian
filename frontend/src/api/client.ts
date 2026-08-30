/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import createClient from 'openapi-fetch';
import type { paths } from './schema';

export const apiClient = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
    const headers = new Headers(init?.headers);
    
    // In browser
    if (typeof document !== 'undefined') {
      const match = document.cookie.match(new RegExp('(^| )tenant_id=([^;]+)'));
      if (match) headers.set('X-Tenant-ID', match[2]);
      const tokenMatch = document.cookie.match(new RegExp('(^| )token=([^;]+)'));
      if (tokenMatch) headers.set('Authorization', `Bearer ${tokenMatch[2]}`);
    } else {
      // On server
      try {
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();
        const tenantId = cookieStore.get('tenant_id');
        if (tenantId) headers.set('X-Tenant-ID', tenantId.value);
        const token = cookieStore.get('token');
        if (token) headers.set('Authorization', `Bearer ${token.value}`);
      } catch (_) {
        // ignore if not in Next.js server context
      }
    }
    
    return fetch(input, { ...init, headers });
  }
});

// Helper for type-safe data extraction
export async function fetchApi<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>
): Promise<T> {
  const { data, error } = await request;
  if (error) {
    throw new Error((error as {detail?: string}).detail || 'An API error occurred');
  }
  if (!data) {
    throw new Error('No data returned from API');
  }
  return data;
}
