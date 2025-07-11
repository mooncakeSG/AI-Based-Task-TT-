// API Configuration - FORCE Fly.io backend
// FIXED: Using only Fly.io backend (working CORS)
const BACKEND_BASE = 'https://intelliassist-backend.fly.dev';
const API_BASE_URL = `${BACKEND_BASE}/api/v1`;

console.log('🚀 FORCED API Base URL:', API_BASE_URL);
console.log('🚀 FORCED Backend:', BACKEND_BASE);
console.log('🚀 Environment override:', import.meta.env.VITE_API_BASE_URL);

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