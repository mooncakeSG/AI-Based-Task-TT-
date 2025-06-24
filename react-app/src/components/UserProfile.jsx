import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfile = ({ onAuthModalOpen, onNavigate }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { 
    user, 
    signOut, 
    isAuthenticated, 
    getUserEmail, 
    getUserMetadata, 
    isEmailConfirmed,
    loading 
  } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
      setIsDropdownOpen(false);
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  const getInitials = () => {
    const metadata = getUserMetadata();
    const fullName = metadata?.full_name || getUserEmail() || '';
    
    if (fullName.includes('@')) {
      // If it's an email, use first letter
      return fullName.charAt(0).toUpperCase();
    }
    
    // If it's a name, use initials
    return fullName
      .split(' ')
      .map(name => name.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getDisplayName = () => {
    const metadata = getUserMetadata();
    return metadata?.full_name || getUserEmail() || 'User';
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
      </div>
    );
  }

  if (!isAuthenticated()) {
    return (
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onAuthModalOpen('signin')}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          Sign In
        </button>
        <button
          onClick={() => onAuthModalOpen('signup')}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          Sign Up
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {getInitials()}
          </div>
        </div>
        
        {/* User Info */}
        <div className="hidden sm:block text-left">
          <div className="text-sm font-medium text-gray-900 truncate max-w-32">
            {getDisplayName()}
          </div>
          {!isEmailConfirmed() && (
            <div className="text-xs text-amber-600">
              Email not verified
            </div>
          )}
        </div>

        {/* Dropdown Arrow */}
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${
            isDropdownOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isDropdownOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsDropdownOpen(false)}
          />
          
          {/* Dropdown Content */}
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-20">
            <div className="py-1">
              {/* User Info Header */}
              <div className="px-4 py-3 border-b border-gray-100">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                    {getInitials()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {getDisplayName()}
                    </div>
                    <div className="text-xs text-gray-500 truncate">
                      {getUserEmail()}
                    </div>
                    {!isEmailConfirmed() && (
                      <div className="text-xs text-amber-600 mt-1">
                        ⚠️ Email not verified
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Account Status */}
              <div className="px-4 py-2 text-xs text-gray-500 bg-gray-50">
                <div className="flex items-center justify-between">
                  <span>Account Status</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    isEmailConfirmed() 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {isEmailConfirmed() ? 'Verified' : 'Unverified'}
                  </span>
                </div>
              </div>

              {/* Menu Items */}
              <div className="py-1">
                {!isEmailConfirmed() && (
                  <button
                    onClick={() => {
                      // TODO: Implement resend verification
                      setIsDropdownOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-amber-700 hover:bg-amber-50 focus:outline-none focus:bg-amber-50 transition-colors"
                  >
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      Resend Verification
                    </div>
                  </button>
                )}

                <a
                  href="/profile"
                  onClick={(e) => {
                    e.preventDefault();
                    onNavigate && onNavigate('profile');
                    setIsDropdownOpen(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 transition-colors block"
                >
                  <div className="flex items-center">
                    <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Edit Profile
                  </div>
                </a>

                <a
                  href="/settings"
                  onClick={(e) => {
                    e.preventDefault();
                    onNavigate && onNavigate('settings');
                    setIsDropdownOpen(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 transition-colors block"
                >
                  <div className="flex items-center">
                    <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Settings
                  </div>
                </a>
              </div>

              {/* Divider */}
              <div className="border-t border-gray-100"></div>

              {/* Sign Out */}
              <button
                onClick={handleSignOut}
                className="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50 focus:outline-none focus:bg-red-50 transition-colors"
              >
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign Out
                </div>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default UserProfile;
