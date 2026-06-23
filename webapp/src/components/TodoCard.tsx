import { useState } from 'react';
import { useSwipeable } from 'react-swipeable';
import { format, isPast, isToday } from 'date-fns';
import { useDeleteTodo, useUpdateTodo } from '../hooks/useTodos';
import { haptic } from '../lib/tg';
import type { Todo } from '../types';

const PRIORITY_LABEL: Record<string, string> = {
  low: '▸ Low',
  medium: '◆ Medium',
  high: '▲ High',
  urgent: '⚡ Urgent',
};

interface Props {
  todo: Todo;
  onEdit?: (id: string) => void;
}

export default function TodoCard({ todo, onEdit }: Props) {
  const [offset, setOffset] = useState(0);
  const [swiped, setSwiped] = useState(false);
  const updateTodo = useUpdateTodo();
  const deleteTodo = useDeleteTodo();

  const swipe = useSwipeable({
    onSwiping: ({ deltaX }) => {
      if (deltaX < 0) setOffset(Math.max(deltaX, -90));
    },
    onSwipedLeft: ({ deltaX }) => {
      if (Math.abs(deltaX) > 50) {
        setSwiped(true);
        setOffset(-80);
      } else {
        setOffset(0);
      }
    },
    onSwipedRight: () => {
      setSwiped(false);
      setOffset(0);
    },
    trackMouse: false,
    preventScrollOnSwipe: true,
  });

  function handleComplete() {
    if (todo.is_completed) return;
    haptic('success');
    updateTodo.mutate({ id: todo.id, is_completed: true });
  }

  function handleDelete() {
    haptic('warning');
    deleteTodo.mutate(todo.id);
  }

  function handleCardTap() {
    if (swiped) {
      setSwiped(false);
      setOffset(0);
      return;
    }
    onEdit?.(todo.id);
  }

  const deadline = todo.deadline ? new Date(todo.deadline) : null;
  const isOverdue = deadline && !todo.is_completed && isPast(deadline) && !isToday(deadline);
  const isTodayDue = deadline && isToday(deadline);

  return (
    <div className="todo-card-wrap">
      {/* Delete background */}
      <div className="todo-delete-bg" onClick={handleDelete}>
        🗑️
      </div>

      {/* Card */}
      <div
        {...swipe}
        className={`todo-card${todo.is_completed ? ' completed' : ''}`}
        style={{ transform: `translateX(${offset}px)` }}
        onClick={handleCardTap}
      >
        <div className="todo-card-top">
          {/* Checkbox */}
          <button
            className={`todo-check${todo.is_completed ? ' checked' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              handleComplete();
            }}
            disabled={updateTodo.isPending}
            aria-label="Complete"
          >
            {todo.is_completed && <span className="todo-check-icon">✓</span>}
          </button>

          <div className="todo-body">
            <div className={`todo-title${todo.is_completed ? ' completed' : ''}`}>
              {todo.title}
            </div>
            {todo.description && (
              <div className="todo-desc">{todo.description}</div>
            )}

            <div className="todo-meta">
              <span className={`priority-badge ${todo.priority}`}>
                {PRIORITY_LABEL[todo.priority]}
              </span>

              {todo.categories && (
                <span
                  className="todo-cat-badge"
                  style={{ background: `${todo.categories.color}30`, color: todo.categories.color }}
                >
                  {todo.categories.icon} {todo.categories.name}
                </span>
              )}

              {deadline && (
                <span className={`todo-deadline${isOverdue ? ' overdue' : ''}`}>
                  {isOverdue ? '⚠️' : isTodayDue ? '📅' : '🗓️'}{' '}
                  {format(deadline, 'MMM d, HH:mm')}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
