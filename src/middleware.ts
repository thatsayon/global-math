
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return !payload.exp || payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  if (!pathname.startsWith('/dashboard')) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get('access')?.value;

  if (accessToken && !isTokenExpired(accessToken)) {
    return NextResponse.next();
  }

  // Token missing or expired → silent refresh
  const url = new URL('/api/generateToken', request.url);
  url.searchParams.set('redirect', pathname + request.nextUrl.search);

  return NextResponse.redirect(url);
}

export const config = {
  matcher: '/dashboard/:path*',
};