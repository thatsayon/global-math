// app/api/logout/route.ts
import { NextResponse } from "next/server";

const AUTH_COOKIES = ["access", "refresh"] as const;

export async function POST() {
  const response = NextResponse.json({ success: true });

  // Overwrite with an already-expired cookie using the same attributes they
  // were set with, so the browser actually drops them.
  for (const name of AUTH_COOKIES) {
    response.cookies.set(name, "", {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 0,
    });
  }

  return response;
}
