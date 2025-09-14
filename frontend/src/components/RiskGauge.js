import React from 'react';
import { motion } from 'framer-motion';

const RiskGauge = ({ riskScore, size = 'medium', showLabel = true }) => {
  const sizeClasses = {
    small: 'w-16 h-16',
    medium: 'w-24 h-24',
    large: 'w-32 h-32'
  };

  const textSizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  };

  const getRiskLevel = (score) => {
    if (score <= 3) return 'low';
    if (score <= 6) return 'moderate';
    return 'high';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low':
        return {
          primary: '#10b981',
          secondary: '#d1fae5',
          text: 'text-success-700'
        };
      case 'moderate':
        return {
          primary: '#f59e0b',
          secondary: '#fef3c7',
          text: 'text-warning-700'
        };
      case 'high':
        return {
          primary: '#ef4444',
          secondary: '#fee2e2',
          text: 'text-danger-700'
        };
      default:
        return {
          primary: '#6b7280',
          secondary: '#f3f4f6',
          text: 'text-gray-700'
        };
    }
  };

  const riskLevel = getRiskLevel(riskScore);
  const colors = getRiskColor(riskLevel);
  const percentage = (riskScore / 10) * 100;

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${sizeClasses[size]}`}>
        <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke={colors.secondary}
            strokeWidth="8"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="50"
            cy="50"
            r="40"
            stroke={colors.primary}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 40}`}
            initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
            animate={{ 
              strokeDashoffset: 2 * Math.PI * 40 * (1 - percentage / 100)
            }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${colors.text} ${textSizeClasses[size]}`}>
            {riskScore}/10
          </span>
        </div>
      </div>
      {showLabel && (
        <div className="mt-2 text-center">
          <span className={`text-xs font-medium uppercase tracking-wide ${colors.text}`}>
            {riskLevel} Risk
          </span>
        </div>
      )}
    </div>
  );
};

export default RiskGauge;
