# TodoSmart — Telegram Mini App

A beautiful, full-featured todo manager built as a **Telegram Mini App**.  
iOS 18 Liquid Glass design · React + Vite · FastAPI · Supabase · Railway + Vercel

---

## Project Overview

| Layer | Stack |
|---|---|
| Bot | Python · aiogram 3.x |
| API | FastAPI · Uvicorn |
| Database | Supabase (PostgreSQL) |
| Frontend | React 18 · Vite · TypeScript |
| State | Zustand + TanStack Query |
| Animations | Framer Motion |
| Charts | Recharts |
| Deploy | Railway (API + Bot) · Vercel (Frontend) |

---

## Project Structure

```
todosmart/
├── api/                  FastAPI REST backend
│   ├── main.py
│   ├── auth.py           Telegram initData validation + user upsert
│   ├── scheduler.py      APScheduler — fires reminder messages
│   └── routes/
│       ├── auth.py       POST /api/auth/me
│       ├── todos.py      CRUD /api/todos/
│       ├── categories.py CRUD /api/categories/
│       └── stats.py      GET  /api/stats/{user_id}
├── bot/                  aiogram Telegram bot
├── webapp/               React Mini App (Vite)
│   └── src/
│       ├── pages/        Dashboard · Todos · Categories · Stats
│       ├── components/   NavBar · TodoCard · BottomSheet · Forms · Charts
│       ├── hooks/        TanStack Query data hooks
│       ├── store/        Zustand global state
│       └── styles/       globals.css — Liquid Glass design system
└── migrations/
    └── 001_initial.sql   Supabase schema
```

---

## Prerequisites

- **Telegram bot** — create one via [@BotFather](https://t.me/BotFather) and note the token
- **Supabase project** — free tier at [supabase.com](https://supabase.com)
- **Railway account** — [railway.app](https://railway.app)
- **Vercel account** — [vercel.com](https://vercel.com)
- Python 3.11+ and Node.js 18+ for local development

---

## Step 1 — Supabase Setup

1. Create a new project at [app.supabase.com](https://app.supabase.com)
2. Go to **SQL Editor** and run the contents of `migrations/001_initial.sql`
3. From **Settings → API** copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** key → `SUPABASE_KEY` (use service_role, not anon)

---

## Step 2 — Local Development

### API

```bash
cd api
cp .env.example .env        # fill in BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# → http://localhost:8000/health should return {"status":"ok"}
```

### Bot

```bash
cp .env.example .env        # same vars + WEBAPP_URL=https://localhost:5173 (for testing)
pip install -r requirements.txt
python -m bot.main
```

### Frontend

```bash
cd webapp
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000
npm install
npm run dev
# → http://localhost:5173
```

> **Local testing tip:** set `VITE_DEV_INIT_DATA` to a real initData string  
> (open the bot, intercept the request from DevTools, paste the value)

---

## Step 3 — Deploy API to Railway

1. Push your repo to GitHub
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select the repo; Railway will detect `railway.toml` and use `api/Dockerfile`
4. Go to **Variables** and add:

   ```
   BOT_TOKEN=...
   SUPABASE_URL=...
   SUPABASE_KEY=...
   WEBAPP_URL=https://your-app.vercel.app   (fill in after Step 4)
   PORT=8000
   ```

5. Click **Deploy** — note the generated URL: `https://xxx.railway.app`

---

## Step 4 — Deploy Frontend to Vercel

1. [vercel.com](https://vercel.com) → **New Project** → import the same GitHub repo
2. Set **Root Directory** to `webapp`
3. Add **Environment Variables**:

   ```
   VITE_API_URL=https://xxx.railway.app
   ```

4. Deploy — note the Vercel URL: `https://your-app.vercel.app`

---

## Step 5 — Configure the Bot

1. In Railway, update `WEBAPP_URL=https://your-app.vercel.app`
2. Redeploy the Railway service (or it auto-redeploys)
3. In Telegram, talk to [@BotFather](https://t.me/BotFather):
   - `/setmenubutton` → select your bot → paste your Vercel URL
   - Or use webhook: `curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook -d url=https://xxx.railway.app/webhook`

---

## Environment Variables Reference

### API / Bot (`.env` or Railway Variables)

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase **service_role** key |
| `WEBAPP_URL` | ✅ | Vercel deployment URL |
| `PORT` | Railway sets this | HTTP port for uvicorn |

### Frontend (`.env` or Vercel Environment Variables)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ✅ | Railway API URL |
| `VITE_DEV_INIT_DATA` | Dev only | Telegram initData for local testing |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/me` | Validate initData, upsert user, return profile |
| `GET` | `/api/todos/{user_id}` | List todos (filter: all/pending/completed) |
| `POST` | `/api/todos/` | Create todo |
| `PATCH` | `/api/todos/{id}` | Update todo |
| `DELETE` | `/api/todos/{id}` | Delete todo |
| `GET` | `/api/categories/{user_id}` | List categories with todo count |
| `POST` | `/api/categories/` | Create category |
| `PATCH` | `/api/categories/{id}` | Update category |
| `DELETE` | `/api/categories/{id}` | Delete category |
| `GET` | `/api/stats/{user_id}` | Stats (totals, weekly chart, streak) |
| `GET` | `/health` | Health check |

All requests must include `Authorization: tma <initData>` header.

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Register user + show Mini App button |
| `/app` | Open the Mini App |
| `/stats` | Quick text statistics |
| `/remind` | Manage reminders |
