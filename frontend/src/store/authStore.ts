import { create } from 'zustand'
import { User } from '../types'
import { authAPI } from '../services/api'

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await authAPI.login(email, password)
      localStorage.setItem('token', data.access_token)
      set({ user: data.user, token: data.access_token, isAuthenticated: true, isLoading: false })
    } catch (err: any) {
      set({ error: err.response?.data?.message || 'Login failed', isLoading: false })
    }
  },

  register: async (email, password, name) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await authAPI.register(email, password, name)
      localStorage.setItem('token', data.access_token)
      set({ user: data.user, token: data.access_token, isAuthenticated: true, isLoading: false })
    } catch (err: any) {
      set({ error: err.response?.data?.message || 'Registration failed', isLoading: false })
    }
  },

  logout: async () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false, error: null })
  },
}))