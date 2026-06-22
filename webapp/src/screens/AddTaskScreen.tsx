import { useState } from 'react';
import { api } from '../api';

const PRIORITIES = ['low', 'medium', 'high', 'urgent'] as const;
const PRIORITY_LABEL: Record<string, string> = {
  low: '🟢 Low',
  medium: '🟡 Medium',
  high: '🔴 High',
  urgent: '🚨 Urgent',
};

interface Props {
  onDone: () => void;
  onBack: () => void;
}

export default function AddTaskScreen({ onDone, onBack }: Props) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await api.create({
        title: title.trim(),
        priority,
        due_date: dueDate || undefined,
      });
      window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success');
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add task');
      setSaving(false);
    }
  }

  return (
    <div className="screen">
      <header className="header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <span className="header-title">New Task</span>
      </header>

      <form className="add-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Task title</label>
          <input
            autoFocus
            className="input"
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Priority</label>
          <div className="priority-row">
            {PRIORITIES.map((p) => (
              <button
                type="button"
                key={p}
                className={`priority-pill${priority === p ? ' selected' : ''}`}
                onClick={() => setPriority(p)}
              >
                {PRIORITY_LABEL[p]}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Due date (optional)</label>
          <input
            className="input"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>

        {error && <div className="error-box">{error}</div>}

        <button
          type="submit"
          className="submit-btn"
          disabled={saving || !title.trim()}
        >
          {saving ? 'Adding…' : '✅ Add Task'}
        </button>
      </form>
    </div>
  );
}
