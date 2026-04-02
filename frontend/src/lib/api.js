import axios from "axios";


const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL;

export const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 second timeout
});

export const loginApi = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 second timeout
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
      error.message = 'Request timeout. Please try again.';
    } else if (!error.response) {
      console.error('Network error');
      error.message = 'Network error. Please check your connection.';
    }
    return Promise.reject(error);
  }
);

export const withAuth = (token) => ({
  headers: {
    Authorization: `Bearer ${token}`,
  },
});