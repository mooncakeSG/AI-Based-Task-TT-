import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, LogOut, Settings, ChevronDown, Shield, Mail, Calendar } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

const UserProfile = ({ className = "" }) => {
  const { user, isAuthenticated, signOut } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleSignOut = async () => {
    const { error } = await signOut();
    if (error) {
      toast.error('Failed to sign out');
    } else {
      toast.success('Signed out successfully');
      setIsDropdownOpen(false);
    }
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  const userDisplayName = user.user_metadata?.full_name || user.email?.split('@')[0] || 'User';
  const userEmail = user.email;
  const userAvatar = user.user_metadata?.avatar_url;
  const joinDate = new Date(user.created_at).toLocaleDateString();

  return (
    <div className={`relative ${className}`}>
      <motion.button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-3 p-2 rounded-xl hover:bg-gray-100/80 transition-colors"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="relative">
          {userAvatar ? (
            <img
              src={userAvatar}
              alt={userDisplayName}
              className="w-8 h-8 rounded-full border-2 border-blue-200 shadow-sm"
            />
          ) : (
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center border-2 border-blue-200 shadow-sm">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
        </div>

        <div className="hidden sm:block text-left">
          <p className="text-sm font-medium text-gray-900 truncate max-w-24">
            {userDisplayName}
          </p>
          <p className="text-xs text-gray-500">
            Authenticated
          </p>
        </div>

        <ChevronDown 
          className={`w-4 h-4 text-gray-400 transition-transform ${
            isDropdownOpen ? 'rotate-180' : ''
          }`} 
        />
      </motion.button>

      <AnimatePresence>
        {isDropdownOpen && (
          <>
            <div 
              className="fixed inset-0 z-40" 
              onClick={() => setIsDropdownOpen(false)}
            />
            
            <motion.div
              className="absolute right-0 top-full mt-2 w-72 bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-200/60 z-50 overflow-hidden"
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <div className="p-4 bg-gradient-to-r from-blue-50/80 to-purple-50/80 border-b border-gray-200/60">
                <div className="flex items-center space-x-3">
                  {userAvatar ? (
                    <img
                      src={userAvatar}
                      alt={userDisplayName}
                      className="w-12 h-12 rounded-full border-2 border-blue-200 shadow-sm"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center border-2 border-blue-200 shadow-sm">
                      <User className="w-6 h-6 text-white" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {userDisplayName}
                    </h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Mail className="w-3 h-3" />
                      <span className="truncate">{userEmail}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>Joined {joinDate}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Shield className="w-3 h-3" />
                    <span>Verified</span>
                  </div>
                </div>
              </div>

              <div className="p-2">
                <button
                  onClick={() => {
                    setIsDropdownOpen(false);
                    toast.info('Settings coming soon!');
                  }}
                  className="w-full flex items-center space-x-3 p-3 text-gray-700 hover:bg-gray-100/80 rounded-xl transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  <span className="text-sm font-medium">Account Settings</span>
                </button>

                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center space-x-3 p-3 text-red-600 hover:bg-red-50/80 rounded-xl transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-medium">Sign Out</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserProfile; 