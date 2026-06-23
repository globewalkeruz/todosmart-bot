import { motion } from 'framer-motion';
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { format } from 'date-fns';
import { SkeletonCard } from '../components/Skeleton';
import { useStats } from '../hooks/useStats';

export default function Stats() {
  const { data: stats, isLoading } = useStats();

  if (isLoading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1 className="page-title">Statistics</h1>
        </div>
        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
          <SkeletonCard height={80} />
          <SkeletonCard height={200} />
          <SkeletonCard height={200} />
        </div>
      </div>
    );
  }

  const weeklyData = (stats?.weekly ?? []).map((d) => ({
    day: format(new Date(d.date), 'EEE'),
    count: d.count,
  }));

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Statistics</h1>
        <p className="page-subtitle">Your productivity at a glance</p>
      </div>

      {/* Key metrics */}
      <motion.div
        className="stats-grid"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="card stat-card">
          <div className="stat-card-icon">📝</div>
          <div className="stat-card-value">{stats?.total ?? 0}</div>
          <div className="stat-card-label">Total</div>
        </div>
        <div className="card stat-card">
          <div className="stat-card-icon">✅</div>
          <div className="stat-card-value">{stats?.completed ?? 0}</div>
          <div className="stat-card-label">Completed</div>
        </div>
        <div className="card stat-card">
          <div className="stat-card-icon">⏳</div>
          <div className="stat-card-value">{stats?.pending ?? 0}</div>
          <div className="stat-card-label">Pending</div>
        </div>
        <div className="card stat-card">
          <div className="stat-card-icon">⚠️</div>
          <div className="stat-card-value">{stats?.overdue ?? 0}</div>
          <div className="stat-card-label">Overdue</div>
        </div>
      </motion.div>

      {/* Streak */}
      {(stats?.streak ?? 0) > 0 && (
        <motion.div
          className="streak-banner"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <span className="streak-flame">🔥</span>
          <div className="streak-info">
            <h3>{stats!.streak}-day streak!</h3>
            <p>Keep it up — you're on a roll!</p>
          </div>
        </motion.div>
      )}

      {/* Most productive day */}
      {stats?.most_productive_day && (
        <motion.div
          className="card"
          style={{ margin: '0 16px 16px', display: 'flex', alignItems: 'center', gap: 12 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
        >
          <span style={{ fontSize: 28 }}>🏆</span>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--txt-primary)' }}>
              Most Productive Day
            </div>
            <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--txt-primary)' }}>
              {stats.most_productive_day}
            </div>
          </div>
        </motion.div>
      )}

      {/* Weekly chart */}
      <motion.div
        className="card chart-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="chart-title">📅 Last 7 Days</div>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={weeklyData} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
            <XAxis
              dataKey="day"
              tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(30,20,60,0.9)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: 10,
                color: '#fff',
                fontSize: 13,
              }}
              cursor={{ fill: 'rgba(255,255,255,0.08)' }}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="rgba(255,255,255,0.6)" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Category donut */}
      {(stats?.by_category ?? []).length > 0 && (
        <motion.div
          className="card chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          <div className="chart-title">🗂️ By Category</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <ResponsiveContainer width={140} height={140}>
              <PieChart>
                <Pie
                  data={stats!.by_category}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={38}
                  outerRadius={64}
                  paddingAngle={3}
                >
                  {stats!.by_category.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(30,20,60,0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 10,
                    color: '#fff',
                    fontSize: 13,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {stats!.by_category.map((c) => (
                <div key={c.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: c.color,
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ fontSize: 13, color: 'var(--txt-primary)', flex: 1 }}>
                    {c.icon} {c.name}
                  </span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--txt-secondary)' }}>
                    {c.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Completion rate */}
      {stats && stats.total > 0 && (
        <motion.div
          className="card"
          style={{ margin: '0 16px 24px', textAlign: 'center', padding: '24px 16px' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div style={{ fontSize: 48, fontWeight: 800, color: 'var(--txt-primary)' }}>
            {stats.completion_rate}%
          </div>
          <div style={{ fontSize: 14, color: 'var(--txt-secondary)', marginTop: 4 }}>
            Overall completion rate
          </div>
        </motion.div>
      )}
    </div>
  );
}
