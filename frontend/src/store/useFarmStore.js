import { create } from 'zustand';
import { apiGet, apiPost } from '../api/http.js';

const initialState = {
  farm: null,
  loading: false,
  action: null,
  error: null,
  lastMessage: null,
};

export const useFarmStore = create((set) => ({
  ...initialState,
  reset: () => set(() => ({ ...initialState })),

  fetchFarm: async (playerId) => {
    if (!Number.isFinite(playerId)) {
      set({ error: 'Player ID is not set.', farm: null });
      return null;
    }
    set({ loading: true, error: null });
    try {
      const farm = await apiGet(`/farm/${playerId}`);
      set({ farm, loading: false, error: null });
      return farm;
    } catch (error) {
      const message = error?.message ?? 'Не вдалося завантажити ферму.';
      set({ error: message, loading: false });
      throw error;
    }
  },

  plantCrop: async (playerId, plotId, plantTypeId) => {
    set({ action: 'plant', error: null });
    try {
      const response = await apiPost(`/farm/${playerId}/plant`, {
        plot_id: plotId,
        plant_type_id: plantTypeId,
      });
      set({
        farm: response.state,
        action: null,
        lastMessage: response.message,
      });
      return response;
    } catch (error) {
      set({ action: null, error: error?.message ?? 'Не вдалося посадити рослину.' });
      throw error;
    }
  },

  harvestCrop: async (playerId, plotId) => {
    set({ action: 'harvest', error: null });
    try {
      const response = await apiPost(`/farm/${playerId}/harvest`, {
        plot_id: plotId,
      });
      set({
        farm: response.state,
        action: null,
        lastMessage: response.message,
      });
      return response;
    } catch (error) {
      set({ action: null, error: error?.message ?? 'Не вдалося зібрати врожай.' });
      throw error;
    }
  },

  unlockPlot: async (playerId, plotId) => {
    set({ action: 'unlock', error: null });
    try {
      const response = await apiPost(`/farm/${playerId}/plots/${plotId}/unlock`);
      set({
        farm: response.state,
        action: null,
        lastMessage: response.message,
      });
      return response;
    } catch (error) {
      set({ action: null, error: error?.message ?? 'Не вдалося відкрити ділянку.' });
      throw error;
    }
  },

  upgradeTool: async (playerId) => {
    set({ action: 'upgrade', error: null });
    try {
      const response = await apiPost(`/farm/${playerId}/tool/upgrade`);
      set({
        farm: response.state,
        action: null,
        lastMessage: response.message,
      });
      return response;
    } catch (error) {
      set({ action: null, error: error?.message ?? 'Не вдалося покращити інструмент.' });
      throw error;
    }
  },

  refillEnergy: async (playerId, amount) => {
    set({ action: 'refill', error: null });
    try {
      const response = await apiPost(`/farm/${playerId}/energy/refill`, {
        amount,
      });
      set({
        farm: response.state,
        action: null,
        lastMessage: response.message,
      });
      return response;
    } catch (error) {
      set({ action: null, error: error?.message ?? 'Не вдалося поповнити енергію.' });
      throw error;
    }
  },
}));
