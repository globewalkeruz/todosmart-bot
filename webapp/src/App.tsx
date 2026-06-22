import { useState } from 'react';
import TaskListScreen from './screens/TaskListScreen';
import AddTaskScreen from './screens/AddTaskScreen';

type Screen = 'list' | 'add';

export default function App() {
  const [screen, setScreen] = useState<Screen>('list');
  const [refreshKey, setRefreshKey] = useState(0);

  function goAdd() {
    setScreen('add');
  }

  function goList(refresh = false) {
    setScreen('list');
    if (refresh) setRefreshKey((k) => k + 1);
  }

  return screen === 'list' ? (
    <TaskListScreen key={refreshKey} onAdd={goAdd} />
  ) : (
    <AddTaskScreen onDone={() => goList(true)} onBack={() => goList()} />
  );
}
