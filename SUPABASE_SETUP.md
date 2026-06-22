# Supabase Setup Guide

## 1. Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click **New Project**
3. Choose your organization, give the project a name (e.g. `todosmart`), set a database password, and pick a region close to your users
4. Wait ~2 minutes for the project to be provisioned

## 2. Get Your API Keys

1. In your project dashboard, go to **Settings → API**
2. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon / public key** → `SUPABASE_KEY` (use **service_role** key for production)

## 3. Run the Schema

1. In your project dashboard, go to **SQL Editor**
2. Click **New query**
3. Paste the contents of `bot/database/schema.sql`
4. Click **Run**

## 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
BOT_TOKEN=your_bot_token_from_botfather
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_anon_key_here
DAILY_SUMMARY_HOUR=21
DAILY_SUMMARY_MINUTE=0
```

## 5. Run Locally

```bash
pip install -r requirements.txt
python -m bot.main
```

## 6. Deploy to Railway

1. Push your code to GitHub
2. Create a new Railway project → Deploy from GitHub repo
3. Add environment variables in Railway dashboard (same as `.env`)
4. Railway auto-builds via `Dockerfile` and runs `python -m bot.main`

## Row-Level Security (Optional but Recommended)

After the schema runs, enable RLS and add policies so the anon key can only read/write its own data. Example for `tasks`:

```sql
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (for the bot)
CREATE POLICY "service_full_access" ON tasks
  USING (true)
  WITH CHECK (true);
```

Or use the Supabase **service_role** key instead of `anon` for full access without RLS.
