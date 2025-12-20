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

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get("access")?.value;
  const refreshToken = request.cookies.get("refresh")?.value;

  // 1. Root redirect: if logged in → go to dashboard
  if (pathname === "/" && accessToken && !isTokenExpired(accessToken)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
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
      const refreshUrl = new URL("/api/generateToken", request.url);
      refreshUrl.searchParams.set("redirect", pathname + request.nextUrl.search);

      return NextResponse.redirect(refreshUrl);
    }

    // Case C: No refresh token → force logout
    return NextResponse.redirect(new URL("/", request.url));
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