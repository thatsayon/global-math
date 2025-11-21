
import { configureStore } from '@reduxjs/toolkit';
import { apiSlice } from './slices/api/ApiSlice';

export const makeStore = () => {
  return configureStore({
    reducer: {
      // Add the RTK Query api slice reducer
      [apiSlice.reducerPath]: apiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false, // recommended for RTK Query
        immutableCheck: false,
      }).concat(apiSlice.middleware),
    devTools: process.env.NODE_ENV !== 'production',
  });
};

// Infer the type of makeStore
export type AppStore = ReturnType<typeof makeStore>;
// Infer RootState and AppDispatch from the store itself
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];