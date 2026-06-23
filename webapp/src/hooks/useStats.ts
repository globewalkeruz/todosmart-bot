import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/axios';
import { useStore } from '../store';
import type { Stats } from '../types';

export function useStats() {
  const user = useStore((s) => s.user);
  return useQuery<Stats, Error>({
    queryKey: ['stats', user?.id],
    queryFn: async () => {
      const res = await api.get<Stats>(`/api/stats/${user!.id}`);
      return res.data;
    },
    enabled: !!user?.id,
    staleTime: 30_000,
  });
}
