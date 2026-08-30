/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
'use server';

import { cookies } from 'next/headers';
import { apiClient } from '../../api/client';
import { redirect } from 'next/navigation';

function formatApiError(resError: unknown, fallback: string): string {
  if (!resError || typeof resError !== 'object') return fallback;
  const err = resError as Record<string, unknown>;
  const detail = err.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object' && 'msg' in item && typeof item.msg === 'string') {
          return item.msg;
        }
        return typeof item === 'object' ? JSON.stringify(item) : String(item);
      })
      .join(', ');
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  return fallback;
}

export async function loginAction(prevState: unknown, formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  if (!email || !password) {
    return { error: 'Email and password are required' };
  }

  try {
    const res = await apiClient.POST('/api/v1/auth/login', {
      body: { email, password }
    });

    if (res.data) {
      if (res.data.mfa_required) {
        return { success: true, mfaRequired: true, mfaToken: res.data.mfa_token };
      }

      const cookieStore = await cookies();
      
      if (res.data.token) {
        cookieStore.set('token', res.data.token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 604800,
          path: '/',
        });
      }
      
      if (res.data.organizations && res.data.organizations.length > 0) {
        cookieStore.set('tenant_id', res.data.organizations[0].id, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 604800,
          path: '/',
        });
        
        return { success: true, redirectUrl: '/dashboard' };
      } else {
        return { success: true, redirectUrl: '/onboarding' };
      }
    } else {
      const errorMessage = formatApiError(res.error, 'Invalid email or password.');
      return { error: errorMessage };
    }
  } catch (err: any) {
    const msg = (err as Error).message || '';
    if (msg.includes('fetch failed') || msg.includes('ECONNREFUSED') || msg.includes('Failed to fetch')) {
      return { error: 'API Guardian is temporarily unavailable. Please try again.' };
    }
    return { error: `Error: ${msg}` };
  }
}

export async function verifyMfaLoginAction(prevState: unknown, formData: FormData) {
  const mfaToken = formData.get('mfaToken') as string;
  const code = formData.get('code') as string;

  if (!mfaToken || !code) {
    return { error: 'Code is required' };
  }

  try {
    const res = await apiClient.POST('/api/v1/auth/verify-mfa-login', {
      body: { mfa_token: mfaToken, code }
    });

    if (res.data) {
      const cookieStore = await cookies();
      
      if (res.data.token) {
        cookieStore.set('token', res.data.token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 604800,
          path: '/',
        });
      }
      
      if (res.data.organizations && res.data.organizations.length > 0) {
        cookieStore.set('tenant_id', res.data.organizations[0].id, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 604800,
          path: '/',
        });
        
        return { success: true, redirectUrl: '/dashboard' };
      } else {
        return { success: true, redirectUrl: '/onboarding' };
      }
    } else {
      const errorMessage = formatApiError(res.error, 'Invalid code.');
      return { error: errorMessage };
    }
  } catch (err: any) {
    const msg = (err as Error).message || '';
    if (msg.includes('fetch failed') || msg.includes('ECONNREFUSED') || msg.includes('Failed to fetch')) {
      return { error: 'API Guardian is temporarily unavailable. Please try again.' };
    }
    return { error: `Error: ${msg}` };
  }
}

export async function signupAction(prevState: unknown, formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;
  const confirmPassword = formData.get('confirmPassword') as string;

  if (!email || !password || !name || !confirmPassword) {
    return { error: 'All fields are required' };
  }

  if (password !== confirmPassword) {
    return { error: 'Passwords do not match' };
  }

  try {
    const res = await apiClient.POST('/api/v1/auth/signup', {
      body: { name, email, password, confirm_password: confirmPassword }
    });

    if (res.data && res.data.token) {
      const cookieStore = await cookies();
      
      cookieStore.set('token', res.data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 604800,
        path: '/',
      });
      
      return { success: true, redirectUrl: '/onboarding' };
    } else if (res.data && res.data.mfa_required) {
      return { success: true, mfaRequired: true, mfaToken: res.data.mfa_token };
    } else {
      const errorMessage = formatApiError(res.error, 'Signup failed.');
      return { error: errorMessage };
    }
  } catch (err: any) {
    const msg = (err as Error).message || '';
    if (msg.includes('fetch failed') || msg.includes('ECONNREFUSED') || msg.includes('Failed to fetch')) {
      return { error: 'API Guardian is temporarily unavailable. Please try again.' };
    }
    return { error: `Error: ${msg}` };
  }
}

export async function onboardAction(prevState: unknown, formData: FormData) {
  const accountType = formData.get('accountType') as string || 'PERSONAL';
  const orgName = formData.get('orgName') as string;

  if (!orgName) {
    return { error: 'Workspace / Organization name is required' };
  }

  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    return { error: 'Authentication required. Please log in again.' };
  }

  try {
    const payloadBase64 = token.split('.')[1];
    const payloadStr = Buffer.from(payloadBase64, 'base64').toString('utf-8');
    const payload = JSON.parse(payloadStr);
    const userId = payload.sub;

    const res = await apiClient.POST('/api/v1/auth/onboarding', {
      params: { query: { user_id: userId } },
      body: {
        account_type: accountType,
        organization_name: orgName
      }
    });

    if (res.data) {
      cookieStore.set('tenant_id', res.data.id, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 604800,
        path: '/',
      });
      return { success: true, redirectUrl: '/dashboard' };
    } else {
      const errorMessage = formatApiError(res.error, 'Onboarding failed.');
      return { error: errorMessage };
    }
  } catch (err: any) {
    const msg = (err as Error).message || '';
    if (msg.includes('fetch failed') || msg.includes('ECONNREFUSED') || msg.includes('Failed to fetch')) {
      return { error: 'API Guardian is temporarily unavailable. Please try again.' };
    }
    return { error: `Error: ${msg}` };
  }
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete('token');
  cookieStore.delete('tenant_id');
  redirect('/login');
}
