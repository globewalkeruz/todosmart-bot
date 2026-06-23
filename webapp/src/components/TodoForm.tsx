import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import BottomSheet from './BottomSheet';
import { useCategories } from '../hooks/useCategories';
import { useCreateTodo, useTodos, useUpdateTodo } from '../hooks/useTodos';
import { useStore } from '../store';
import type { Priority, TodoFormData } from '../types';

const PRIORITIES: { value: Priority; label: string; emoji: string }[] = [
  { value: 'low',    label: 'Low',    emoji: '🟢' },
  { value: 'medium', label: 'Medium', emoji: '🟡' },
  { value: 'high',   label: 'High',   emoji: '🔴' },
  { value: 'urgent', label: 'Urgent', emoji: '⚡' },
];

function localDatetimeValue(iso?: string): string {
  if (!iso) return '';
  try {
    return format(new Date(iso), "yyyy-MM-dd'T'HH:mm");
  } catch {
    return '';
  }
}

export default function TodoForm() {
  const { todoSheet, closeTodoSheet } = useStore();
  const { data: allTodos } = useTodos();
  const { data: categories = [] } = useCategories();
  const createTodo = useCreateTodo();
  const updateTodo = useUpdateTodo();

  const editingTodo = allTodos?.find((t) => t.id === todoSheet.todoId) ?? null;
  const isEdit = !!editingTodo;

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [categoryId, setCategoryId] = useState<string | undefined>();
  const [deadline, setDeadline] = useState('');
  const [reminderAt, setReminderAt] = useState('');

  useEffect(() => {
    if (todoSheet.isOpen) {
      if (editingTodo) {
        setTitle(editingTodo.title);
        setDescription(editingTodo.description ?? '');
        setPriority(editingTodo.priority);
        setCategoryId(editingTodo.category_id);
        setDeadline(localDatetimeValue(editingTodo.deadline));
        setReminderAt('');
      } else {
        setTitle('');
        setDescription('');
        setPriority('medium');
        setCategoryId(undefined);
        setDeadline('');
        setReminderAt('');
      }
    }
  }, [todoSheet.isOpen, todoSheet.todoId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;

    const data: TodoFormData = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      category_id: categoryId,
      deadline: deadline ? new Date(deadline).toISOString() : undefined,
      reminder_at: reminderAt ? new Date(reminderAt).toISOString() : undefined,
    };

    if (isEdit) {
      await updateTodo.mutateAsync({ id: editingTodo.id, ...data });
    } else {
      await createTodo.mutateAsync(data);
    }
    closeTodoSheet();
  }

  const isPending = createTodo.isPending || updateTodo.isPending;

  return (
    <BottomSheet
      isOpen={todoSheet.isOpen}
      onClose={closeTodoSheet}
      title={isEdit ? 'Edit Todo' : 'New Todo'}
    >
      <form onSubmit={handleSubmit}>
        {/* Title */}
        <div className="form-group">
          <label className="form-label">Title *</label>
          <input
            className="form-input"
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
            required
          />
        </div>

        {/* Description */}
        <div className="form-group">
          <label className="form-label">Description (optional)</label>
          <textarea
            className="form-input form-textarea"
            placeholder="Add details…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Priority */}
        <div className="form-group">
          <label className="form-label">Priority</label>
          <div className="priority-grid">
            {PRIORITIES.map((p) => (
              <button
                key={p.value}
                type="button"
                className={`priority-btn${priority === p.value ? ' active' : ''}`}
                onClick={() => setPriority(p.value)}
              >
                {p.emoji}<br />{p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Category */}
        {categories.length > 0 && (
          <div className="form-group">
            <label className="form-label">Category</label>
            <div className="cat-select-grid">
              <button
                type="button"
                className={`cat-select-pill${!categoryId ? ' active' : ''}`}
                onClick={() => setCategoryId(undefined)}
              >
                📋 None
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className={`cat-select-pill${categoryId === c.id ? ' active' : ''}`}
                  onClick={() => setCategoryId(c.id)}
                >
                  {c.icon} {c.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Deadline */}
        <div className="form-group">
          <label className="form-label">Deadline (optional)</label>
          <input
            className="form-input"
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />
        </div>

        {/* Reminder */}
        {!isEdit && (
          <div className="form-group">
            <label className="form-label">Reminder (optional)</label>
            <input
              className="form-input"
              type="datetime-local"
              value={reminderAt}
              onChange={(e) => setReminderAt(e.target.value)}
            />
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={isPending || !title.trim()}
          style={{ marginTop: 8 }}
        >
          {isPending ? '⏳ Saving…' : isEdit ? '💾 Save Changes' : '✅ Add Todo'}
        </button>
      </form>
    </BottomSheet>
  );
}
