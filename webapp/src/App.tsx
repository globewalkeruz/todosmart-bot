import { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import NavBar from './components/NavBar';
import TodoForm from './components/TodoForm';
import { useUser } from './hooks/useUser';
import { tg } from './lib/tg';
import Dashboard from './pages/Dashboard';
import Todos from './pages/Todos';
import Categories from './pages/Categories';
import Stats from './pages/Stats';
import { useStore } from './store';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-logo">✅</div>
      <div className="loading-text">TodoSmart</div>
      <div className="loading-dots">Loading your workspace…</div>
    </div>
  );
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="error-screen">
      <div className="error-icon">⚠️</div>
      <h2>Something went wrong</h2>
      <p>{message}</p>
      <p style={{ marginTop: 8, fontSize: 13, opacity: 0.7 }}>
        Make sure you're opening this inside Telegram.
      </p>
      <button
        className="btn btn-glass"
        style={{ marginTop: 20 }}
        onClick={() => window.location.reload()}
      >
        Try again
      </button>
    </div>
  );
}

function AppInner() {
  const activeTab = useStore((s) => s.activeTab);
  const { isLoading, isError, error } = useUser();

  useEffect(() => {
    tg?.ready();
    tg?.expand();

    // Apply dark theme if Telegram is in dark mode
    if (tg?.colorScheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, []);

  if (isLoading) return <LoadingScreen />;
  if (isError) return <ErrorScreen message={error?.message ?? 'Authentication failed'} />;

  return (
    <div className="app">
      <main className="main-content">
        {activeTab === 'home'       && <Dashboard />}
        {activeTab === 'todos'      && <Todos />}
        {activeTab === 'categories' && <Categories />}
        {activeTab === 'stats'      && <Stats />}
      </main>
      <NavBar />
      <TodoForm />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 2500,
          style: {
            borderRadius: '16px',
            background: 'rgba(20, 10, 50, 0.92)',
            color: '#fff',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.15)',
            fontSize: '14px',
            fontWeight: '600',
          },
        }}
      />
    </QueryClientProvider>
  );
}
