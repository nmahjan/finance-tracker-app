import axios from 'axios'
import { User, Account, Transaction, Budget, Bill, AuthResponse } from '../types'

const API_BASE = 'http://localhost:5000/api/v1'
export const apiClient = axios.create({ baseURL: API_BASE })

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authAPI = {
  login: (email: string, password: string) => apiClient.post<AuthResponse>('/auth/login', { email, password }),
  register: (email: string, password: string, name?: string) => apiClient.post<AuthResponse>('/auth/register', { email, password, name }),
  logout: () => apiClient.post('/auth/logout'),
}

export const accountsAPI = {
  list: () => apiClient.get<Account[]>('/accounts'),
}

export const transactionsAPI = {
  list: (accountId?: string) => apiClient.get<Transaction[]>('/transactions', { params: { account_id: accountId } }),
}