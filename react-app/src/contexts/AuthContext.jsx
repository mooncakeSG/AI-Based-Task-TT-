import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  // API base URL
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting session:', error);
        } else {
          setSession(session);
          setUser(session?.user ?? null);
        }
      } catch (error) {
        console.error('Error in getInitialSession:', error);
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email);
        
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);

        // Handle different auth events
        if (event === 'SIGNED_IN') {
          console.log('User signed in:', session?.user?.email);
        } else if (event === 'SIGNED_OUT') {
          console.log('User signed out');
        } else if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed');
        }
      }
    );

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  // Sign up with email and password
  const signUp = async (email, password, metadata = {}) => {
    try {
      setLoading(true);
      
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      });

      if (error) {
        throw error;
      }

      return { user: data.user, session: data.session, error: null };
    } catch (error) {
      console.error('Sign up error:', error);
      return { user: null, session: null, error };
    } finally {
      setLoading(false);
    }
  };

  // Sign in with email and password
  const signIn = async (email, password) => {
    try {
      setLoading(true);
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) {
        throw error;
      }

      return { user: data.user, session: data.session, error: null };
    } catch (error) {
      console.error('Sign in error:', error);
      return { user: null, session: null, error };
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const signOut = async () => {
    try {
      setLoading(true);
      
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        throw error;
      }

      setUser(null);
      setSession(null);
      
      return { error: null };
    } catch (error) {
      console.error('Sign out error:', error);
      return { error };
    } finally {
      setLoading(false);
    }
  };

  // Reset password
  const resetPassword = async (email) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      });

      if (error) {
        throw error;
      }

      return { error: null };
    } catch (error) {
      console.error('Reset password error:', error);
      return { error };
    }
  };

  // Update user profile
  const updateProfile = async (updates) => {
    try {
      setLoading(true);
      
      const { data, error } = await supabase.auth.updateUser({
        data: updates
      });

      if (error) {
        throw error;
      }

      return { user: data.user, error: null };
    } catch (error) {
      console.error('Update profile error:', error);
      return { user: null, error };
    } finally {
      setLoading(false);
    }
  };

  // Get access token for API calls
  const getAccessToken = async () => {
    try {
      if (!session) {
        return null;
      }

      const { data: { session: currentSession }, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Error getting access token:', error);
        return null;
      }

      return currentSession?.access_token || null;
    } catch (error) {
      console.error('Error in getAccessToken:', error);
      return null;
    }
  };

  // Make authenticated API calls
  const apiCall = async (endpoint, options = {}) => {
    try {
      const token = await getAccessToken();
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      };

      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };

  // Check if user is authenticated
  const isAuthenticated = () => {
    return !!(user && session);
  };

  // Check if email is confirmed
  const isEmailConfirmed = () => {
    return user?.email_confirmed_at != null;
  };

  // Get user metadata
  const getUserMetadata = () => {
    return user?.user_metadata || {};
  };

  // Get user ID
  const getUserId = () => {
    return user?.id;
  };

  // Get user email
  const getUserEmail = () => {
    return user?.email;
  };

  const value = {
    // State
    user,
    session,
    loading,
    initialized,
    
    // Actions
    signUp,
    signIn,
    signOut,
    resetPassword,
    updateProfile,
    
    // Utilities
    getAccessToken,
    apiCall,
    isAuthenticated,
    isEmailConfirmed,
    getUserMetadata,
    getUserId,
    getUserEmail,
    
    // Constants
    API_BASE_URL
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 