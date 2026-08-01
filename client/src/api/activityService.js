import { get, set, del, keys } from "idb-keyval";
import apiClient from "./apiClient";

const OFFLINE_ACTIVITY_PREFIX = "activity_";

export const activityService = {
  syncWithServer: async (activity) => {
    try {
      const response = await apiClient.post("/api/activity-log", {
        plot_id: activity.plot_id,
        entry_text: activity.entry_text,
        entry_language: activity.entry_language,
        input_mode: activity.input_mode,
        created_at: activity.created_at,
      });
      const updatedActivity = { ...activity, synced: true, id: response.data.id };
      await set(`${OFFLINE_ACTIVITY_PREFIX}${activity.client_id}`, updatedActivity);
      return { success: true, data: response.data };
    } catch (error) {
      console.error("Sync failed for activity:", activity.client_id, error);
      return { success: false, error };
    }
  },

  saveActivityLocally: async (activity) => {
    const client_id = crypto.randomUUID();
    const localActivity = {
      ...activity,
      client_id,
      synced: false,
      created_at: activity.created_at || new Date().toISOString(),
    };
    await set(`${OFFLINE_ACTIVITY_PREFIX}${client_id}`, localActivity);

    if (navigator.onLine) {
      const res = await activityService.syncWithServer(localActivity);
      if (res.success) {
        return { ...localActivity, synced: true, id: res.data.id };
      }
    }
    return localActivity;
  },

  getActivities: async (plotId = null) => {
    if (navigator.onLine) {
      try {
        const params = {};
        if (plotId) params.plot_id = plotId;
        const response = await apiClient.get("/api/activity-log", { params });
        const serverActivities = response.data;

        for (const act of serverActivities) {
          // Use server ID to check if it's already cached.
          // Store key as client_id (or server ID if client_id not available)
          const key = `${OFFLINE_ACTIVITY_PREFIX}srv_${act.id}`;
          await set(key, {
            ...act,
            client_id: `srv_${act.id}`,
            synced: true,
          });
        }
      } catch (error) {
        console.error("Failed to fetch activities from server, using local cache", error);
      }
    }

    const localKeys = await keys();
    const actKeys = localKeys.filter((key) => key.startsWith(OFFLINE_ACTIVITY_PREFIX));
    const allActivities = [];

    for (const key of actKeys) {
      const act = await get(key);
      if (act) {
        if (plotId && act.plot_id !== plotId) continue;
        allActivities.push(act);
      }
    }

    // Sort by created_at desc
    allActivities.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return allActivities;
  },

  syncOfflineQueue: async () => {
    const localKeys = await keys();
    const actKeys = localKeys.filter((key) => key.startsWith(OFFLINE_ACTIVITY_PREFIX));
    let syncCount = 0;

    for (const key of actKeys) {
      const act = await get(key);
      if (act && !act.synced && !key.startsWith(`${OFFLINE_ACTIVITY_PREFIX}srv_`)) {
        const res = await activityService.syncWithServer(act);
        if (res.success) {
          syncCount++;
        }
      }
    }
    return syncCount;
  },
};

if (typeof window !== "undefined") {
  window.addEventListener("online", () => {
    activityService.syncOfflineQueue().catch(console.error);
  });
}
