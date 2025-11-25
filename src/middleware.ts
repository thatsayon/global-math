
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
const isProtectedRoute = pathname.startsWith("/dashboard");
  const accessToken = request.cookies.get('access')?.value;
  
  if (!isProtectedRoute) {
    return NextResponse.next();
  }
if (accessToken && !isTokenExpired(accessToken)) {
    return NextResponse.next();
  }

  // Token missing or expired → silent refresh
  const url = new URL('/api/generateToken', request.url);
  url.searchParams.set('redirect', pathname + request.nextUrl.search);


  if (isProtectedRoute && !accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  if (pathname === "/" && accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  

  return NextResponse.redirect(url);
}

export const config = {
  matcher: '/dashboard/:path*',
};
