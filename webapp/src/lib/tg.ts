interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    hash: string;
  };
  colorScheme: 'light' | 'dark';
  themeParams: Record<string, string>;
  isExpanded: boolean;
  viewportHeight: number;
  ready(): void;
  expand(): void;
  close(): void;
  enableClosingConfirmation(): void;
  setHeaderColor(color: string): void;
  setBackgroundColor(color: string): void;
  HapticFeedback: {
    impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
    notificationOccurred(type: 'error' | 'success' | 'warning'): void;
    selectionChanged(): void;
  };
  BackButton: {
    isVisible: boolean;
    show(): void;
    hide(): void;
    onClick(fn: () => void): void;
    offClick(fn: () => void): void;
  };
}

declare global {
  interface Window {
    Telegram?: { WebApp: TelegramWebApp };
  }
}

export const tg = window.Telegram?.WebApp;
export const initData =
  tg?.initData ||
  (import.meta.env.VITE_DEV_INIT_DATA as string | undefined) ||
  '';
export const tgUser = tg?.initDataUnsafe?.user;

export function haptic(
  type: 'tap' | 'medium' | 'success' | 'error' | 'warning' = 'tap',
): void {
  if (!tg?.HapticFeedback) return;
  switch (type) {
    case 'tap':
      tg.HapticFeedback.impactOccurred('light');
      break;
    case 'medium':
      tg.HapticFeedback.impactOccurred('medium');
      break;
    case 'success':
      tg.HapticFeedback.notificationOccurred('success');
      break;
    case 'error':
      tg.HapticFeedback.notificationOccurred('error');
      break;
    case 'warning':
      tg.HapticFeedback.notificationOccurred('warning');
      break;
  }
}
