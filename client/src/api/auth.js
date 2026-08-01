import apiClient from "./apiClient";

export const registerUser = async (userData) => {
  return apiClient.post("/register", userData);
};

export const loginUser = async (userData) => {
  return apiClient.post("/login", userData);
};

export default apiClient;