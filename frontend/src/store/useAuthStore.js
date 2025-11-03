import { create } from 'zustand';
import { apiPost, setAuthToken } from '../api/http.js';
import { usePlayerStore } from './usePlayerStore.js';

const STORAGE_KEY = 'ultimate-app-session';

const initialState = {
  token: null,
  user: null,
  player: null,
  loading: false,
  error: null,
};

function persistSession(data) {
  if (typeof window === 'undefined') return;
  if (!data) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function readPersistedSession() {
  if (typeof window === 'undefined') return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export const useAuthStore = create((set, get) => ({
  ...initialState,

  hydrate: () => {
    const persisted = readPersistedSession();
    if (!persisted || !persisted.token || !persisted.user) {
      return;
    }
    setAuthToken(persisted.token);
    usePlayerStore.getState().applyAuthSession(persisted.player ?? null);
    set({
      token: persisted.token,
      user: persisted.user,
      player: persisted.player ?? null,
      loading: false,
      error: null,
    });
  },

  setSession: (session) => {
    if (!session || !session.access_token || !session.user) {
      setAuthToken(null);
      usePlayerStore.getState().clear();
      persistSession(null);
      set({ ...initialState });
      return;
    }

    const playerProfile = session.player ?? null;
    setAuthToken(session.access_token);
    usePlayerStore.getState().applyAuthSession(playerProfile);
    persistSession({
      token: session.access_token,
      user: session.user,
      player: playerProfile,
    });
    set({
      token: session.access_token,
      user: session.user,
      player: playerProfile,
      loading: false,
      error: null,
    });
  },

  register: async (payload) => {
    set({ loading: true, error: null });
    try {
      const session = await apiPost('/auth/register', payload);
      get().setSession(session);
      return session;
    } catch (error) {
      const message = error?.details || error?.message || 'Не вдалося створити героя.';
      set({ loading: false, error: message });
      throw error;
    }
  },

  login: async (payload) => {
    set({ loading: true, error: null });
    try {
      const session = await apiPost('/auth/login', payload);
      get().setSession(session);
      return session;
    } catch (error) {
      const message = error?.details || error?.message || 'Не вдалося виконати вхід.';
      set({ loading: false, error: message });
      throw error;
    }
  },

  clearError: () => set({ error: null }),

  logout: () => {
    setAuthToken(null);
    usePlayerStore.getState().clear();
    persistSession(null);
    set({ ...initialState });
  },
}));
