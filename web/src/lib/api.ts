import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add CORS headers
api.interceptors.request.use((config) => {
  config.headers['Access-Control-Allow-Origin'] = '*';
  config.headers['Access-Control-Allow-Methods'] =
    'GET, POST, PUT, DELETE, OPTIONS';
  config.headers['Access-Control-Allow-Headers'] =
    'Content-Type, Authorization';
  return config;
});

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  },
);
