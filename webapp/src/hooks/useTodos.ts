import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../lib/axios';
import { haptic } from '../lib/tg';
import { useStore } from '../store';
import type { Todo, TodoFormData } from '../types';

export function useTodos(status = 'all') {
  const user = useStore((s) => s.user);
  return useQuery<Todo[], Error>({
    queryKey: ['todos', user?.id, status],
    queryFn: async () => {
      const res = await api.get<Todo[]>(`/api/todos/${user!.id}`, {
        params: { status },
      });
      return res.data;
    },
    enabled: !!user?.id,
  });
}

export function useCreateTodo() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<Todo, Error, TodoFormData>({
    mutationFn: (data) => api.post<Todo>('/api/todos/', data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['todos', user?.id] });
      qc.invalidateQueries({ queryKey: ['stats', user?.id] });
      haptic('success');
      toast.success('Todo added!');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}

export function useUpdateTodo() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<Todo, Error, Partial<Todo> & { id: string }>({
    mutationFn: ({ id, ...data }) =>
      api.patch<Todo>(`/api/todos/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['todos', user?.id] });
      qc.invalidateQueries({ queryKey: ['stats', user?.id] });
      haptic('medium');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}

export function useDeleteTodo() {
  const qc = useQueryClient();
  const user = useStore((s) => s.user);
  return useMutation<void, Error, string>({
    mutationFn: (id) => api.delete(`/api/todos/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['todos', user?.id] });
      qc.invalidateQueries({ queryKey: ['stats', user?.id] });
      haptic('tap');
      toast.success('Deleted');
    },
    onError: (e) => {
      haptic('error');
      toast.error(e.message);
    },
  });
}
