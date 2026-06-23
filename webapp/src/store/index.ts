import { create } from 'zustand';
import type { User, TodoFilter } from '../types';

interface BottomSheetState {
  isOpen: boolean;
  todoId: string | null;
}

interface AppState {
  user: User | null;
  setUser: (user: User) => void;

  activeTab: 'home' | 'todos' | 'categories' | 'stats';
  setActiveTab: (tab: AppState['activeTab']) => void;

  filter: TodoFilter;
  setFilter: (f: TodoFilter) => void;

  activeCategoryId: string | null;
  setActiveCategoryId: (id: string | null) => void;

  todoSheet: BottomSheetState;
  openTodoSheet: (todoId?: string) => void;
  closeTodoSheet: () => void;

  categorySheet: { isOpen: boolean; categoryId: string | null };
  openCategorySheet: (categoryId?: string) => void;
  closeCategorySheet: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),

  activeTab: 'home',
  setActiveTab: (tab) => set({ activeTab: tab }),

  filter: 'all',
  setFilter: (filter) => set({ filter }),

  activeCategoryId: null,
  setActiveCategoryId: (id) => set({ activeCategoryId: id }),

  todoSheet: { isOpen: false, todoId: null },
  openTodoSheet: (todoId) =>
    set({ todoSheet: { isOpen: true, todoId: todoId ?? null } }),
  closeTodoSheet: () =>
    set({ todoSheet: { isOpen: false, todoId: null } }),

  categorySheet: { isOpen: false, categoryId: null },
  openCategorySheet: (categoryId) =>
    set({ categorySheet: { isOpen: true, categoryId: categoryId ?? null } }),
  closeCategorySheet: () =>
    set({ categorySheet: { isOpen: false, categoryId: null } }),
}));
