export type Priority = 'low' | 'medium' | 'high' | 'urgent';
export type TodoFilter = 'all' | 'pending' | 'completed' | 'today' | 'overdue';

export interface User {
  id: string;
  telegram_id: number;
  username?: string;
  first_name: string;
  last_name?: string;
  created_at: string;
}

export interface Category {
  id: string;
  user_id: string;
  name: string;
  color: string;
  icon: string;
  todo_count?: number;
  created_at: string;
}

export interface Todo {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  category_id?: string;
  categories?: Category;
  priority: Priority;
  deadline?: string;
  is_completed: boolean;
  completed_at?: string;
  created_at: string;
}

export interface WeeklyPoint {
  date: string;
  count: number;
}

export interface CategoryStat {
  name: string;
  color: string;
  icon: string;
  count: number;
}

export interface Stats {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
  completion_rate: number;
  weekly: WeeklyPoint[];
  streak: number;
  most_productive_day: string | null;
  by_category: CategoryStat[];
}

export interface TodoFormData {
  title: string;
  description?: string;
  category_id?: string;
  priority: Priority;
  deadline?: string;
  reminder_at?: string;
}
