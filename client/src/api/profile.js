import apiClient from "./apiClient";

export const saveProfile = (data) => {
  return apiClient.post("/profile", data);
};