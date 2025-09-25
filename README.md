# Telegram To-Do Bot 🤖

A simple and efficient Telegram bot for managing your daily tasks and to-do lists. Built with Python and the `python-telegram-bot` library.

## Features ✨

- ✅ Add new tasks
- 📋 List pending and completed tasks
- ✅ Mark tasks as completed
- 🗑️ Delete tasks
- 🧹 Clear completed tasks
- 💾 Persistent storage (JSON file)
- 🎯 User-specific task management

## Commands 📝

### Adding Tasks
- `/add <task>` - Add a new task
- `/todo <task>` - Quick add a task (alias for /add)

### Viewing Tasks
- `/list` - Show pending tasks
- `/all` - Show all tasks (including completed)
- `/completed` - Show only completed tasks

### Managing Tasks
- `/complete <id>` - Mark task as completed
- `/delete <id>` - Delete a task
- `/clear` - Clear all completed tasks

### Help
- `/start` - Welcome message and help
- `/help` - Show help information

## Setup Instructions 🚀

### Option 1: Local Development

#### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to create your bot
4. Save the bot token you receive

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

**Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**Linux/macOS:**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

#### 4. Run the Bot

```bash
python telegram_todo_bot.py
```

### Option 2: Deploy to Railway 🚄

#### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to create your bot
4. Save the bot token you receive

#### 2. Deploy to Railway

1. **Fork or clone this repository**
2. **Go to [Railway.app](https://railway.app)**
3. **Sign up/Login with GitHub**
4. **Click "New Project" → "Deploy from GitHub repo"**
5. **Select your repository**
6. **Add Environment Variable:**
   - Variable: `TELEGRAM_BOT_TOKEN`
   - Value: `your_bot_token_here`
7. **Click "Deploy"**

#### 3. Railway Configuration

The project includes:
- `Dockerfile` - Optimized for Railway deployment
- `railway.json` - Railway-specific configuration
- `.dockerignore` - Optimized Docker build
- Automatic data persistence in `/app/data`

#### 4. Monitor Your Bot

- Check Railway dashboard for logs
- Your bot will automatically restart if it crashes
- Data is persisted in Railway's persistent storage

### Option 3: Docker Deployment 🐳

#### 1. Build the Docker Image

```bash
docker build -t telegram-todo-bot .
```

#### 2. Run the Container

```bash
docker run -d \
  --name telegram-todo-bot \
  -e TELEGRAM_BOT_TOKEN="your_bot_token_here" \
  -v $(pwd)/data:/app/data \
  telegram-todo-bot
```

## Usage Examples 💡

```
/add Buy groceries
/todo Call mom
/list
/complete 1
/delete 2
/clear
/all
```

## Data Storage 💾

The bot stores all tasks in a `todos.json` file in the same directory as the script. Each user's tasks are stored separately, ensuring privacy and organization.

## File Structure 📁

```
telegram-todo-bot/
├── telegram_todo_bot.py    # Main bot script
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── Dockerfile             # Docker configuration for Railway
├── railway.json           # Railway deployment config
├── .dockerignore          # Docker build optimization
├── README.md              # This file
└── todos.json             # Data storage (created automatically)
```

## Railway Deployment Features 🚄

### Automatic Scaling
- Railway automatically scales your bot based on usage
- No need to manage servers or infrastructure

### Persistent Storage
- Data is automatically persisted in Railway's storage
- Your todos survive bot restarts and deployments

### Environment Management
- Secure environment variable management
- Easy configuration through Railway dashboard

### Monitoring & Logs
- Real-time logs in Railway dashboard
- Automatic restart on failures
- Health checks and monitoring

### Zero Configuration
- Just add your `TELEGRAM_BOT_TOKEN` environment variable
- Railway handles everything else automatically

## Features in Detail 🔍

### Task Management
- **Add Tasks**: Use `/add` or `/todo` followed by your task description
- **View Tasks**: Use `/list` to see pending tasks, `/all` to see everything
- **Complete Tasks**: Use `/complete <id>` to mark a task as done
- **Delete Tasks**: Use `/delete <id>` to remove a task permanently
- **Clean Up**: Use `/clear` to remove all completed tasks

### Data Persistence
- All tasks are automatically saved to a JSON file
- Data persists between bot restarts
- Each user has their own separate task list

### User Experience
- Clean, emoji-rich interface
- Clear error messages and help text
- Intuitive command structure
- Real-time task management

## Troubleshooting 🔧

### Common Issues

1. **Bot not responding**: Check that your bot token is correct and the bot is running
2. **Permission errors**: Make sure the bot has permission to write to the directory
3. **Import errors**: Run `pip install -r requirements.txt` to install dependencies

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your bot token is correct
3. Ensure the bot has the necessary permissions
4. Check the console output for error messages

## Contributing 🤝

Feel free to contribute to this project by:
- Adding new features
- Improving the user interface
- Fixing bugs
- Adding more storage options

## License 📄

This project is open source and available under the MIT License.

---

**Happy task managing! 🎯**
