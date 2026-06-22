declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: { id: number; first_name: string; username?: string };
        };
        colorScheme: 'light' | 'dark';
        ready(): void;
        expand(): void;
        close(): void;
        HapticFeedback?: {
          impactOccurred(style: 'light' | 'medium' | 'heavy'): void;
          notificationOccurred(type: 'error' | 'success' | 'warning'): void;
        };
        BackButton?: {
          isVisible: boolean;
          show(): void;
          hide(): void;
          onClick(fn: () => void): void;
          offClick(fn: () => void): void;
        };
      };
    };
  }
}

export const tg = window.Telegram?.WebApp;
export const initData = tg?.initData ?? '';
export const tgUser = tg?.initDataUnsafe?.user;
