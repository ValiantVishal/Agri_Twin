import { get, set, del, keys } from "idb-keyval";
import apiClient from "./apiClient";

const OFFLINE_PLOT_PREFIX = "plot_";

export const getProfile = async () => {
  return apiClient.get("/profile");
};

export const plotService = {
  syncWithServer: async (plot) => {
    try {
      const response = await apiClient.post("/api/plots", {
        id: plot.id,
        plot_name: plot.plot_name,
        points: plot.points,
        area_sqm: plot.area_sqm,
        area_acres: plot.area_acres,
        area_cents: plot.area_cents,
        perimeter_m: plot.perimeter_m,
      });
      const updatedPlot = { ...plot, synced: true, warning: response.data.warning };
      await set(`${OFFLINE_PLOT_PREFIX}${plot.id}`, updatedPlot);
      return { success: true, data: response.data };
    } catch (error) {
      console.error("Sync failed for plot:", plot.id, error);
      return { success: false, error };
    }
  },

  savePlotLocally: async (plot) => {
    const localPlot = {
      ...plot,
      synced: false,
      created_at: plot.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
    };
    await set(`${OFFLINE_PLOT_PREFIX}${plot.id}`, localPlot);

    if (navigator.onLine) {
      const res = await plotService.syncWithServer(localPlot);
      if (res.success) {
        return { ...localPlot, synced: true, warning: res.data.warning };
      }
    }
    return localPlot;
  },

  getPlots: async () => {
    if (navigator.onLine) {
      try {
        const response = await apiClient.get("/api/plots");
        const serverPlots = response.data;

        for (const plot of serverPlots) {
          const cached = await get(`${OFFLINE_PLOT_PREFIX}${plot.id}`);
          if (cached && !cached.synced) continue;

          await set(`${OFFLINE_PLOT_PREFIX}${plot.id}`, {
            ...plot,
            synced: true,
          });
        }
      } catch (error) {
        console.error("Failed to fetch plots from server, using local cache", error);
      }
    }

    const localKeys = await keys();
    const plotKeys = localKeys.filter((key) => key.startsWith(OFFLINE_PLOT_PREFIX));
    const allPlots = [];

    for (const key of plotKeys) {
      const plot = await get(key);
      if (plot && plot.is_active) {
        allPlots.push(plot);
      }
    }

    allPlots.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return allPlots;
  },

  updatePlot: async (id, updatedFields) => {
    const existing = await get(`${OFFLINE_PLOT_PREFIX}${id}`);
    if (!existing) throw new Error("Plot not found locally");

    const updatedPlot = {
      ...existing,
      ...updatedFields,
      synced: false,
      updated_at: new Date().toISOString(),
    };

    await set(`${OFFLINE_PLOT_PREFIX}${id}`, updatedPlot);

    if (navigator.onLine) {
      try {
        const response = await apiClient.put(`/api/plots/${id}`, {
          plot_name: updatedPlot.plot_name,
          points: updatedPlot.points,
          area_sqm: updatedPlot.area_sqm,
          area_acres: updatedPlot.area_acres,
          area_cents: updatedPlot.area_cents,
          perimeter_m: updatedPlot.perimeter_m,
        });
        const synced = { ...updatedPlot, synced: true, warning: response.data.warning };
        await set(`${OFFLINE_PLOT_PREFIX}${id}`, synced);
        return synced;
      } catch (error) {
        console.error("Failed to sync update, saved offline:", error);
      }
    }
    return updatedPlot;
  },

  deletePlot: async (id) => {
    const existing = await get(`${OFFLINE_PLOT_PREFIX}${id}`);
    if (existing) {
      existing.is_active = false;
      existing.synced = false;
      await set(`${OFFLINE_PLOT_PREFIX}${id}`, existing);
    }

    if (navigator.onLine) {
      try {
        await apiClient.delete(`/api/plots/${id}`);
        await del(`${OFFLINE_PLOT_PREFIX}${id}`);
      } catch (error) {
        console.error("Failed to sync delete, queued offline:", error);
      }
    }
  },

  syncOfflineQueue: async () => {
    const localKeys = await keys();
    const plotKeys = localKeys.filter((key) => key.startsWith(OFFLINE_PLOT_PREFIX));
    let syncCount = 0;

    for (const key of plotKeys) {
      const plot = await get(key);
      if (plot && !plot.synced) {
        if (!plot.is_active) {
          try {
            await apiClient.delete(`/api/plots/${plot.id}`);
            await del(key);
            syncCount++;
          } catch (e) {
            console.error("Sync deletion failed:", e);
          }
        } else {
          const res = await plotService.syncWithServer(plot);
          if (res.success) {
            syncCount++;
          }
        }
      }
    }
    return syncCount;
  },
};

if (typeof window !== "undefined") {
  window.addEventListener("online", () => {
    plotService.syncOfflineQueue().catch(console.error);
  });
}
