-- ============================================================
-- TodoSmart — Supabase Schema
-- Run this SQL once in your Supabase project's SQL editor
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id       BIGINT PRIMARY KEY,
    username      TEXT,
    first_name    TEXT,
    last_name     TEXT,
    language_code TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    last_active   TIMESTAMPTZ DEFAULT NOW()
);

-- Groups / Channels
CREATE TABLE IF NOT EXISTS groups (
    group_id   BIGINT PRIMARY KEY,
    title      TEXT NOT NULL,
    chat_type  TEXT NOT NULL,        -- 'group' | 'supergroup' | 'channel'
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Group membership
CREATE TABLE IF NOT EXISTS group_members (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id  BIGINT REFERENCES groups(group_id) ON DELETE CASCADE,
    user_id   BIGINT REFERENCES users(user_id)  ON DELETE CASCADE,
    role      TEXT DEFAULT 'member',             -- 'admin' | 'member'
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(group_id, user_id)
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL,
    description     TEXT,
    priority        TEXT DEFAULT 'medium',   -- 'low' | 'medium' | 'high' | 'urgent'
    status          TEXT DEFAULT 'pending',  -- 'pending' | 'in_progress' | 'completed' | 'cancelled'
    created_by      BIGINT REFERENCES users(user_id),
    group_id        BIGINT REFERENCES groups(group_id) ON DELETE CASCADE,
    due_date        TIMESTAMPTZ,
    reminder_time   TIMESTAMPTZ,
    reminder_job_id TEXT,                    -- APScheduler job ID for cancellation
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Task assignments (group tasks only)
CREATE TABLE IF NOT EXISTS task_assignments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id     UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id     BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    assigned_by BIGINT REFERENCES users(user_id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(task_id, user_id)
);

-- Task completions (one record per user who completed the task)
CREATE TABLE IF NOT EXISTS task_completions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id      BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(task_id, user_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by);
CREATE INDEX IF NOT EXISTS idx_tasks_group_id   ON tasks(group_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status     ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_reminder   ON tasks(reminder_time) WHERE reminder_time IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assignments_task ON task_assignments(task_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user ON task_assignments(user_id);

-- Auto-update updated_at on tasks
CREATE OR REPLACE FUNCTION fn_update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_tasks_updated_at ON tasks;
CREATE TRIGGER trg_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
