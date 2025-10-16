import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout to 30 seconds for ML processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const faceRecognitionAPI = {
  // Health check
  healthCheck: () => api.get('/health'),
  
  // Recognize faces in uploaded image
  recognizeFace: (file, threshold = 0.8) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('threshold', threshold);
    
    return api.post('/recognize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Add a new face to the database
  addFace: (name, file) => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);
    
    return api.post('/faces', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get all faces from database
  getFaces: () => api.get('/faces'),

  // Delete a face from database
  deleteFace: (faceId) => api.delete(`/faces/${faceId}`),

  // Get recognition logs
  getLogs: () => api.get('/logs'),
};

export default api;
