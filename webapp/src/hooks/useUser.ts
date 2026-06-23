import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/axios';
import { useStore } from '../store';
import type { User } from '../types';

export function useUser() {
  const setUser = useStore((s) => s.setUser);

  return useQuery<User, Error>({
    queryKey: ['user'],
    queryFn: async () => {
      const res = await api.post<User>('/api/auth/me');
      setUser(res.data);
      return res.data;
    },
    retry: 1,
    staleTime: Infinity,
  });
}
