import { motion } from 'framer-motion';
import { Home, MessageSquare, ListChecks, Upload, Menu, Sparkles } from 'lucide-react';
import UserProfile from './UserProfile';
import { animations } from '../styles/design-system';

const Header = ({ currentPage, onNavigate, onAuthModalOpen }) => {
  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'tasks', label: 'Tasks', icon: ListChecks },
    { id: 'upload', label: 'Upload', icon: Upload },
  ];

  return (
    <motion.header 
      className="sticky top-0 bg-white/90 backdrop-blur-md shadow-sm/50 border-b border-gray-200/60 z-50"
      initial={animations.slideUp.initial}
      animate={animations.slideUp.animate}
      transition={animations.slideUp.transition}
    >
      <div className="max-w-4xl mx-auto px-4 md:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div 
              className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
              whileHover={{ rotate: 5, scale: 1.1 }}
              transition={{ duration: 0.2 }}
            >
              <Sparkles className="w-5 h-5 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">IntelliAssist</h1>
              <p className="text-xs text-gray-500 -mt-1">AI Assistant</p>
            </div>
          </motion.div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item) => (
              <motion.button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`
                  relative px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200
                  ${currentPage === item.id
                    ? 'text-blue-600 bg-blue-50/80 backdrop-blur-sm shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white/60 backdrop-blur-sm'
                  }
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {currentPage === item.id && (
                  <motion.div
                    className="absolute inset-0 bg-blue-100/60 backdrop-blur-sm rounded-xl -z-10"
                    layoutId="activeTab"
                    transition={{ duration: 0.3, ease: "easeOut" }}
                  />
                )}
              </motion.button>
            ))}
          </nav>

          {/* User Profile */}
          <div className="hidden md:block">
            <UserProfile onAuthModalOpen={onAuthModalOpen} />
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden">
            <motion.button
              onClick={() => {
                // Toggle mobile menu logic here if needed
              }}
              className="p-2 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-white/60 backdrop-blur-sm transition-colors"
              whileTap={{ scale: 0.95 }}
            >
              <Menu className="w-6 h-6" />
            </motion.button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <div className="md:hidden pb-4 pt-2">
          <div className="flex justify-between items-center">
            <div className="flex space-x-1 overflow-x-auto">
              {navigationItems.map((item) => (
                <motion.button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`
                    flex-shrink-0 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                    ${currentPage === item.id
                      ? 'text-blue-600 bg-blue-50/80 backdrop-blur-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white/60 backdrop-blur-sm'
                    }
                  `}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="flex items-center gap-2">
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                </motion.button>
              ))}
            </div>
            
            {/* Mobile User Profile */}
            <div className="ml-4">
              <UserProfile onAuthModalOpen={onAuthModalOpen} />
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header; 