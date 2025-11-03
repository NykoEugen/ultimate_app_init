import { create } from 'zustand';
import { apiGet, apiPost } from '../api/http.js';

const initialState = {
  playerId: null,
  profile: null,
  dashboard: null,
  loadingDashboard: false,
  error: null,
};

export const usePlayerStore = create((set, get) => ({
  ...initialState,

  applyAuthSession: (profile) =>
    set(() => ({
      playerId: profile?.player_id ?? null,
      profile: profile ?? null,
      dashboard: null,
      error: null,
    })),

  setPlayerId: (playerId) =>
    set(() => ({
      playerId: Number.isFinite(playerId) ? Number(playerId) : null,
    })),

  setProfile: (profile) =>
    set(() => ({
      profile: profile ?? null,
    })),

  clear: () => set({ ...initialState }),

  fetchDashboard: async () => {
    const { playerId } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Ідентифікатор героя не заданий.', dashboard: null });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      const dashboard = await apiGet(`/player/${playerId}/dashboard`);
      set({ dashboard, loadingDashboard: false, error: null });
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Не вдалося завантажити дашборд.',
      });
    }
  },

  claimDaily: async () => {
    const { playerId, fetchDashboard } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Ідентифікатор героя не заданий.' });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      await apiPost(`/player/${playerId}/claim-daily-reward`);
      await fetchDashboard();
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Не вдалося отримати щоденну нагороду.',
      });
    }
  },

  choose: async (choiceId) => {
    const { playerId, fetchDashboard } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Ідентифікатор героя не заданий.' });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      await apiPost(`/player/${playerId}/quest/choose`, { choiceId });
      await fetchDashboard();
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Не вдалося обробити вибір.',
      });
    }
  },
}));
