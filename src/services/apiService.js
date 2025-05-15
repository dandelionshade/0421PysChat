import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api'; // Adjust API base URL as needed

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// User APIs
export const loginUser = (credentials) => apiClient.post('/user/login', credentials);
export const registerUser = (userData) => apiClient.post('/user/register', userData);
export const getUserInfo = () => apiClient.get('/user/info');
export const updateUserInfo = (userData) => apiClient.put('/user/update', userData);
export const logoutUser = () => apiClient.post('/user/logout'); // Assuming a logout endpoint

// Psychologist APIs
export const getPsychologistList = (params) => apiClient.get('/psychologist/list', { params });
export const getPsychologistDetail = (id) => apiClient.get(`/psychologist/detail/${id}`);
export const getRecommendedPsychologists = () => apiClient.get('/psychologist/recommend');

// Chat APIs
export const getChatHistory = (params) => apiClient.get('/chat/history', { params }); // e.g., { userId, psychologistId }
export const sendMessage = (messageData, sessionId = null) => {
  const payload = { message: messageData };

  // Include sessionId if provided
  if (sessionId) {
    payload.session_id = sessionId;
  }

  return apiClient.post('/chat/send', payload);
};
export const createChatSession = (name = 'New Conversation') =>
  apiClient.post('/chat/sessions', { name });
export const getUnreadMessages = () => apiClient.get('/chat/unread');

// Order APIs
export const createOrder = (orderData) => apiClient.post('/order/create', orderData);
export const getUserOrders = (params) => apiClient.get('/order/list', { params });
export const getOrderDetail = (id) => apiClient.get(`/order/detail/${id}`);
export const cancelOrder = (id) => apiClient.put(`/order/cancel/${id}`);

// Admin: User Management APIs
export const adminGetUserList = (params) => apiClient.get('/admin/user/list', { params });
export const adminDeleteUser = (id) => apiClient.delete(`/admin/user/delete/${id}`);
export const adminUpdateUser = (id, userData) => apiClient.put(`/admin/user/update/${id}`, userData); // Assuming endpoint

// Admin: Psychologist Management APIs
export const adminAddPsychologist = (psychologistData) => apiClient.post('/admin/psychologist/add', psychologistData);
export const adminUpdatePsychologist = (id, psychologistData) => apiClient.put(`/admin/psychologist/update/${id}`, psychologistData); // Assuming endpoint
export const adminDeletePsychologist = (id) => apiClient.delete(`/admin/psychologist/delete/${id}`);
export const adminGetPsychologistList = (params) => apiClient.get('/admin/psychologist/list', { params }); // Might be same as user-facing or specific admin one

// Admin: Order Management APIs
export const adminGetOrderList = (params) => apiClient.get('/admin/order/list', { params });
export const adminUpdateOrder = (id, orderData) => apiClient.put(`/admin/order/update/${id}`, orderData); // Assuming endpoint
export const adminDeleteOrder = (id) => apiClient.delete(`/admin/order/delete/${id}`); // Assuming endpoint

// Admin: Content/Article Management APIs (Interpreted from "内容管理")
export const getArticleList = (params) => apiClient.get('/article/list', { params });
export const getArticleDetail = (id) => apiClient.get(`/article/detail/${id}`);
export const adminAddArticle = (articleData) => apiClient.post('/admin/article/add', articleData);
export const adminUpdateArticle = (id, articleData) => apiClient.put(`/admin/article/update/${id}`, articleData);
export const adminDeleteArticle = (id) => apiClient.delete(`/admin/article/delete/${id}`);

export default apiClient;
