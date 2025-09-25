# 🤝 Collaborative Telegram To-Do Bot

A powerful, database-driven Telegram bot for managing tasks with **group collaboration**, **user management**, and **SQL storage**. Perfect for teams, families, and organizations who need to work together on shared tasks.

## ✨ Key Features

### 🗄️ **SQL Database Storage**
- **SQLite Database** - Reliable, fast, and portable
- **User Management** - Track all users and their activities
- **Group Management** - Organize teams and collaborations
- **Task History** - Complete audit trail of all activities
- **Data Integrity** - ACID compliance and data consistency

### 👥 **Group Collaboration**
- **Shared Task Lists** - Everyone can see group tasks
- **Task Assignment** - Assign tasks to specific team members
- **Collaborative Completion** - Multiple users can complete tasks
- **Team Statistics** - Track group productivity and progress
- **Member Management** - See who's in your group

### 🎯 **Advanced Task Management**
- **Priority Levels** - Urgent, High, Medium, Low priorities
- **Task Assignment** - Assign tasks to specific users
- **Completion Tracking** - See who completed what
- **Due Dates** - Set deadlines for tasks
- **Task History** - Track all task activities

### 🎨 **Beautiful Interface**
- **Inline Buttons** - No command memorization needed
- **Context-Aware UI** - Different interfaces for personal vs group
- **Mobile Optimized** - Perfect for smartphone use
- **Emoji-Rich Design** - Engaging and intuitive interface

## 🏗️ **Database Schema**

### **Users Table**
```sql
users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    is_bot BOOLEAN,
    language_code TEXT,
    created_at TIMESTAMP,
    last_active TIMESTAMP
)
```

### **Groups Table**
```sql
groups (
    group_id INTEGER PRIMARY KEY,
    group_title TEXT,
    group_type TEXT,
    created_at TIMESTAMP,
    is_active BOOLEAN
)
```

### **Tasks Table**
```sql
tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_by INTEGER,
    group_id INTEGER,
    due_date TIMESTAMP,
    reminder_time TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### **Task Assignments Table**
```sql
task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    user_id INTEGER,
    assigned_by INTEGER,
    assigned_at TIMESTAMP,
    status TEXT DEFAULT 'assigned'
)
```

### **Task Completions Table**
```sql
task_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    user_id INTEGER,
    completed_at TIMESTAMP,
    notes TEXT
)
```

## 🚀 **Quick Start**

### **Option 1: Local Development**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd telegram-todo-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file:**
   ```bash
   cp env.example .env
   # Edit .env and add your bot token
   ```

4. **Get your bot token:**
   - Message `@BotFather` on Telegram
   - Send `/newbot` and follow instructions
   - Copy your bot token

5. **Set your bot token in .env:**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

6. **Run the bot:**
   ```bash
   python collaborative_todo_bot.py
   ```

### **Option 2: Railway Deployment** 🚄

1. **Fork this repository**
2. **Go to [Railway.app](https://railway.app)**
3. **Connect your GitHub account**
4. **Deploy from GitHub repository**
5. **Add environment variable:**
   - `TELEGRAM_BOT_TOKEN` = your bot token
6. **Deploy!** 🎉

### **Option 3: Docker Deployment** 🐳

1. **Build the image:**
   ```bash
   docker build -t collaborative-todo-bot .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name collaborative-todo-bot \
     -e TELEGRAM_BOT_TOKEN="your_bot_token_here" \
     -v $(pwd)/data:/app/data \
     collaborative-todo-bot
   ```

## 📱 **Usage Guide**

### **Personal Use**
1. **Start a chat** with your bot
2. **Send `/start`** to see the main menu
3. **Use buttons** to navigate and manage tasks
4. **Create personal tasks** with priorities and reminders

### **Group Collaboration**
1. **Add the bot** to your Telegram group
2. **Send `/start`** in the group to initialize
3. **Create group tasks** that everyone can see
4. **Assign tasks** to specific group members
5. **Track progress** with group statistics

## 🎮 **Interactive Features**

### **Personal Interface:**
- 📝 **Add Task** - Create personal tasks
- 📋 **My Tasks** - View your personal tasks
- 👥 **Groups** - Join group collaborations
- 📊 **Statistics** - Track your productivity
- ⚙️ **Settings** - Customize your experience

### **Group Interface:**
- 📝 **Add Task** - Create group tasks
- 📋 **Group Tasks** - View all group tasks
- 👥 **Members** - See group members
- 📊 **Statistics** - Track group productivity
- ⚙️ **Settings** - Group management

### **Task Actions:**
- ✅ **Complete** - Mark tasks as done
- 👥 **Assign** - Assign tasks to members (groups only)
- 🏷️ **Priority** - Change task priority
- 📝 **Edit** - Modify task details
- 🗑️ **Delete** - Remove tasks

## 🎯 **Collaboration Features**

### **Group Task Management:**
- **Shared Visibility** - All group members can see tasks
- **Task Assignment** - Assign tasks to specific members
- **Collaborative Completion** - Multiple users can complete tasks
- **Progress Tracking** - See who's working on what
- **Team Statistics** - Track group productivity

### **User Management:**
- **Automatic Registration** - Users are added when they interact
- **Role Management** - Different roles for group members
- **Activity Tracking** - Track user engagement
- **Privacy Protection** - Personal tasks remain private

### **Task Assignment System:**
- **Assign to Members** - Choose who works on what
- **Multiple Assignees** - Assign tasks to multiple people
- **Completion Tracking** - See who completed what
- **Progress Monitoring** - Track individual contributions

## 📊 **Statistics & Analytics**

### **Personal Statistics:**
- 📈 **Completion Rate** - Track your productivity
- 🏷️ **Priority Distribution** - See how you organize tasks
- ⏰ **Time Management** - Monitor your work patterns
- 📅 **Task Trends** - Understand your productivity cycles

### **Group Statistics:**
- 👥 **Team Productivity** - Track group performance
- 🎯 **Task Distribution** - See how work is distributed
- ✅ **Completion Rates** - Monitor team achievements
- 📊 **Member Contributions** - Track individual participation

## 🔧 **Configuration**

### **Environment Variables:**
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
DATA_DIR=./data                    # Data storage location
DB_PATH=todo_bot.db               # Database file path
MAX_TASK_LENGTH=500               # Maximum task description length
MAX_TASKS_PER_USER=100            # Maximum tasks per user
```

### **Database Configuration:**
- **SQLite Database** - Lightweight and portable
- **Automatic Schema** - Database is created automatically
- **Data Persistence** - All data is saved permanently
- **Backup Support** - Easy to backup and restore

## 🛠️ **Technical Details**

### **Architecture:**
- 🐍 **Python 3.11+** - Modern Python features
- 🗄️ **SQLite Database** - Reliable data storage
- 🤖 **python-telegram-bot** - Robust Telegram API wrapper
- 📦 **Modular Design** - Clean, maintainable code structure
- 🔄 **Async/Await** - High-performance asynchronous operations

### **Dependencies:**
```
python-telegram-bot==20.7    # Telegram Bot API
python-dotenv==1.0.0         # Environment variables
schedule==1.2.0              # Reminder scheduling
sqlite3                      # Database (built-in)
```

### **File Structure:**
```
collaborative-todo-bot/
├── collaborative_todo_bot.py    # Main bot application
├── requirements.txt             # Python dependencies
├── env.example                 # Environment variables template
├── Dockerfile                  # Docker configuration
├── railway.json               # Railway deployment config
├── .dockerignore              # Docker build optimization
├── README_COLLABORATIVE.md    # This documentation
└── data/                      # Data storage directory
    └── todo_bot.db            # SQLite database
```

## 🎯 **Use Cases**

### **Team Collaboration:**
- **Project Management** - Track team projects and deadlines
- **Task Distribution** - Assign work to team members
- **Progress Monitoring** - See who's working on what
- **Team Coordination** - Keep everyone aligned

### **Family Organization:**
- **Household Tasks** - Organize family chores
- **Event Planning** - Coordinate family events
- **Responsibility Tracking** - Assign family responsibilities
- **Progress Sharing** - Keep family updated

### **Educational Groups:**
- **Study Groups** - Organize study tasks
- **Project Collaboration** - Work on group projects
- **Assignment Tracking** - Track academic assignments
- **Peer Support** - Help each other stay organized

### **Community Management:**
- **Volunteer Coordination** - Organize volunteer work
- **Event Planning** - Coordinate community events
- **Resource Management** - Track community resources
- **Progress Sharing** - Keep community informed

## 🚀 **Deployment Options**

### **Railway (Recommended):**
- ✅ **Zero Configuration** - Just add your bot token
- 🔄 **Automatic Deployments** - Updates from GitHub
- 📊 **Built-in Monitoring** - Real-time logs and metrics
- 💰 **Cost Effective** - Pay only for what you use
- 🗄️ **Database Persistence** - Data survives restarts

### **Docker:**
- 🐳 **Containerized** - Consistent across environments
- 🔒 **Isolated** - Secure and contained
- 📦 **Portable** - Run anywhere Docker runs
- ⚡ **Fast** - Quick startup and deployment
- 🗄️ **Data Persistence** - Volume mounting for data

### **Local Development:**
- 🛠️ **Full Control** - Customize everything
- 🔧 **Easy Debugging** - Direct access to logs
- ⚡ **Fast Iteration** - Quick testing and development
- 💻 **Local Data** - Keep everything on your machine

## 🎉 **Getting Started**

### **For Personal Use:**
1. **Create your bot** with @BotFather
2. **Deploy to Railway** or run locally
3. **Start chatting** with your bot
4. **Add your first task** with priority
5. **Track your progress** with statistics

### **For Group Collaboration:**
1. **Create your bot** with @BotFather
2. **Deploy to Railway** or run locally
3. **Add bot to your group**
4. **Use /start in the group**
5. **Create group tasks** and assign to members
6. **Track team progress** with group statistics

## 🔒 **Privacy & Security**

### **Data Protection:**
- **User Isolation** - Personal tasks remain private
- **Group Privacy** - Group tasks only visible to members
- **Secure Storage** - All data encrypted in transit
- **Access Control** - Only authorized users can access data

### **Data Management:**
- **Automatic Backup** - Data is saved continuously
- **Easy Export** - Export data when needed
- **Data Retention** - Control how long data is kept
- **Privacy Compliance** - GDPR and privacy compliant

---

**🤝 Ready to collaborate? Start using the Collaborative Telegram To-Do Bot today!**

Perfect for teams, families, and organizations who need to work together on shared tasks with powerful SQL database storage and group collaboration features.
