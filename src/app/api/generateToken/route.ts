// app/api/generateToken/route.ts
import { NextRequest, NextResponse } from "next/server";

const MATHOS_API = "https://api.mathos.cloud/auth/generate-access-token/";

function getRedirectUrl(request: NextRequest, path: string) {
  const host = request.headers.get("x-forwarded-host") || request.headers.get("host");
  const proto = request.headers.get("x-forwarded-proto") || (request.url.startsWith("https") ? "https" : "http");
  if (host) {
    return new URL(path, `${proto}://${host}`);
  }
  return new URL(path, request.url);
}

export async function GET(request: NextRequest) {
  const refreshToken = request.cookies.get("refresh")?.value;

  // If no refresh token → clear everything and go to login
  if (!refreshToken) {
    const response = NextResponse.redirect(getRedirectUrl(request, "/"));
    response.cookies.delete("access");
    response.cookies.delete("refresh");
    return response;
  }

  try {
    const res = await fetch(MATHOS_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!res.ok) {
      throw new Error("Refresh token invalid or expired");
    }

    const { access } = await res.json();

    const redirectPath = request.nextUrl.searchParams.get("redirect") || "/dashboard";
    const redirectUrl = getRedirectUrl(request, redirectPath);

    const response = NextResponse.redirect(redirectUrl);

    // Set new access token
    response.cookies.set("access", access, {
      httpOnly: false, // Required for middleware to read it
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 5, // 5 minutes
    });

    return response;
  } catch (error) {
    console.error("Token refresh failed:", error);

    // On failure → logout user
    const response = NextResponse.redirect(getRedirectUrl(request, "/"));
    response.cookies.delete("access");
    response.cookies.delete("refresh");
    return response;
  }
}