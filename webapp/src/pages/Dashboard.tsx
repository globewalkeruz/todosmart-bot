import { isToday } from 'date-fns';
import { motion } from 'framer-motion';
import ProgressRing from '../components/ProgressRing';
import { SkeletonCard, SkeletonStatChips } from '../components/Skeleton';
import TodoCard from '../components/TodoCard';
import { useStats } from '../hooks/useStats';
import { useTodos } from '../hooks/useTodos';
import { tgUser } from '../lib/tg';
import { useStore } from '../store';

const FADE_UP = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.35 },
};

export default function Dashboard() {
  const { openTodoSheet, setActiveTab } = useStore();
  const { data: todos = [], isLoading: todosLoading } = useTodos();
  const { data: stats, isLoading: statsLoading } = useStats();

  const todayTodos = todos.filter(
    (t) => !t.is_completed && t.deadline && isToday(new Date(t.deadline)),
  );

  const todayTotal = todayTodos.length;
  const todayDone = todos.filter(
    (t) => t.is_completed && t.completed_at && isToday(new Date(t.completed_at)),
  ).length;
  const todayPct = todayTotal + todayDone > 0
    ? Math.round((todayDone / (todayTotal + todayDone)) * 100)
    : 0;

  const name = tgUser?.first_name ?? 'there';
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="page">
      {/* Greeting */}
      <motion.div className="dashboard-greeting" {...FADE_UP}>
        <div className="greeting-text">
          <h2>{greeting}, {name}! 👋</h2>
          <p>Let's get things done today.</p>
        </div>
        <div className="greeting-avatar">
          {name.charAt(0).toUpperCase()}
        </div>
      </motion.div>

      {/* Progress card */}
      <motion.div
        className="card progress-card"
        {...FADE_UP}
        transition={{ delay: 0.05, duration: 0.35 }}
      >
        <div className="progress-info">
          <h3>Today's Progress</h3>
          <p>
            {todayDone} of {todayDone + todayTotal} tasks done
          </p>
          <div className="progress-pct" style={{ marginTop: 8 }}>
            {todayPct}%
          </div>
        </div>
        <ProgressRing progress={todayPct} />
      </motion.div>

      {/* Stat chips */}
      <motion.div
        {...FADE_UP}
        transition={{ delay: 0.1, duration: 0.35 }}
      >
        {statsLoading ? (
          <SkeletonStatChips />
        ) : (
          <div className="stat-chips">
            <div className="card stat-chip">
              <div className="stat-chip-value">{stats?.total ?? 0}</div>
              <div className="stat-chip-label">Total</div>
            </div>
            <div className="card stat-chip">
              <div className="stat-chip-value">{stats?.completed ?? 0}</div>
              <div className="stat-chip-label">Done</div>
            </div>
            <div className="card stat-chip">
              <div className="stat-chip-value">{stats?.overdue ?? 0}</div>
              <div className="stat-chip-label">Overdue</div>
            </div>
          </div>
        )}
      </motion.div>

      {/* Today's todos */}
      <motion.div
        style={{ marginTop: 24 }}
        {...FADE_UP}
        transition={{ delay: 0.15, duration: 0.35 }}
      >
        <div className="section-title" style={{ padding: '0 16px' }}>
          📅 Due Today
          <button onClick={() => setActiveTab('todos')}>See all</button>
        </div>

        {todosLoading ? (
          <SkeletonCard height={80} />
        ) : todayTodos.length === 0 ? (
          <div className="empty-state" style={{ padding: '32px 16px' }}>
            <div className="empty-state-icon">🎉</div>
            <p>Nothing due today!</p>
          </div>
        ) : (
          <div className="todo-list">
            {todayTodos.slice(0, 5).map((t) => (
              <TodoCard key={t.id} todo={t} onEdit={openTodoSheet} />
            ))}
          </div>
        )}
      </motion.div>

      {/* Recent todos */}
      {!todosLoading && todos.filter((t) => !t.is_completed).length > 0 && (
        <motion.div
          style={{ marginTop: 24, marginBottom: 12 }}
          {...FADE_UP}
          transition={{ delay: 0.2, duration: 0.35 }}
        >
          <div className="section-title" style={{ padding: '0 16px' }}>
            📋 Recent Pending
            <button onClick={() => setActiveTab('todos')}>See all</button>
          </div>
          <div className="todo-list">
            {todos
              .filter((t) => !t.is_completed)
              .slice(0, 3)
              .map((t) => (
                <TodoCard key={t.id} todo={t} onEdit={openTodoSheet} />
              ))}
          </div>
        </motion.div>
      )}

      {/* FAB */}
      <button className="fab" onClick={() => openTodoSheet()} aria-label="Add todo">
        +
      </button>
    </div>
  );
}
