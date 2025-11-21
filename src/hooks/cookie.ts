// src/hooks/cookie.ts
"use client";

import { authEvents } from '@/lib/authEvents';

const isProd = process.env.NODE_ENV === 'production';

export const setCookie = (name: string, value: string, days: number) => {
  if (typeof window === "undefined") return;

  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);

  const secure = isProd ? ';Secure' : '';
  const cookieValue = encodeURIComponent(value);

  document.cookie = `${name}=${cookieValue};expires=${expires.toUTCString()};path=/;SameSite=Strict${secure}`;

  if (name === 'access') authEvents.emit('accessChanged');
  if (name === 'refresh') authEvents.emit('refreshChanged');
};

export const removeCookie = (name: string) => {
  if (typeof window === "undefined") return;

  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Strict`;
  
  if (name === 'access' || name === 'refresh') {
    authEvents.emit('loggedOut');
  }
};

export const getCookie = (name: string): string | null => {
  if (typeof window === "undefined") return null;

  const match = document.cookie
    .split('; ')
    .find(row => row.startsWith(`${name}=`));

  return match ? decodeURIComponent(match.split('=')[1]) : null;
};