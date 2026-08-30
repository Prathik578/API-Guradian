/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  const protectedRoutes = [
    '/dashboard',
    '/apis',
    '/api-changes',
    '/repositories',
    '/cases',
    '/migrations',
    '/verifications',
    '/pull-requests',
    '/notices',
    '/activity',
    '/notifications',
    '/integrations',
    '/usage',
    '/settings',
    '/security',
    '/members',
  ];

  const pathname = request.nextUrl.pathname;
  
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

  if (isProtectedRoute && !token) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from auth pages
  if (token && (pathname === '/login' || pathname === '/signup' || pathname === '/')) {
    const dashboardUrl = new URL('/dashboard', request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
