import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

function getRedirectUrl(request: NextRequest, path: string) {
  const host = request.headers.get("x-forwarded-host") || request.headers.get("host");
  const proto = request.headers.get("x-forwarded-proto") || (request.url.startsWith("https") ? "https" : "http");
  if (host) {
    return new URL(path, `${proto}://${host}`);
  }
  return new URL(path, request.url);
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get("access")?.value;
  const refreshToken = request.cookies.get("refresh")?.value;

  // 1. Root redirect: if logged in → go to dashboard
  if (pathname === "/" && accessToken && !isTokenExpired(accessToken)) {
    return NextResponse.redirect(getRedirectUrl(request, "/dashboard"));
  }

  // 2. Protected routes
  const isProtected = pathname.startsWith("/dashboard");

  if (isProtected) {
    const hasValidAccessToken = accessToken && !isTokenExpired(accessToken);

    // Case A: Valid access token → continue
    if (hasValidAccessToken) {
      return NextResponse.next();
    }

    // Case B: No access token OR expired → try to refresh (if refresh exists)
    if (refreshToken) {
      const refreshUrl = getRedirectUrl(request, "/api/generateToken");
      refreshUrl.searchParams.set("redirect", pathname + request.nextUrl.search);

      return NextResponse.redirect(refreshUrl);
    }

    // Case C: No refresh token → force logout
    return NextResponse.redirect(getRedirectUrl(request, "/"));
  }

  // All other routes → allow
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/dashboard/:path*",
    // Important: Exclude the refresh API route itself to prevent redirect loop
    "/((?!api/generateToken).*)",
  ],
};