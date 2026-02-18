import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  user_id: string;
  email: string;
  name: string;
  picture?: string;
  role: 'sender' | 'carrier' | 'admin';
  phone_whatsapp?: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  sessionToken: string | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setSessionToken: (token: string | null) => void;
  login: (user: User, token: string) => Promise<void>;
  logout: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  sessionToken: null,
  isLoading: true,

  setUser: (user) => set({ user }),
  
  setSessionToken: (token) => set({ sessionToken: token }),

  login: async (user, token) => {
    await AsyncStorage.setItem('session_token', token);
    await AsyncStorage.setItem('user', JSON.stringify(user));
    set({ user, sessionToken: token });
  },

  logout: async () => {
    await AsyncStorage.removeItem('session_token');
    await AsyncStorage.removeItem('user');
    set({ user: null, sessionToken: null });
  },

  initialize: async () => {
    try {
      const token = await AsyncStorage.getItem('session_token');
      const userStr = await AsyncStorage.getItem('user');
      
      if (token && userStr) {
        const user = JSON.parse(userStr);
        set({ user, sessionToken: token, isLoading: false });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      set({ isLoading: false });
    }
  },
}));