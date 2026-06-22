import { initData } from './tg';
import type { Task } from './types';

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `tma ${initData}`,
      ...(opts?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(body || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  list: (status: 'pending' | 'completed' = 'pending') =>
    req<Task[]>(`/api/tasks/?status=${status}`),

  create: (data: { title: string; priority: string; due_date?: string }) =>
    req<Task>('/api/tasks/', { method: 'POST', body: JSON.stringify(data) }),

  complete: (id: string) =>
    req<Task>(`/api/tasks/${id}/complete`, { method: 'POST' }),

  delete: (id: string) =>
    req<void>(`/api/tasks/${id}`, { method: 'DELETE' }),

  updatePriority: (id: string, priority: string) =>
    req<Task>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ priority }),
    }),
};
