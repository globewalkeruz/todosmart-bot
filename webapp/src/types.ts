export type Priority = 'low' | 'medium' | 'high' | 'urgent';
export type Status = 'pending' | 'completed';

export interface Task {
  task_id: string;
  title: string;
  priority: Priority;
  status: Status;
  due_date: string | null;
  created_at: string;
}
