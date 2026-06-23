import { isToday, isPast } from 'date-fns';
import { motion } from 'framer-motion';
import { SkeletonList } from '../components/Skeleton';
import TodoCard from '../components/TodoCard';
import { useCategories } from '../hooks/useCategories';
import { useTodos } from '../hooks/useTodos';
import { haptic } from '../lib/tg';
import { useStore } from '../store';
import type { Todo, TodoFilter } from '../types';

const FILTERS: { value: TodoFilter; label: string }[] = [
  { value: 'all',       label: '✨ All' },
  { value: 'pending',   label: '⏳ Pending' },
  { value: 'completed', label: '✅ Done' },
  { value: 'today',     label: '📅 Today' },
  { value: 'overdue',   label: '⚠️ Overdue' },
];

function applyFilter(todos: Todo[], filter: TodoFilter, catId: string | null): Todo[] {
  let result = [...todos];

  if (catId) result = result.filter((t) => t.category_id === catId);

  switch (filter) {
    case 'pending':
      return result.filter((t) => !t.is_completed);
    case 'completed':
      return result.filter((t) => t.is_completed);
    case 'today':
      return result.filter(
        (t) => !t.is_completed && t.deadline && isToday(new Date(t.deadline)),
      );
    case 'overdue':
      return result.filter(
        (t) =>
          !t.is_completed &&
          t.deadline &&
          isPast(new Date(t.deadline)) &&
          !isToday(new Date(t.deadline)),
      );
    default:
      return result;
  }
}

export default function Todos() {
  const {
    filter, setFilter,
    activeCategoryId, setActiveCategoryId,
    openTodoSheet,
  } = useStore();

  const { data: todos = [], isLoading, refetch, isFetching } = useTodos();
  const { data: categories = [] } = useCategories();

  const filtered = applyFilter(todos, filter, activeCategoryId);

  function handleFilterChange(f: TodoFilter) {
    haptic('tap');
    setFilter(f);
  }

  function handleCatFilter(id: string | null) {
    haptic('tap');
    setActiveCategoryId(id);
  }

  return (
    <div className="page">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 className="page-title">My Todos</h1>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { haptic('tap'); refetch(); }}
            disabled={isFetching}
          >
            {isFetching ? '⏳' : '↺ Refresh'}
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="filter-bar">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            className={`filter-pill${filter === f.value ? ' active' : ''}`}
            onClick={() => handleFilterChange(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Category chips */}
      {categories.length > 0 && (
        <div className="cat-chips">
          <button
            className={`cat-chip${!activeCategoryId ? ' active' : ''}`}
            onClick={() => handleCatFilter(null)}
          >
            🗂️ All
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              className={`cat-chip${activeCategoryId === c.id ? ' active' : ''}`}
              onClick={() => handleCatFilter(c.id)}
            >
              <span className="cat-chip-dot" style={{ background: c.color }} />
              {c.icon} {c.name}
            </button>
          ))}
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <SkeletonList />
      ) : filtered.length === 0 ? (
        <motion.div
          className="empty-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="empty-state-icon">
            {filter === 'completed' ? '🎉' : filter === 'overdue' ? '✨' : '📭'}
          </div>
          <h3>
            {filter === 'completed'
              ? 'Nothing completed yet'
              : filter === 'overdue'
              ? 'No overdue tasks!'
              : 'No todos here'}
          </h3>
          <p>
            {filter === 'overdue'
              ? "You're all caught up — great work!"
              : 'Tap + to add your first todo.'}
          </p>
        </motion.div>
      ) : (
        <motion.div
          className="todo-list"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.25 }}
        >
          {filtered.map((t) => (
            <TodoCard key={t.id} todo={t} onEdit={openTodoSheet} />
          ))}
        </motion.div>
      )}

      {/* FAB */}
      <button className="fab" onClick={() => openTodoSheet()} aria-label="Add todo">
        +
      </button>
    </div>
  );
}
