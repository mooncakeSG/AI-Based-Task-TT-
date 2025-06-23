import React from 'react';
import { motion } from 'framer-motion';

const IconButton = ({ 
  icon: Icon, 
  children, 
  variant = 'default',
  size = 'md',
  onClick,
  disabled = false,
  className = '',
  ...props 
}) => {
  const variants = {
    default: 'text-gray-600 hover:text-gray-900 hover:bg-white/60 border border-gray-200/60',
    primary: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50/80 border border-blue-200/60',
    secondary: 'text-purple-600 hover:text-purple-700 hover:bg-purple-50/80 border border-purple-200/60',
    success: 'text-green-600 hover:text-green-700 hover:bg-green-50/80 border border-green-200/60',
    danger: 'text-red-600 hover:text-red-700 hover:bg-red-50/80 border border-red-200/60',
    ghost: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50/80'
  };

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      className={`
        inline-flex items-center gap-2 rounded-xl font-medium transition-all duration-200 backdrop-blur-sm
        ${variants[variant]} ${sizes[size]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
        ${className}
      `}
      whileHover={disabled ? {} : { scale: 1.02 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      {...props}
    >
      {Icon && <Icon className={`${iconSizes[size]} transition-transform`} />}
      {children}
    </motion.button>
  );
};

export default IconButton; 