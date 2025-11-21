'use client';

import { Provider } from 'react-redux';
import { useRef } from 'react';
import { AppStore, makeStore } from '@/store/store';

interface StoreProviderProps {
  children: React.ReactNode;
}

export default function StoreProvider({ children }: StoreProviderProps) {
  const storeRef = useRef<AppStore | null>(null);

  if (!storeRef.current) {
    // Create store only once (prevents recreating on HMR/re-renders)
    storeRef.current = makeStore();
  }

  return <Provider store={storeRef.current}>{children}</Provider>;
}