import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api', // This works with our Vite proxy configuration
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout (LLM responses can be slow)
});

export default {
  // Chat API
  sendMessage(message) {
    return api.post('/chat', { message });
  },
  
  // Resources API
  getResources(params = {}) {
    return api.get('/resources', { params });
  }
};
