'use client';

import { useEffect, useState } from 'react';

export default function RedirectClient({ postId }: { postId: string }) {
  const [redirecting, setRedirecting] = useState(true);

  useEffect(() => {
    const appUrl = `oreo://post?id=${postId}`;
    const storeUrl = "https://play.google.com/store/apps/details?id=com.coyoote.app";

    // Attempt to open the app
    window.location.replace(appUrl);

    // Fallback if app doesn't open
    const timeout = setTimeout(() => {
      window.location.replace(storeUrl);
    }, 2500);

    return () => clearTimeout(timeout);
  }, [postId]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-800 font-sans text-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-sm max-w-md w-full">
        <h1 className="text-xl font-bold mb-3">Opening in Coyoote...</h1>
        <p className="text-sm text-gray-500 mb-6">If the app doesn't open automatically, click the button below.</p>
        <a 
          href={`oreo://post?id=${postId}`} 
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-sm hover:bg-blue-700 transition-colors"
        >
          Open App
        </a>
      </div>
    </div>
  );
}
