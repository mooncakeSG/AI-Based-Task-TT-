import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key'

// Configuration check
console.log('🔧 Supabase Configuration:', {
  url: supabaseUrl,
  hasValidKey: supabaseAnonKey && supabaseAnonKey !== 'your-anon-key',
  keyLength: supabaseAnonKey?.length || 0
})

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
})

// Auth helper functions
export const auth = {
  // Sign up new user
  signUp: async (email, password, options = {}) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: options.metadata || {}
        }
      })
      
      // Enhanced error handling
      if (error) {
        console.error('Supabase SignUp Error:', error)
        if (error.status === 401) {
          return { data: null, error: { message: 'Authentication service unavailable. Please check your Supabase configuration.' } }
        }
      }
      
      return { data, error }
    } catch (err) {
      console.error('Network/Configuration Error:', err)
      return { data: null, error: { message: 'Unable to connect to authentication service. Please try again later.' } }
    }
  },

  // Sign in user
  signIn: async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })
      
      // Enhanced error handling
      if (error) {
        console.error('Supabase SignIn Error:', error)
        if (error.status === 401) {
          return { data: null, error: { message: 'Invalid credentials or authentication service unavailable.' } }
        }
      }
      
      return { data, error }
    } catch (err) {
      console.error('Network/Configuration Error:', err)
      return { data: null, error: { message: 'Unable to connect to authentication service. Please try again later.' } }
    }
  },

  // Sign out user
  signOut: async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  // Get current user
  getCurrentUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  },

  // Get current session
  getSession: async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    return { session, error }
  },

  // Listen to auth changes
  onAuthStateChange: (callback) => {
    return supabase.auth.onAuthStateChange(callback)
  }
}

// Database helper functions
export const database = {
  // Tasks operations
  tasks: {
    // Get all tasks for current user
    getAll: async () => {
      const { data, error } = await supabase
        .from('tasks')
        .select('*')
        .order('created_at', { ascending: false })
      return { data, error }
    },

    // Create new task
    create: async (taskData) => {
      const { data, error } = await supabase
        .from('tasks')
        .insert([taskData])
        .select()
      return { data: data?.[0], error }
    },

    // Update task
    update: async (id, updates) => {
      const { data, error } = await supabase
        .from('tasks')
        .update(updates)
        .eq('id', id)
        .select()
      return { data: data?.[0], error }
    },

    // Delete task
    delete: async (id) => {
      const { error } = await supabase
        .from('tasks')
        .delete()
        .eq('id', id)
      return { error }
    },

    // Subscribe to task changes
    subscribe: (callback) => {
      return supabase
        .channel('tasks')
        .on('postgres_changes', {
          event: '*',
          schema: 'public',
          table: 'tasks'
        }, callback)
        .subscribe()
    }
  },

  // Chat history operations
  chatHistory: {
    // Get chat history for current user
    getAll: async (limit = 50) => {
      const { data, error } = await supabase
        .from('chat_history')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)
      return { data, error }
    },

    // Save chat message
    save: async (messageData) => {
      const { data, error } = await supabase
        .from('chat_history')
        .insert([messageData])
        .select()
      return { data: data?.[0], error }
    },

    // Clear chat history
    clear: async () => {
      const { error } = await supabase
        .from('chat_history')
        .delete()
        .neq('id', 0) // Delete all records
      return { error }
    }
  },

  // File operations
  files: {
    // Get file records
    getAll: async () => {
      const { data, error } = await supabase
        .from('uploaded_files')
        .select('*')
        .order('created_at', { ascending: false })
      return { data, error }
    },

    // Save file record
    save: async (fileData) => {
      const { data, error } = await supabase
        .from('uploaded_files')
        .insert([fileData])
        .select()
      return { data: data?.[0], error }
    },

    // Upload file to storage
    upload: async (bucket, path, file) => {
      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(path, file)
      return { data, error }
    },

    // Get file URL
    getUrl: async (bucket, path) => {
      const { data } = supabase.storage
        .from(bucket)
        .getPublicUrl(path)
      return data.publicUrl
    }
  }
}

// Utility functions
export const utils = {
  // Check if user is authenticated
  isAuthenticated: async () => {
    const { session } = await auth.getSession()
    return !!session
  },

  // Get user ID
  getUserId: async () => {
    const { user } = await auth.getCurrentUser()
    return user?.id
  },

  // Format timestamp
  formatTimestamp: (timestamp) => {
    return new Date(timestamp).toLocaleString()
  },

  // Handle Supabase errors
  handleError: (error) => {
    console.error('Supabase error:', error)
    
    if (error?.message) {
      return error.message
    }
    
    if (error?.error_description) {
      return error.error_description
    }
    
    return 'An unexpected error occurred'
  }
}

export default supabase 