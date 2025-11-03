import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Retry logic for failed requests
const retryRequest = async (error) => {
  const config = error.config;
  
  // Initialize retry count
  if (!config.__retryCount) {
    config.__retryCount = 0;
  }
  
  // Check if we should retry
  const shouldRetry = 
    config.__retryCount < MAX_RETRIES &&
    error.response?.status >= 500 && // Retry only on server errors
    error.response?.status !== 501; // Don't retry "Not Implemented"
  
  if (!shouldRetry) {
    return Promise.reject(error);
  }
  
  config.__retryCount += 1;
  
  // Exponential backoff
  const delay = RETRY_DELAY * Math.pow(2, config.__retryCount - 1);
  
  console.log(`Retrying request (${config.__retryCount}/${MAX_RETRIES}) after ${delay}ms...`);
  
  await new Promise(resolve => setTimeout(resolve, delay));
  
  return api.request(config);
};

// Add response interceptor for error handling and retry logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Network errors or timeout
    if (!error.response) {
      console.error('Network error or timeout:', error.message);
      // Retry network errors
      if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
        return retryRequest(error);
      }
    }
    
    // Server errors (5xx) - retry
    if (error.response?.status >= 500) {
      return retryRequest(error);
    }
    
    return Promise.reject(error);
  }
);

// Projects
export const projectsApi = {
  getAll: () => api.get('/projects'),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Scans
export const scansApi = {
  create: (data) => api.post('/scans', data),
  getById: (id) => api.get(`/scans/${id}`),
  getByProject: (projectId) => api.get(`/scans/project/${projectId}`),
  run: (id) => api.post(`/scans/${id}/run`),
  getAISuggestions: (id) => api.post(`/scans/${id}/ai-suggestions`, {}, { timeout: 60000 }), // 60s timeout for LLM
};

export default api;
