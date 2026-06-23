import axios from 'axios';
import { initData } from './tg';

export const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string | undefined) ?? '',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  config.headers.Authorization = `tma ${initData}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg: string =
      err?.response?.data?.detail ?? err?.message ?? 'Request failed';
    return Promise.reject(new Error(msg));
  },
);
