import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ChatBox from './components/ChatBox';
import SavedTasks from './components/SavedTasks';
import AuthModal from './components/AuthModal';
import Home from './pages/Home';
import Upload from './pages/Upload';
import About from './pages/About';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import { animations } from './styles/design-system';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('signin');

  // Add event listener for chat navigation
  useEffect(() => {
    const handleNavigateToChat = () => {
      setCurrentPage('chat');
    };
    
    window.addEventListener('navigate-to-chat', handleNavigateToChat);
    
    return () => {
      window.removeEventListener('navigate-to-chat', handleNavigateToChat);
    };
  }, []);

  const handleAuthModalOpen = (mode = 'signin') => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  const handleAuthModalClose = () => {
    setAuthModalOpen(false);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={setCurrentPage} />;
      case 'chat':
        return <ChatBox className="h-full" />;
      case 'tasks':
        return <SavedTasks className="h-full" />;
      case 'upload':
        return <Upload onNavigate={setCurrentPage} />;
      case 'about':
        return <About />;
      case 'profile':
        return <Profile />;
      case 'settings':
        return <Settings />;
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <AuthProvider>
      <Layout 
        currentPage={currentPage} 
        onNavigate={setCurrentPage}
        onAuthModalOpen={handleAuthModalOpen}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={animations.fadeIn.initial}
            animate={animations.fadeIn.animate}
            exit={animations.fadeIn.exit}
            transition={animations.fadeIn.transition}
            className="h-full"
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>

        {/* Authentication Modal */}
        <AuthModal
          isOpen={authModalOpen}
          onClose={handleAuthModalClose}
          initialMode={authModalMode}
        />

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#FFFFFF',
              color: '#1F2937',
              border: '1px solid #E5E7EB',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '500',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10B981',
                secondary: '#FFFFFF',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#EF4444',
                secondary: '#FFFFFF',
              },
            },
            loading: {
              iconTheme: {
                primary: '#2563EB',
                secondary: '#FFFFFF',
              },
            },
          }}
        />
      </Layout>
    </AuthProvider>
  );
}

export default App;
