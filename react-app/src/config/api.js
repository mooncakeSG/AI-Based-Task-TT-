// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Chat endpoints
  chat: `${API_BASE_URL}/api/v1/chat`,
  multimodal: `${API_BASE_URL}/api/v1/multimodal`,
  
  // Task endpoints
  tasks: `${API_BASE_URL}/api/v1/tasks`,
  
  // Upload endpoints
  upload: `${API_BASE_URL}/api/v1/upload`,
  uploadFile: `${API_BASE_URL}/api/v1/upload/file`,
  uploadAudio: `${API_BASE_URL}/api/v1/upload/audio`,
  
  // Health endpoints
  health: `${API_BASE_URL}/ping`,
  status: `${API_BASE_URL}/api/v1/status`,
};

export default API_BASE_URL; 