import { useState } from 'react';
import type { Task } from '../types';

const PRIORITY_ICON: Record<string, string> = {
  urgent: '🚨',
  high: '🔴',
  medium: '🟡',
  low: '🟢',
};

interface Props {
  task: Task;
  onComplete?: () => Promise<void>;
  onDelete: () => Promise<void>;
}

export default function TaskItem({ task, onComplete, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handle(fn: () => Promise<void>) {
    if (busy) return;
    setBusy(true);
    try {
      await fn();
    } finally {
      setBusy(false);
    }
  }

  const due = task.due_date
    ? new Date(task.due_date).toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
      })
    : null;

  return (
    <div className={`task-item${task.status === 'completed' ? ' done' : ''}`}>
      <div className="task-row" onClick={() => setExpanded((e) => !e)}>
        <span className="task-icon">{PRIORITY_ICON[task.priority] ?? '🟡'}</span>
        <span className="task-title">{task.title}</span>
        {due && <span className="task-due">{due}</span>}
        <span className="task-chevron">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="task-actions">
          {onComplete && (
            <button
              className="act-btn act-complete"
              disabled={busy}
              onClick={() => handle(onComplete)}
            >
              ✅ Done
            </button>
          )}
          <button
            className="act-btn act-delete"
            disabled={busy}
            onClick={() => handle(onDelete)}
          >
            🗑️ Delete
          </button>
        </div>
      )}
    </div>
  );
}
