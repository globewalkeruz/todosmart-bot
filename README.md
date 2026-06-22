# TodoSmart — Telegram To-Do Bot

A feature-rich Telegram bot for personal and team task management, built with **aiogram 3.x** and **Supabase**.

---

## Features

### Personal Mode (DM)
- **Add tasks** via button flow or `/add <title>`
- **Priority levels** — 🚨 Urgent / 🔴 High / 🟡 Medium / 🟢 Low
- **Due dates** — natural language: `tomorrow`, `next week`, `DD.MM.YYYY`
- **Real push reminders** — notifications fire at exact time via APScheduler
- **Edit tasks** — change title or priority inline
- **Delete tasks** — actually removes from database
- **Statistics** — completion rate, priority breakdown
- **Paginated task list** — 5 tasks per page with navigation buttons

### Group Mode (Groups / Supergroups / Channels)
- **Shared task board** — all members see group tasks
- **Task assignment** — assign tasks to specific members
- **Group statistics** — team-level completion tracking
- **Member list** — view who is in the group

### System
- Reminders survive bot restarts (restored from Supabase on startup)
- Daily summary sent to all users with pending tasks (configurable time)
- Rate limiting — 1 request per 0.5s per user
- Auto-registers users and groups on first interaction

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot framework | aiogram 3.x |
| Database | Supabase (PostgreSQL) |
| Scheduler | APScheduler 3.x |
| Config | pydantic-settings |
| Deployment | Docker + Railway |

---

## Project Structure

```
bot/
├── main.py                  # Entry point
├── config.py                # Reads .env via pydantic-settings
├── handlers/
│   ├── start.py             # /start, /help, main menu
│   ├── tasks.py             # Add, list, view, complete, delete, edit, priority
│   ├── reminders.py         # Set/cancel push reminders
│   ├── groups.py            # Group tasks, members, assignment
│   ├── stats.py             # Personal + group statistics
│   └── errors.py            # Global error handler
├── keyboards/
│   ├── callback_data.py     # Type-safe CallbackData classes
│   ├── main_menu.py         # Main menu (personal vs group)
│   ├── task_kb.py           # Task list + task action keyboards
│   ├── priority_kb.py       # Priority picker
│   └── reminder_kb.py       # Reminder time picker
├── database/
│   ├── client.py            # Supabase async client singleton
│   ├── models.py            # Pydantic models
│   ├── schema.sql           # Full database schema (run once in Supabase)
│   └── queries/             # One file per table: users, tasks, groups, reminders
├── middlewares/
│   ├── db_middleware.py     # Injects Supabase client into every handler
│   ├── user_middleware.py   # Auto-upserts user on every update
│   ├── group_middleware.py  # Auto-upserts group + member on group updates
│   └── throttling.py        # Rate limiting
├── scheduler/
│   └── jobs.py              # APScheduler setup, schedule/cancel/restore reminders
├── states/
│   └── task_states.py       # FSM state groups for add/edit task flows
└── utils/
    ├── formatters.py        # Format task/stats for display
    └── date_parser.py       # Parse natural-language dates
```

---

## Commands

| Command | Description |
|---|---|
| `/start` | Open main menu |
| `/help` | Show help and command list |
| `/add <task>` | Quick-add a task (or open guided flow with no argument) |
| `/list` | Show pending tasks (group tasks in groups, personal in DM) |

All other actions use inline buttons — no need to remember extra commands.

---

## Installation & Local Setup

### 1. Prerequisites

- Python 3.11+
- A [Supabase](https://supabase.com) project
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 2. Clone and install

```bash
git clone <your-repo>
cd todosmart
pip install -r requirements.txt
```

### 3. Set up Supabase

Follow **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** — takes about 5 minutes.

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
DAILY_SUMMARY_HOUR=21
DAILY_SUMMARY_MINUTE=0
```

### 5. Run locally

```bash
python -m bot.main
```

Expected startup output:
```
INFO  TodoSmart bot starting...
INFO  Restored 0 pending reminder(s)
INFO  Daily summary scheduled at 21:00
INFO  Started polling
```

---

## Deployment to Railway

### From GitHub (recommended)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Go to **Variables** and add all environment variables from `.env`
5. Railway auto-detects `Dockerfile` and deploys automatically

### Railway CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Then set variables in the Railway dashboard under **Variables**.

### Production tip

Use the **service_role** key instead of the `anon` key for `SUPABASE_KEY` in production — it gives the bot full database access without Row Level Security issues. Get it from **Supabase → Settings → API → service_role**.

---

## How Reminders Work

1. User sets a reminder → APScheduler job created with `run_date` trigger
2. Job ID stored in Supabase (`tasks.reminder_job_id`)
3. When time arrives → bot sends a DM to the user
4. Reminder cleared from database
5. On bot restart → `restore_reminders()` re-creates all jobs for future reminders from Supabase

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon key (dev) or service_role key (prod) |
| `DAILY_SUMMARY_HOUR` | No | Hour for daily task digest (default: 21) |
| `DAILY_SUMMARY_MINUTE` | No | Minute for daily task digest (default: 0) |
