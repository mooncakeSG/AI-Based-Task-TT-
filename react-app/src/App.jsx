import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import ChatBox from './components/ChatBox';
import SavedTasks from './components/SavedTasks';
import Home from './pages/Home';
import Upload from './pages/Upload';
import About from './pages/About';
import { animations } from './styles/design-system';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

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
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
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
  );
}

export default App;
