import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, AlertCircle } from 'lucide-react';

export const ErrorState: React.FC<{ onRefresh?: () => void }> = ({ onRefresh }) => {
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center max-w-md px-6"
      >
        <motion.div
          animate={{ rotate: [0, -5, 5, -5, 0] }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative w-32 h-32 mx-auto mb-6"
        >
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-red-500 via-purple-500 to-blue-600 opacity-20 blur-2xl"></div>
          <div className="relative w-32 h-32 rounded-3xl bg-gradient-to-br from-red-50 to-purple-50 flex items-center justify-center border-4 border-white shadow-xl">
            <AlertCircle className="w-16 h-16 text-red-500" strokeWidth={1.5} />
          </div>
        </motion.div>

        <h2 className="text-3xl font-bold text-slate-800 mb-3">
          Oops! Something Went Wrong
        </h2>
        <p className="text-slate-600 text-lg mb-8">
          We encountered an error while loading your content. Please try refreshing the page.
        </p>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleRefresh}
          className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow"
        >
          <RefreshCw className="w-5 h-5" />
          Refresh Page
        </motion.button>

        <motion.p
          className="mt-6 text-sm text-slate-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          If the problem persists, please contact support
        </motion.p>
      </motion.div>
    </div>
  );
};