import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../lib/axios';
import { haptic } from '../lib/tg';
import { useStore } from '../store';
import type { Category } from '../types';

export function useCategories() {
  const user = useStore((s) => s.user);
  return useQuery<Category[], Error>({
    queryKey: ['categories', user?.id],
    queryFn: async () => {
      const res = await api.get<Category[]>(`/api/categories/${user!.id}`);
      return res.data;
    },
    enabled: !!user?.id,
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<Category, Error, { name: string; color: string; icon: string }>({
    mutationFn: (data) =>
      api.post<Category>('/api/categories/', data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories', user?.id] });
      haptic('success');
      toast.success('Category created!');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<
    Category,
    Error,
    { id: string; name?: string; color?: string; icon?: string }
  >({
    mutationFn: ({ id, ...data }) =>
      api.patch<Category>(`/api/categories/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories', user?.id] });
      haptic('medium');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<void, Error, string>({
    mutationFn: (id) => api.delete(`/api/categories/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories', user?.id] });
      qc.invalidateQueries({ queryKey: ['todos', user?.id] });
      haptic('tap');
      toast.success('Category deleted');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}
