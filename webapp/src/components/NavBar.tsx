import { haptic } from '../lib/tg';
import { useStore } from '../store';

const TABS = [
  { id: 'home',       icon: '🏠', label: 'Home' },
  { id: 'todos',      icon: '✅', label: 'Todos' },
  { id: 'categories', icon: '🗂️', label: 'Lists' },
  { id: 'stats',      icon: '📊', label: 'Stats' },
] as const;

export default function NavBar() {
  const activeTab = useStore((s) => s.activeTab);
  const setActiveTab = useStore((s) => s.setActiveTab);

  function handleTab(id: typeof TABS[number]['id']) {
    if (id !== activeTab) {
      haptic('tap');
      setActiveTab(id);
    }
  }

  return (
    <nav className="nav">
      {TABS.map((t) => (
        <button
          key={t.id}
          className={`nav-item${activeTab === t.id ? ' active' : ''}`}
          onClick={() => handleTab(t.id)}
        >
          <span className="nav-icon">{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}
    </nav>
  );
}
