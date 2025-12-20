import React from 'react';
import { motion } from 'framer-motion';
import { Database } from 'lucide-react';

export const NoDataState: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center max-w-md px-6"
      >
        <motion.div
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="relative w-32 h-32 mx-auto mb-6"
        >
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-500 to-blue-600 opacity-10 blur-2xl"></div>
          <div className="relative w-32 h-32 rounded-3xl bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center border-4 border-white shadow-xl">
            <Database className="w-16 h-16 text-purple-600" strokeWidth={1.5} />
          </div>
        </motion.div>

        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-3">
          No Data Found
        </h2>
        <p className="text-slate-600 text-lg mb-8">
          We couldn&apos;t find any data to display. Try adjusting your filters or check back later.
        </p>

        <motion.div
          className="inline-flex gap-2 text-sm text-slate-500"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 mt-1"></div>
          <span>No results available</span>
        </motion.div>
      </motion.div>
    </div>
  );
};
