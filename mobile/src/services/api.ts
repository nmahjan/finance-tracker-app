// API service with WebSocket support
import axios from 'axios';
import { io } from 'socket.io-client';
import { useAuthStore } from '../store/authStore';

const API_URL = 'http://localhost:5000/api/v1';
let socket: any = null;

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const accessToken = useAuthStore((state) => state.accessToken);
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export const initializeAPI = () => {
  // Connect to WebSocket for real-time updates
  const accessToken = useAuthStore((state) => state.accessToken);
  if (accessToken) {
    socket = io('http://localhost:5000', {
      auth: { token: accessToken }
    });

    socket.on('connected', (data: any) => {
      console.log('Connected to real-time updates:', data);
    });

    socket.on('transaction_update', (data: any) => {
      console.log('New transaction:', data);
    });

    socket.on('balance_update', (data: any) => {
      console.log('Balance updated:', data);
    });

    socket.on('budget_alert', (data: any) => {
      console.log('Budget alert:', data);
    });

    socket.on('bill_reminder', (data: any) => {
      console.log('Bill reminder:', data);
    });
  }
};

// Auth APIs
export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (email: string, username: string, password: string, firstName: string, lastName: string) =>
    apiClient.post('/auth/register', { email, username, password, first_name: firstName, last_name: lastName }),
  getProfile: () => apiClient.get('/auth/profile'),
  updateProfile: (data: any) => apiClient.put('/auth/profile', data)
};

// Transactions APIs
export const transactionsAPI = {
  create: (data: any) => apiClient.post('/transactions', data),
  list: (params: any) => apiClient.get('/transactions', { params }),
  get: (id: string) => apiClient.get(`/transactions/${id}`),
  update: (id: string, data: any) => apiClient.put(`/transactions/${id}`, data),
  delete: (id: string) => apiClient.delete(`/transactions/${id}`)
};

// Budgets APIs
export const budgetsAPI = {
  create: (data: any) => apiClient.post('/budgets', data),
  list: () => apiClient.get('/budgets'),
  get: (id: string) => apiClient.get(`/budgets/${id}`),
  update: (id: string, data: any) => apiClient.put(`/budgets/${id}`, data),
  delete: (id: string) => apiClient.delete(`/budgets/${id}`)
};

// Bills APIs
export const billsAPI = {
  create: (data: any) => apiClient.post('/bills', data),
  list: (params: any) => apiClient.get('/bills', { params }),
  get: (id: string) => apiClient.get(`/bills/${id}`),
  update: (id: string, data: any) => apiClient.put(`/bills/${id}`, data),
  markPaid: (id: string) => apiClient.post(`/bills/${id}/pay`),
  delete: (id: string) => apiClient.delete(`/bills/${id}`)
};

// Plaid APIs
export const plaidAPI = {
  createLinkToken: () => apiClient.post('/plaid/create-link-token'),
  exchangeToken: (publicToken: string) =>
    apiClient.post('/plaid/exchange-token', { public_token: publicToken }),
  getLinkedAccounts: () => apiClient.get('/plaid/accounts'),
  sync: () => apiClient.post('/plaid/sync'),
  disconnect: () => apiClient.post('/plaid/disconnect')
};

// Analytics APIs
export const analyticsAPI = {
  getSummary: () => apiClient.get('/analytics/summary'),
  getSpendingByCategory: (days: number = 30) =>
    apiClient.get('/analytics/spending-by-category', { params: { days } }),
  getMonthlyTrend: (months: number = 12) =>
    apiClient.get('/analytics/monthly-trend', { params: { months } }),
  getBudgetProgress: () => apiClient.get('/analytics/budget-progress')
};

export const getSocket = () => socket;

export default apiClient;
