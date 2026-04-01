import axios from "axios";


const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL;

export const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export const loginApi = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const withAuth = (token) => ({
  headers: {
    Authorization: `Bearer ${token}`,
  },
});