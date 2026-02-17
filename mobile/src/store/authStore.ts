// Auth store with Zustand
import create from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface AuthState {
  isAuthed: boolean;
  user: any | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, firstName: string, lastName: string) => Promise<void>;
  logout: () => Promise<void>;
  initAuth: () => Promise<void>;
  setUser: (user: any) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthed: false,
  user: null,
  accessToken: null,
  refreshToken: null,

  login: async (email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      
      await SecureStore.setItemAsync('accessToken', data.access_token);
      await SecureStore.setItemAsync('refreshToken', data.refresh_token);
      
      set({
        isAuthed: true,
        user: data,
        accessToken: data.access_token,
        refreshToken: data.refresh_token
      });
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  register: async (email: string, username: string, password: string, firstName: string, lastName: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password, first_name: firstName, last_name: lastName })
      });
      const data = await response.json();
      
      await SecureStore.setItemAsync('accessToken', data.access_token);
      await SecureStore.setItemAsync('refreshToken', data.refresh_token);
      
      set({
        isAuthed: true,
        user: data,
        accessToken: data.access_token,
        refreshToken: data.refresh_token
      });
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('accessToken');
    await SecureStore.deleteItemAsync('refreshToken');
    set({
      isAuthed: false,
      user: null,
      accessToken: null,
      refreshToken: null
    });
  },

  initAuth: async () => {
    try {
      const accessToken = await SecureStore.getItemAsync('accessToken');
      if (accessToken) {
        set({ accessToken, isAuthed: true });
      }
    } catch (error) {
      console.error('Init auth error:', error);
    }
  },

  setUser: (user: any) => {
    set({ user });
  }
}));
