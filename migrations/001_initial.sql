-- TodoSmart — initial schema
-- Run this in your Supabase project's SQL editor.
-- The backend uses the service-role key which bypasses RLS.
-- User-level RLS would require Supabase custom JWT auth (not implemented here).

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Tables ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.users (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id BIGINT      UNIQUE NOT NULL,
  username    TEXT,
  first_name  TEXT        NOT NULL DEFAULT '',
  last_name   TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.categories (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name       TEXT        NOT NULL,
  color      TEXT        NOT NULL DEFAULT '#667eea',
  icon       TEXT        NOT NULL DEFAULT '📁',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.todos (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title        TEXT        NOT NULL,
  description  TEXT,
  category_id  UUID        REFERENCES public.categories(id) ON DELETE SET NULL,
  priority     TEXT        NOT NULL DEFAULT 'medium'
                           CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  deadline     TIMESTAMPTZ,
  is_completed BOOLEAN     NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.reminders (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  todo_id    UUID        NOT NULL REFERENCES public.todos(id) ON DELETE CASCADE,
  remind_at  TIMESTAMPTZ NOT NULL,
  is_sent    BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Indexes ─────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_todos_user_id      ON public.todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_completed     ON public.todos(is_completed);
CREATE INDEX IF NOT EXISTS idx_todos_deadline      ON public.todos(deadline);
CREATE INDEX IF NOT EXISTS idx_todos_user_status   ON public.todos(user_id, is_completed);
CREATE INDEX IF NOT EXISTS idx_categories_user_id  ON public.categories(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON public.reminders(remind_at)
  WHERE NOT is_sent;

-- ─── Row Level Security ──────────────────────────────────────────────────────

ALTER TABLE public.users      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.todos      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminders  ENABLE ROW LEVEL SECURITY;

-- Service-role key bypasses these; they only apply to anon/authenticated JWT clients.
-- All backend access goes through the service key — these are a safety net.
CREATE POLICY "deny_all_users"      ON public.users      FOR ALL USING (false);
CREATE POLICY "deny_all_categories" ON public.categories FOR ALL USING (false);
CREATE POLICY "deny_all_todos"      ON public.todos      FOR ALL USING (false);
CREATE POLICY "deny_all_reminders"  ON public.reminders  FOR ALL USING (false);

-- ─── updated_at trigger ──────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_todos_updated_at
  BEFORE UPDATE ON public.todos
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
