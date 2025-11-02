import { create } from 'zustand';
import { apiGet, apiPost } from '../api/http.js';

const initialState = {
  data: null,
  loading: false,
  error: null,
};

export const useOnboardingStore = create((set, get) => ({
  ...initialState,

  fetch: async (playerId) => {
    if (!Number.isFinite(playerId)) {
      set({ data: null, error: null, loading: false });
      return null;
    }
    const { loading } = get();
    if (loading) return null;
    set({ loading: true, error: null });
    try {
      const data = await apiGet(`/player/${playerId}/onboarding`);
      set({ data, loading: false, error: null });
      return data;
    } catch (error) {
      set({ loading: false, error: error?.message ?? 'Не вдалося завантажити привітання.' });
      return null;
    }
  },

  complete: async (playerId) => {
    set({ loading: true, error: null });
    try {
      const data = await apiPost(`/player/${playerId}/onboarding/complete`);
      set({ data, loading: false, error: null });
      return data;
    } catch (error) {
      set({ loading: false, error: error?.message ?? 'Не вдалося завершити привітання.' });
      throw error;
    }
  },

  reset: () => set({ ...initialState }),
}));
