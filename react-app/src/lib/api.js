// API Configuration - Updated with CORS fix
// Try Fly.io first, fallback to Render
const DEFAULT_BACKENDS = [
  'https://intelliassist-backend.fly.dev',
  'https://intelliassist-bxl3.onrender.com'
];

const BACKEND_BASE = import.meta.env.VITE_API_BASE_URL || DEFAULT_BACKENDS[0];
const API_BASE_URL = `${BACKEND_BASE}/api/v1`;

console.log('API Base URL:', API_BASE_URL);
console.log('Backend:', BACKEND_BASE);

// Helper function to make API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`Making API call to: ${url}`);
  
  // Only add Content-Type for requests with body data
  const headers = { ...options.headers };
  if (options.body && typeof options.body === 'string') {
    headers['Content-Type'] = 'application/json';
  }
  
  const config = {
    headers,
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error(`API call failed for ${url}:`, error);
    throw error;
  }
};

// Specific API endpoints
export const api = {
  // Tasks
  getTasks: () => apiCall('/tasks'),
  createTask: (taskData) => apiCall('/tasks', {
    method: 'POST',
    body: JSON.stringify(taskData),
  }),
  updateTask: (taskId, updates) => apiCall(`/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  }),
  deleteTask: (taskId) => apiCall(`/tasks/${taskId}`, {
    method: 'DELETE',
  }),
  clearAllTasks: () => apiCall('/tasks', {
    method: 'DELETE',
  }),
  
  // Chat
  chat: (messageData) => apiCall('/chat', {
    method: 'POST',
    body: JSON.stringify(messageData),
  }),
  
  // Multimodal
  multimodal: (formData) => apiCall('/multimodal', {
    method: 'POST',
    body: formData,
    headers: {}, // Let browser set Content-Type for FormData
  }),
  
  // Upload
  uploadFile: (formData) => apiCall('/upload', {
    method: 'POST',
    body: formData,
    headers: {}, // Let browser set Content-Type for FormData
  }),
  
  uploadAudio: (formData) => apiCall('/upload/audio', {
    method: 'POST',
    body: formData,
    headers: {}, // Let browser set Content-Type for FormData
  }),
};

export { API_BASE_URL }; 