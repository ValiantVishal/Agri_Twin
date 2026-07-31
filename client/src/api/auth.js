import axios from "axios";

const API = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

export const registerUser = async (userData) => {
    return API.post("/register", userData);
};

export const loginUser = async (userData) => {
    return API.post("/login", userData);
};

export default API;