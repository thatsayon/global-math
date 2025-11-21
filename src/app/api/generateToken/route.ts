// app/api/generateToken/route.ts
import { NextRequest, NextResponse } from 'next/server';

const MATHOS_API = 'https://api.mathos.cloud/auth/generate-access-token/';

export async function GET(request: NextRequest) {
  const refreshToken = request.cookies.get('refresh')?.value;

  if (!refreshToken) {
    const response = NextResponse.redirect(new URL('/', request.url));
    response.cookies.delete('access');
    response.cookies.delete('refresh');
    return response;
  }

  try {
    const res = await fetch(MATHOS_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!res.ok) throw new Error('Refresh failed');

    const { access } = await res.json();

    const redirectUrl = request.nextUrl.searchParams.get('redirect') || '/dashboard';
    const response = NextResponse.redirect(new URL(redirectUrl, request.url));

    // 5 minutes expiry
    response.cookies.set('access', access, {
      httpOnly: false, // needed for client + middleware
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: 60 * 5, // 5 minutes
    });

    return response;
  } catch (error) {
    console.error('Token refresh failed:', error);
    const response = NextResponse.redirect(new URL('/', request.url));
    response.cookies.delete('access');
    response.cookies.delete('refresh');
    return response;
  }
}