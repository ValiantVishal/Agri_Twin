import apiClient from "./apiClient";

export const aiService = {
  askAI: async (question, plotId = null) => {
    const response = await apiClient.post("/api/ai/ask", {
      question,
      plot_id: plotId || null,
    });
    return response.data;
  },

  getDailyBrief: async (plotId = null) => {
    const response = await apiClient.post("/api/ai/daily-brief", {
      plot_id: plotId || null,
    });
    return response.data;
  },

  getChatHistory: async (plotId = null) => {
    const params = {};
    if (plotId) params.plot_id = plotId;
    const response = await apiClient.get("/api/ai/chat-history", { params });
    return response.data;
  },
};
