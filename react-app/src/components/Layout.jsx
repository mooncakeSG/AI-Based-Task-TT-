import { motion } from 'framer-motion';
import Header from './Header';
import { animations } from '../styles/design-system';

const Layout = ({ children, currentPage, onNavigate }) => {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image Layer */}
      <motion.div 
        className="fixed inset-0 z-0"
        initial={{ opacity: 0, scale: 1.1 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
      >
        <div 
          className="w-full h-full bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('/bg-pattern.jpg')`,
          }}
        />
      </motion.div>

      {/* Readability Overlay */}
      <motion.div 
        className="fixed inset-0 z-1 bg-gradient-to-br from-white/75 via-white/70 to-white/65 backdrop-blur-[2px]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 0.3 }}
      />

      {/* Main Content Container */}
      <div className="relative z-10 min-h-screen flex flex-col">
        <Header currentPage={currentPage} onNavigate={onNavigate} />
        
        <motion.main 
          className="flex-1 p-4 md:p-6 lg:p-8"
          variants={animations.staggerChildren}
          initial="initial"
          animate="animate"
        >
          <div className="max-w-4xl mx-auto h-full">
            {children}
          </div>
        </motion.main>
        
        <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200/60 py-6">
          <div className="max-w-4xl mx-auto px-4 md:px-6">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-3 md:space-y-0">
              <div className="text-center md:text-left">
                <p className="text-sm text-gray-600 font-medium">
                  © 2024 IntelliAssist.AI
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Powered by React, Tailwind CSS & AI
                </p>
              </div>
              
              <div className="flex items-center space-x-6">
                <button
                  onClick={() => onNavigate('about')}
                  className="text-xs text-gray-500 hover:text-blue-600 transition-colors duration-200"
                >
                  About
                </button>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-gray-500">AI Online</span>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Layout; 