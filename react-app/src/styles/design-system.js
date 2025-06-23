// Design System Configuration
export const colors = {
  background: '#F9FAFB',
  primary: '#2563EB',
  accent: '#9333EA',
  text: '#1F2937',
  border: '#E5E7EB',
  white: '#FFFFFF',
  // Message colors
  userBg: '#EFF6FF',
  userText: '#1E40AF',
  aiBorder: '#2563EB',
  // Status colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  // Grays
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
};

export const animations = {
  // Framer Motion variants
  fadeIn: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  
  slideUp: {
    initial: { opacity: 0, y: 50 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 50 },
    transition: { duration: 0.4, ease: "easeOut" }
  },
  
  scaleIn: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
    transition: { duration: 0.2, ease: "easeOut" }
  },

  staggerChildren: {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }
};

export const spacing = {
  page: 'max-w-4xl mx-auto',
  section: 'p-6',
  card: 'p-6 rounded-2xl shadow-md border border-gray-200',
  gap: 'gap-4',
  spaceY: 'space-y-6'
};

export const shadows = {
  soft: 'shadow-sm',
  card: 'shadow-md',
  elevated: 'shadow-lg',
  floating: 'shadow-xl'
}; 