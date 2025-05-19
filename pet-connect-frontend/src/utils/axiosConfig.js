// src/utils/axiosConfig.js
import axios from 'axios';
// Ensure API_BASE_URL doesn't end with a slash
const API_BASE_URL = process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL.replace(/\/$/, '') : '/api';

// Create an axios instance
const api = axios.create({
  baseURL: API_BASE_URL
});

// Add request debugging
api.interceptors.request.use(
  config => {
    console.log('API Request:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data
    });
    
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response debugging
api.interceptors.response.use(
  response => {
    console.log('API Response:', {
      status: response.status,
      headers: response.headers,
      url: response.config.url,
      method: response.config.method,
      data: response.data
    });
    return response;
  },
  async error => {
    console.error('API Response Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    });
    }
)

// Add a request interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  response => {
    return response;
  },
  async error => {
    const originalRequest = error.config;
    
    // If the error response is 401 and hasn't already been retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/users/token/refresh/`, {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        // Update the authorization header
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, log out the user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;