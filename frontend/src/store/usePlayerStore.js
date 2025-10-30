import { create } from 'zustand';
import { apiGet, apiPost } from '../api/http.js';

const initialState = {
  playerId: 1,
  dashboard: null,
  loadingDashboard: false,
  error: null,
};

export const usePlayerStore = create((set, get) => ({
  ...initialState,
  setPlayerId: (playerId) =>
    set(() => ({
      playerId: Number.isFinite(playerId) ? Number(playerId) : null,
    })),
  fetchDashboard: async () => {
    const { playerId } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Player ID is not set.', dashboard: null });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      const dashboard = await apiGet(`/player/${playerId}/dashboard`);
      set({ dashboard, loadingDashboard: false, error: null });
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Failed to load dashboard.',
      });
    }
  },
  claimDaily: async () => {
    const { playerId, fetchDashboard } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Player ID is not set.' });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      await apiPost(`/player/${playerId}/claim-daily-reward`);
      await fetchDashboard();
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Failed to claim daily reward.',
      });
    }
  },
  choose: async (choiceId) => {
    const { playerId, fetchDashboard } = get();
    if (!Number.isFinite(playerId)) {
      set({ error: 'Player ID is not set.' });
      return;
    }

    set({ loadingDashboard: true, error: null });

    try {
      await apiPost(`/player/${playerId}/quest/choose`, { choiceId });
      await fetchDashboard();
    } catch (error) {
      set({
        loadingDashboard: false,
        error: error?.message ?? 'Failed to submit choice.',
      });
    }
  },
}));
