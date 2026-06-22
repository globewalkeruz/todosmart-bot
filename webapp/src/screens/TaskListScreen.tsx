import { useEffect, useState } from 'react';
import type { Task } from '../types';
import { api } from '../api';
import TaskItem from '../components/TaskItem';

interface Props {
  onAdd: () => void;
}

type Tab = 'pending' | 'completed';

export default function TaskListScreen({ onAdd }: Props) {
  const [tab, setTab] = useState<Tab>('pending');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .list(tab)
      .then(setTasks)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tab]);

  async function handleComplete(id: string) {
    await api.complete(id);
    setTasks((ts) => ts.filter((t) => t.task_id !== id));
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('medium');
  }

  async function handleDelete(id: string) {
    await api.delete(id);
    setTasks((ts) => ts.filter((t) => t.task_id !== id));
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light');
  }

  return (
    <div className="screen">
      <header className="header">
        <span className="header-title">📋 My Tasks</span>
        <button className="add-fab" onClick={onAdd} aria-label="Add task">
          +
        </button>
      </header>

      <div className="tabs">
        <button
          className={`tab${tab === 'pending' ? ' active' : ''}`}
          onClick={() => setTab('pending')}
        >
          Pending
        </button>
        <button
          className={`tab${tab === 'completed' ? ' active' : ''}`}
          onClick={() => setTab('completed')}
        >
          Completed
        </button>
      </div>

      <div className="task-list">
        {loading && <p className="empty">Loading…</p>}
        {error && <p className="empty error-text">{error}</p>}
        {!loading && !error && tasks.length === 0 && (
          <p className="empty">
            {tab === 'pending'
              ? '🎉 No pending tasks!\nTap + to add one.'
              : '📭 No completed tasks yet.'}
          </p>
        )}
        {tasks.map((task) => (
          <TaskItem
            key={task.task_id}
            task={task}
            onComplete={tab === 'pending' ? () => handleComplete(task.task_id) : undefined}
            onDelete={() => handleDelete(task.task_id)}
          />
        ))}
      </div>
    </div>
  );
}
