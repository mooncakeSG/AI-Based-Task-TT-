import { useState, useEffect } from 'react';
import { auth } from '../lib/supabase';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const { session, error } = await auth.getSession();
        if (!error && session) {
          setSession(session);
          setUser(session.user);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error getting initial session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    getInitialSession();

    // Listen for auth changes
    const { data: authListener } = auth.onAuthStateChange(async (event, session) => {
      console.log('Auth state changed:', event, session?.user?.email);
      
      setSession(session);
      setUser(session?.user || null);
      setIsAuthenticated(!!session);
      setIsLoading(false);

      // Handle different auth events
      switch (event) {
        case 'SIGNED_IN':
          console.log('User signed in:', session.user.email);
          break;
        case 'SIGNED_OUT':
          console.log('User signed out');
          break;
        case 'TOKEN_REFRESHED':
          console.log('Token refreshed for:', session.user.email);
          break;
        default:
          break;
      }
    });

    // Cleanup listener on unmount
    return () => {
      authListener?.subscription?.unsubscribe?.();
    };
  }, []);

  const signOut = async () => {
    try {
      setIsLoading(true);
      const { error } = await auth.signOut();
      if (error) {
        console.error('Sign out error:', error);
        return { error };
      }
      return { error: null };
    } catch (error) {
      console.error('Sign out error:', error);
      return { error };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    user,
    session,
    isLoading,
    isAuthenticated,
    signOut
  };
}; 