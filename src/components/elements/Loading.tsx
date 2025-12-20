import React from 'react';
import { motion } from 'framer-motion';

interface LoadingStateProps {
  variant?: 'spinner' | 'dots' | 'pulse' | 'bars';
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ 
  variant = 'dots', 
  size = 'lg',
  fullScreen = true 
}) => {
  const sizeClasses = {
    sm: { container: 'w-8 h-8', dot: 'w-1.5 h-1.5', bar: 'h-6', text: 'text-sm' },
    md: { container: 'w-16 h-16', dot: 'w-2 h-2', bar: 'h-12', text: 'text-base' },
    lg: { container: 'w-24 h-24', dot: 'w-3 h-3', bar: 'h-16', text: 'text-lg' }
  };

  const currentSize = sizeClasses[size];
  const containerClass = fullScreen 
    ? "flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100"
    : "flex items-center justify-center py-12";

  const renderSpinner = () => (
    <div className="relative">
      <motion.div
        className={`${currentSize.container} rounded-full border-4 border-slate-200`}
        style={{ borderTopColor: 'transparent' }}
      >
        <motion.div
          className="absolute inset-0 rounded-full border-4 border-transparent"
          style={{
            borderTopColor: '#3b82f6',
            borderRightColor: '#8b5cf6',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      </motion.div>
      <motion.div
        className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 blur-xl"
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </div>
  );

  const renderDots = () => (
    <div className="flex gap-3">
      {[0, 1, 2, 3, 4].map((i) => (
        <motion.div
          key={i}
          className={`${currentSize.dot} rounded-full bg-gradient-to-r from-blue-500 to-purple-500`}
          animate={{ 
            y: [0, -20, 0],
            scale: [1, 1.2, 1]
          }}
          transition={{ 
            duration: 0.6, 
            repeat: Infinity, 
            delay: i * 0.1,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );

  const renderPulse = () => (
    <div className="relative">
      <motion.div
        className={`${currentSize.container} rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600`}
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: [0, 180, 360]
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className={`absolute inset-0 rounded-2xl border-4 border-purple-500`}
          animate={{ 
            scale: [1, 1.5, 2],
            opacity: [0.8, 0.3, 0]
          }}
          transition={{ 
            duration: 2, 
            repeat: Infinity, 
            delay: i * 0.6,
            ease: "easeOut"
          }}
        />
      ))}
    </div>
  );

  const renderBars = () => (
    <div className="flex gap-2 items-end">
      {[0, 1, 2, 3, 4].map((i) => (
        <motion.div
          key={i}
          className={`w-2 ${currentSize.bar} rounded-full bg-gradient-to-t from-blue-500 to-purple-500`}
          animate={{ 
            scaleY: [0.3, 1, 0.3],
          }}
          transition={{ 
            duration: 1, 
            repeat: Infinity, 
            delay: i * 0.1,
            ease: "easeInOut"
          }}
          style={{ originY: 1 }}
        />
      ))}
    </div>
  );

  const variants = {
    spinner: renderSpinner,
    dots: renderDots,
    pulse: renderPulse,
    bars: renderBars
  };

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="mb-6">
          {variants[variant]()}
        </div>
        
        {fullScreen && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className={`${currentSize.text} font-semibold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-2`}>
              Loading
            </h2>
            <p className="text-slate-600 text-sm">Please wait...</p>
          </motion.div>
        )}
      </div>
    </div>
  );
};