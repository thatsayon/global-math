// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true; // Invalid token → treat as expired
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get("access")?.value;

  // 1. If on root (/) and logged in → redirect to dashboard
  if (pathname === "/" && accessToken && !isTokenExpired(accessToken)) {
    const url = new URL("/dashboard", request.url);
    return NextResponse.redirect(url);
  }

  // 2. If on protected route (/dashboard/*)
  const isProtectedRoute = pathname.startsWith("/dashboard");

  if (isProtectedRoute) {
    // No token → redirect to login
    if (!accessToken) {
      const url = new URL("/", request.url);
      return NextResponse.redirect(url);
    }

    // Token exists but expired → silent refresh
    if (isTokenExpired(accessToken)) {
      const url = new URL("/api/generateToken", request.url);
      url.searchParams.set("redirect", pathname + request.nextUrl.search);
      return NextResponse.redirect(url);
    }

    // Token valid → allow access
    return NextResponse.next();
  }

  // All other routes → allow
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/", // for root redirect
    "/dashboard/:path*", // protect all dashboard routes
  ],
};
