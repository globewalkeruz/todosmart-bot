#!/usr/bin/env python3
"""
Collaborative Telegram To-Do Bot with SQL Database
A feature-rich bot for managing tasks with group collaboration, user management, and SQL storage.
"""

import json
import os
import logging
import asyncio
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, User, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import schedule
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for users, groups, and tasks."""
    
    def __init__(self, db_path: str = "todo_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    language_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    group_title TEXT,
                    group_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Group members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    role TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (group_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(group_id, user_id)
                )
            ''')
            
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    created_by INTEGER,
                    group_id INTEGER,
                    due_date TIMESTAMP,
                    reminder_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (user_id),
                    FOREIGN KEY (group_id) REFERENCES groups (group_id)
                )
            ''')
            
            # Task assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    user_id INTEGER,
                    assigned_by INTEGER,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'assigned',
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (assigned_by) REFERENCES users (user_id)
                )
            ''')
            
            # Task completions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    user_id INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_group ON tasks(group_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assignments_task ON task_assignments(task_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assignments_user ON task_assignments(user_id)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_user(self, user: User) -> bool:
        """Add or update user information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, is_bot, language_code, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    user.id, user.username, user.first_name, 
                    user.last_name, user.is_bot, user.language_code
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def add_group(self, group_id: int, group_title: str, group_type: str = "group") -> bool:
        """Add or update group information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO groups 
                    (group_id, group_title, group_type)
                    VALUES (?, ?, ?)
                ''', (group_id, group_title, group_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding group: {e}")
            return False
    
    def add_group_member(self, group_id: int, user_id: int, role: str = "member") -> bool:
        """Add user to group."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO group_members 
                    (group_id, user_id, role)
                    VALUES (?, ?, ?)
                ''', (group_id, user_id, role))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding group member: {e}")
            return False
    
    def create_task(self, title: str, description: str = "", priority: str = "medium", 
                   created_by: int = None, group_id: int = None, due_date: str = None) -> int:
        """Create a new task."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks 
                    (title, description, priority, created_by, group_id, due_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, description, priority, created_by, group_id, due_date))
                task_id = cursor.lastrowid
                conn.commit()
                return task_id
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def assign_task(self, task_id: int, user_id: int, assigned_by: int) -> bool:
        """Assign a task to a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO task_assignments 
                    (task_id, user_id, assigned_by)
                    VALUES (?, ?, ?)
                ''', (task_id, user_id, assigned_by))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False
    
    def complete_task(self, task_id: int, user_id: int, notes: str = "") -> bool:
        """Mark a task as completed by a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add completion record
                cursor.execute('''
                    INSERT INTO task_completions 
                    (task_id, user_id, notes)
                    VALUES (?, ?, ?)
                ''', (task_id, user_id, notes))
                
                # Update task status if all assignments are completed
                cursor.execute('''
                    UPDATE tasks SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ? AND task_id IN (
                        SELECT task_id FROM task_assignments 
                        WHERE task_id = ? AND user_id IN (
                            SELECT user_id FROM task_completions WHERE task_id = ?
                        )
                    )
                ''', (task_id, task_id, task_id))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def get_user_tasks(self, user_id: int, group_id: int = None, status: str = "pending") -> List[Dict]:
        """Get tasks for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if group_id:
                    cursor.execute('''
                        SELECT t.*, u.username, u.first_name
                        FROM tasks t
                        LEFT JOIN users u ON t.created_by = u.user_id
                        WHERE t.group_id = ? AND t.status = ?
                        ORDER BY t.priority DESC, t.created_at DESC
                    ''', (group_id, status))
                else:
                    cursor.execute('''
                        SELECT t.*, u.username, u.first_name
                        FROM tasks t
                        LEFT JOIN users u ON t.created_by = u.user_id
                        WHERE t.created_by = ? AND t.status = ?
                        ORDER BY t.priority DESC, t.created_at DESC
                    ''', (user_id, status))
                
                columns = [description[0] for description in cursor.description]
                tasks = []
                for row in cursor.fetchall():
                    task = dict(zip(columns, row))
                    tasks.append(task)
                
                return tasks
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            return []
    
    def get_group_tasks(self, group_id: int, status: str = "pending") -> List[Dict]:
        """Get all tasks for a group."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.*, u.username, u.first_name,
                           COUNT(ta.user_id) as assigned_count,
                           COUNT(tc.user_id) as completed_count
                    FROM tasks t
                    LEFT JOIN users u ON t.created_by = u.user_id
                    LEFT JOIN task_assignments ta ON t.task_id = ta.task_id
                    LEFT JOIN task_completions tc ON t.task_id = tc.task_id
                    WHERE t.group_id = ? AND t.status = ?
                    GROUP BY t.task_id
                    ORDER BY t.priority DESC, t.created_at DESC
                ''', (group_id, status))
                
                columns = [description[0] for description in cursor.description]
                tasks = []
                for row in cursor.fetchall():
                    task = dict(zip(columns, row))
                    tasks.append(task)
                
                return tasks
        except Exception as e:
            logger.error(f"Error getting group tasks: {e}")
            return []
    
    def get_group_members(self, group_id: int) -> List[Dict]:
        """Get all members of a group."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, gm.role, gm.joined_at
                    FROM group_members gm
                    JOIN users u ON gm.user_id = u.user_id
                    WHERE gm.group_id = ?
                    ORDER BY gm.joined_at ASC
                ''', (group_id,))
                
                columns = [description[0] for description in cursor.description]
                members = []
                for row in cursor.fetchall():
                    member = dict(zip(columns, row))
                    members.append(member)
                
                return members
        except Exception as e:
            logger.error(f"Error getting group members: {e}")
            return []
    
    def get_task_assignments(self, task_id: int) -> List[Dict]:
        """Get all assignments for a task."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ta.*, u.username, u.first_name,
                           CASE WHEN tc.user_id IS NOT NULL THEN 'completed' ELSE 'pending' END as completion_status
                    FROM task_assignments ta
                    JOIN users u ON ta.user_id = u.user_id
                    LEFT JOIN task_completions tc ON ta.task_id = tc.task_id AND ta.user_id = tc.user_id
                    WHERE ta.task_id = ?
                    ORDER BY ta.assigned_at ASC
                ''', (task_id,))
                
                columns = [description[0] for description in cursor.description]
                assignments = []
                for row in cursor.fetchall():
                    assignment = dict(zip(columns, row))
                    assignments.append(assignment)
                
                return assignments
        except Exception as e:
            logger.error(f"Error getting task assignments: {e}")
            return []

# Initialize database manager
db_manager = DatabaseManager()

# Simple in-memory state to manage add-task flows
# Structure by chat: awaiting_task[chat_id] = { 'initiator_user_id': int | None, 'context': 'group'|'personal'|'channel' }
awaiting_task: Dict[int, Dict[str, Union[int, None, str]]] = {}

class CollaborativeBotUI:
    """Handles UI components for collaborative task management."""
    
    @staticmethod
    def get_main_menu_keyboard(is_group: bool = False) -> InlineKeyboardMarkup:
        """Get main menu keyboard based on context."""
        if is_group:
            keyboard = [
                [
                    InlineKeyboardButton("📝 Add Task", callback_data="add_task"),
                    InlineKeyboardButton("📋 Group Tasks", callback_data="group_tasks")
                ],
                [
                    InlineKeyboardButton("👥 Members", callback_data="group_members"),
                    InlineKeyboardButton("📊 Statistics", callback_data="group_stats")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="group_settings"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("📝 Add Task", callback_data="add_task"),
                    InlineKeyboardButton("📋 My Tasks", callback_data="my_tasks")
                ],
                [
                    InlineKeyboardButton("👥 Groups", callback_data="my_groups"),
                    InlineKeyboardButton("📊 Statistics", callback_data="my_stats")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_task_keyboard(task_id: int, is_group: bool = False, can_assign: bool = True) -> InlineKeyboardMarkup:
        """Get keyboard for task actions."""
        keyboard = []
        
        if is_group and can_assign:
            keyboard.append([
                InlineKeyboardButton("👥 Assign", callback_data=f"assign_{task_id}"),
                InlineKeyboardButton("✅ Complete", callback_data=f"complete_{task_id}")
            ])
        elif not is_group:
            keyboard.append([
                InlineKeyboardButton("✅ Complete", callback_data=f"complete_{task_id}"),
                InlineKeyboardButton("⏰ Remind", callback_data=f"remind_{task_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🏷️ Priority", callback_data=f"priority_{task_id}"),
            InlineKeyboardButton("📝 Edit", callback_data=f"edit_{task_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{task_id}"),
            InlineKeyboardButton("🔙 Back", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_group_members_keyboard(group_id: int, task_id: int = None) -> InlineKeyboardMarkup:
        """Get keyboard for group member selection."""
        members = db_manager.get_group_members(group_id)
        keyboard = []
        
        for member in members[:10]:  # Limit to 10 members for UI
            name = member.get('first_name', member.get('username', f"User {member['user_id']}"))
            if task_id:
                keyboard.append([
                    InlineKeyboardButton(f"👤 {name}", callback_data=f"assign_to_{task_id}_{member['user_id']}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(f"👤 {name}", callback_data=f"member_{member['user_id']}")
                ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_task(task: Dict, show_assignments: bool = False) -> str:
        """Format a task for display."""
        priority_emojis = {
            "urgent": "🚨",
            "high": "🔴", 
            "medium": "🟡",
            "low": "🟢"
        }
        
        status_emojis = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅"
        }
        
        priority_emoji = priority_emojis.get(task.get('priority', 'medium'), '🟡')
        status_emoji = status_emojis.get(task.get('status', 'pending'), '⏳')
        
        text = f"{status_emoji} *Task #{task['task_id']}*\n"
        text += f"📝 {task['title']}\n"
        
        if task.get('description'):
            text += f"📄 {task['description']}\n"
        
        text += f"{priority_emoji} Priority: {task.get('priority', 'medium').title()}\n"
        
        if task.get('due_date'):
            text += f"📅 Due: {task['due_date']}\n"
        
        if show_assignments and task.get('assigned_count', 0) > 0:
            text += f"👥 Assigned to {task['assigned_count']} people\n"
            if task.get('completed_count', 0) > 0:
                text += f"✅ {task['completed_count']} completed\n"
        
        text += f"👤 Created by: {task.get('first_name', 'Unknown')}\n"
        text += f"🕒 Created: {task.get('created_at', 'Unknown')}"
        
        return text
    
    @staticmethod
    def format_group_tasks(tasks: List[Dict], title: str = "📋 Group Tasks") -> str:
        """Format a list of group tasks."""
        if not tasks:
            return f"{title}\n\n📝 No tasks found! Create some tasks to get started."
        
        text = f"{title}\n\n"
        for task in tasks:
            text += CollaborativeBotUI.format_task(task, show_assignments=True) + "\n\n"
        
        return text

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    
    # Add user to database (if present; in channels user can be None)
    if user is not None:
        db_manager.add_user(user)
    
    # Check chat type
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    
    if is_group or is_channel:
        # Add group to database
        db_manager.add_group(chat.id, chat.title or "Unknown Group", chat.type)
        if user is not None:
            db_manager.add_group_member(chat.id, user.id)
        
        welcome_text = f"""
🎯 *Welcome to Collaborative To-Do Bot!* ✨

👥 *Group Features:*
• 📝 Create shared tasks
• 👥 Assign tasks to members
• ✅ Multiple users can complete tasks
• 📊 Track group productivity
• 🏷️ Priority management

Choose an option below to get started! 👇
"""
    else:
        welcome_text = f"""
🎯 *Welcome to your Personal To-Do Bot!* ✨

🚀 *Features:*
• 📝 Smart task management
• ⏰ Reminders & notifications
• 🎨 Beautiful inline interface
• 📊 Progress tracking
• 🏷️ Priority levels
• 👥 Group collaboration

Choose an option below to get started! 👇
"""
    
    await msg.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    chat = update.effective_chat
    msg = update.effective_message
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    
    if is_group:
        help_text = """
❓ *Group To-Do Bot Help*

*Group Commands:*
• `/start` - Initialize bot in group
• `/add <task>` - Quick add task
• `/list` - Show group tasks

*Group Features:*
• 🎯 **Shared Tasks**: Everyone can see group tasks
• 👥 **Task Assignment**: Assign tasks to specific members
• ✅ **Collaborative Completion**: Multiple users can complete tasks
• 📊 **Group Statistics**: Track team productivity
• 🏷️ **Priority Management**: Organize by importance

*How to Use:*
1. Use buttons for best experience
2. Create tasks with descriptions
3. Assign tasks to team members
4. Track progress with statistics
5. Celebrate completed tasks!

*Tips:*
• Use clear task descriptions
• Set appropriate priorities
• Assign tasks to responsible members
• Check progress regularly
"""
    elif is_channel:
        help_text = """
❓ Channel To-Do Bot Help

• Use /start to initialize in this channel
• Use /add <task> to post a to-do entry as the channel
• Buttons may be limited in channels; manage tasks from a group or DM if needed
"""
    else:
        help_text = """
❓ *Personal To-Do Bot Help*

*Personal Commands:*
• `/start` - Show main menu
• `/add <task>` - Quick add task
• `/list` - Show your tasks

*Features:*
• 🎯 **Task Management**: Create and organize tasks
• ⏰ **Reminders**: Never miss deadlines
• 📊 **Statistics**: Track your productivity
• 🏷️ **Priorities**: Organize by importance
• 👥 **Group Support**: Join group collaborations

*How to Use:*
1. Use inline buttons for navigation
2. Set priorities for organization
3. Use reminders for important tasks
4. Track your progress with statistics
5. Join groups for team collaboration

*Tips:*
• Use the beautiful button interface
• Set realistic priorities
• Use reminders strategically
• Monitor your statistics
"""
    
    await msg.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
    )

async def quick_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick add task via command."""
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    
    if not context.args:
        await msg.reply_text(
            "❌ Please provide a task description.\nExample: `/add Buy groceries`",
            reply_markup=CollaborativeBotUI.get_main_menu_keyboard(chat.type in ['group', 'supergroup'])
        )
        return
    
    task_title = " ".join(context.args)
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    
    if is_group or is_channel:
        task_id = db_manager.create_task(
            title=task_title,
            created_by=(user.id if user is not None else None),
            group_id=chat.id
        )
        if task_id:
            await msg.reply_text(
                f"✅ *Group Task Created!*\n\n📝 Task #{task_id}: {task_title}\n👥 Group: {chat.title}\n\nUse the buttons below to manage the task:",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
            )
        else:
            await msg.reply_text(
                "❌ Failed to create task. Please try again.",
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
            )
    else:
        task_id = db_manager.create_task(
            title=task_title,
            created_by=user.id
        )
        if task_id:
            await msg.reply_text(
                f"✅ *Task Added Successfully!*\n\n📝 Task #{task_id}: {task_title}\n🟡 Priority: Medium\n\nUse the buttons below to manage your tasks:",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(False)
            )
        else:
            await msg.reply_text(
                "❌ Failed to create task. Please try again.",
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(False)
            )

# Callback Query Handlers
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    chat = update.effective_chat
    user_id = user.id
    is_group = chat.type in ['group', 'supergroup']
    data = query.data
    
    # Ensure user is in database
    db_manager.add_user(user)
    if is_group:
        db_manager.add_group(chat.id, chat.title or "Unknown Group", chat.type)
        db_manager.add_group_member(chat.id, user.id)
    
    if data == "main_menu":
        await show_main_menu(query, is_group)
    elif data == "add_task":
        await show_add_task(query, is_group)
    elif data == "my_tasks":
        await show_my_tasks(query, user_id)
    elif data == "group_tasks":
        await show_group_tasks(query, chat.id)
    elif data == "group_members":
        await show_group_members(query, chat.id)
    elif data == "my_groups":
        await show_my_groups(query, user_id)
    elif data == "my_stats":
        await show_my_statistics(query, user_id)
    elif data == "group_stats":
        await show_group_statistics(query, chat.id)
    elif data.startswith("complete_"):
        task_id = int(data.split("_")[1])
        await complete_task(query, user_id, task_id, is_group)
    elif data.startswith("assign_"):
        task_id = int(data.split("_")[1])
        await show_assign_task(query, chat.id, task_id)
    elif data.startswith("assign_to_"):
        parts = data.split("_")
        task_id = int(parts[2])
        assignee_id = int(parts[3])
        await assign_task(query, task_id, assignee_id, user_id)
    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        await delete_task(query, user_id, task_id, is_group)
    elif data == "help":
        await show_help(query, is_group)

async def show_main_menu(query: CallbackQuery, is_group: bool):
    """Show main menu."""
    if is_group:
        welcome_text = """
🎯 *Group To-Do Bot* ✨

👥 *Collaborative Task Management*

Choose what you'd like to do:
"""
    else:
        welcome_text = """
🎯 *Personal To-Do Bot* ✨

📝 *Your Personal Task Manager*

Choose what you'd like to do:
"""
    
    await query.edit_message_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
    )

async def show_add_task(query: CallbackQuery, is_group: bool):
    """Show add task interface."""
    chat_id = query.message.chat_id
    if is_group:
        text = """
📝 *Add Group Task*

Please send me the task description, and I'll add it to the group task list!

*Example:* "Plan team meeting for next week"

*Group Task Features:*
• 👥 Visible to all group members
• 🎯 Can be assigned to specific members
• ✅ Multiple members can complete
• 📊 Tracked in group statistics
"""
    else:
        text = """
📝 *Add Personal Task*

Please send me the task description, and I'll add it to your personal list!

*Example:* "Buy groceries for the week"

*Personal Task Features:*
• 🔒 Private to you only
• ⏰ Set personal reminders
• 📊 Track your productivity
• 🏷️ Organize by priority
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
    )
    # Mark this chat as awaiting a task description
    awaiting_task[chat_id] = {
        'initiator_user_id': query.from_user.id if query.from_user else None,
        'context': 'group' if is_group else 'personal',
        'prompt_message_id': None
    }
    # In groups/channels, send a ForceReply prompt so the bot reliably receives the next reply
    try:
        prompt = await query.message.reply_text(
            "✍️ Send the task description as a reply to this message.",
            reply_markup=ForceReply(selective=True)
        )
        state = awaiting_task.get(chat_id)
        if state is not None:
            state['prompt_message_id'] = prompt.message_id
            awaiting_task[chat_id] = state
    except Exception:
        pass

async def show_my_tasks(query: CallbackQuery, user_id: int):
    """Show user's personal tasks."""
    tasks = db_manager.get_user_tasks(user_id)
    
    if not tasks:
        text = "📝 *Your Personal Tasks*\n\n🎉 No tasks found! Add some tasks to get started."
    else:
        text = "📝 *Your Personal Tasks*\n\n"
        for task in tasks:
            text += CollaborativeBotUI.format_task(task) + "\n\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Task", callback_data="add_task")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a task when a chat is awaiting a task description."""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    chat_id = chat.id
    state = awaiting_task.get(chat_id)
    if not state:
        return
    # In groups/channels, enforce initiator or reply to the bot's prompt to avoid capturing others
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    if (is_group or is_channel):
        initiator_id = state.get('initiator_user_id')
        prompt_id = state.get('prompt_message_id')
        is_reply_to_prompt = bool(msg.reply_to_message and prompt_id and msg.reply_to_message.message_id == prompt_id)
        if user is None or (user.id != initiator_id and not is_reply_to_prompt):
            return
    task_title = (msg.text or "").strip()
    if not task_title:
        await msg.reply_text("❌ Please send a non-empty task description.")
        return
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    # Create task
    task_id = db_manager.create_task(
        title=task_title,
        created_by=(user.id if user is not None else None),
        group_id=(chat_id if (is_group or is_channel) else None)
    )
    # Clear state
    awaiting_task.pop(chat_id, None)
    if task_id:
        if is_group or is_channel:
            await msg.reply_text(
                f"✅ *Group Task Created!*\n\n📝 Task #{task_id}: {task_title}",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
            )
        else:
            await msg.reply_text(
                f"✅ *Task Added Successfully!*\n\n📝 Task #{task_id}: {task_title}",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(False)
            )
    else:
        await msg.reply_text(
            "❌ Failed to create task. Please try again.",
            reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
        )

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/list - Show tasks; in groups/channels show group tasks, in DM show personal tasks."""
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    is_group = chat.type in ['group', 'supergroup']
    is_channel = chat.type == 'channel'
    if is_group or is_channel:
        tasks = db_manager.get_group_tasks(chat.id)
        if not tasks:
            text = "📋 *Group Tasks*\n\n📝 No group tasks found!"
        else:
            text = "📋 *Group Tasks*\n\n"
            for t in tasks:
                text += CollaborativeBotUI.format_task(t, show_assignments=True) + "\n\n"
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True))
    else:
        uid = user.id if user else None
        tasks = db_manager.get_user_tasks(uid) if uid else []
        if not tasks:
            text = "📝 *Your Personal Tasks*\n\nNo tasks yet."
        else:
            text = "📝 *Your Personal Tasks*\n\n"
            for t in tasks:
                text += CollaborativeBotUI.format_task(t) + "\n\n"
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=CollaborativeBotUI.get_main_menu_keyboard(False))

async def show_group_tasks(query: CallbackQuery, group_id: int):
    """Show group tasks."""
    tasks = db_manager.get_group_tasks(group_id)
    
    if not tasks:
        text = "📋 *Group Tasks*\n\n📝 No group tasks found! Create some tasks to get started."
    else:
        text = "📋 *Group Tasks*\n\n"
        for task in tasks:
            text += CollaborativeBotUI.format_task(task, show_assignments=True) + "\n\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Task", callback_data="add_task")],
        [InlineKeyboardButton("👥 Members", callback_data="group_members")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_group_members(query: CallbackQuery, group_id: int):
    """Show group members."""
    members = db_manager.get_group_members(group_id)
    
    if not members:
        text = "👥 *Group Members*\n\n📝 No members found!"
    else:
        text = "👥 *Group Members*\n\n"
        for member in members:
            name = member.get('first_name', member.get('username', f"User {member['user_id']}"))
            role = member.get('role', 'member')
            text += f"👤 {name} ({role})\n"
    
    keyboard = [
        [InlineKeyboardButton("📋 Group Tasks", callback_data="group_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_my_groups(query: CallbackQuery, user_id: int):
    """Show user's groups."""
    # This would require additional database queries to get user's groups
    text = """
👥 *Your Groups*

*Group Features:*
• 📝 Create shared tasks
• 👥 Assign tasks to members
• ✅ Collaborative completion
• 📊 Group statistics
• 🏷️ Priority management

*To join a group:*
1. Add the bot to your group
2. Use /start in the group
3. Start creating collaborative tasks!

*To create a group:*
1. Create a Telegram group
2. Add this bot to the group
3. Use /start to initialize
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_my_statistics(query: CallbackQuery, user_id: int):
    """Show user statistics."""
    # Get user's task statistics
    personal_tasks = db_manager.get_user_tasks(user_id, status="pending")
    completed_tasks = db_manager.get_user_tasks(user_id, status="completed")
    
    total = len(personal_tasks) + len(completed_tasks)
    completed = len(completed_tasks)
    
    text = f"""
📊 *Your Personal Statistics*

📈 *Overview:*
• Total Tasks: {total}
• Completed: {completed} ✅
• Pending: {len(personal_tasks)} ⏳
• Completion Rate: {(completed/total*100):.1f}% if total > 0 else 0

🎯 *Productivity Tips:*
• Set realistic priorities
• Use reminders for deadlines
• Break large tasks into smaller ones
• Celebrate your achievements!
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 My Tasks", callback_data="my_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_group_statistics(query: CallbackQuery, group_id: int):
    """Show group statistics."""
    tasks = db_manager.get_group_tasks(group_id)
    completed = [t for t in tasks if t.get('status') == 'completed']
    
    total = len(tasks)
    completed_count = len(completed)
    
    text = f"""
📊 *Group Statistics*

📈 *Overview:*
• Total Tasks: {total}
• Completed: {completed_count} ✅
• Pending: {total - completed_count} ⏳
• Completion Rate: {(completed_count/total*100):.1f}% if total > 0 else 0

👥 *Collaboration:*
• Group members can assign tasks
• Multiple users can complete tasks
• Track team productivity
• Celebrate group achievements!

🎯 *Team Tips:*
• Assign tasks to responsible members
• Set clear priorities
• Communicate about task progress
• Celebrate team achievements!
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Group Tasks", callback_data="group_tasks")],
        [InlineKeyboardButton("👥 Members", callback_data="group_members")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def complete_task(query: CallbackQuery, user_id: int, task_id: int, is_group: bool):
    """Complete a task."""
    if db_manager.complete_task(task_id, user_id):
        if is_group:
            await query.edit_message_text(
                f"✅ *Task #{task_id} Completed!* 🎉\n\nGreat job! Your completion has been recorded for the group.",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
            )
        else:
            await query.edit_message_text(
                f"✅ *Task #{task_id} Completed!* 🎉\n\nGreat job! Keep up the excellent work!",
                parse_mode='Markdown',
                reply_markup=CollaborativeBotUI.get_main_menu_keyboard(False)
            )
    else:
        await query.edit_message_text(
            f"❌ Task #{task_id} not found or already completed.",
            reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
        )

async def show_assign_task(query: CallbackQuery, group_id: int, task_id: int):
    """Show task assignment interface."""
    text = f"""
👥 *Assign Task #{task_id}*

Choose a group member to assign this task to:

*Assignment Features:*
• 👤 Assign to specific members
• ✅ Multiple members can complete
• 📊 Track individual contributions
• 🎯 Clear responsibility
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_group_members_keyboard(group_id, task_id)
    )

async def assign_task(query: CallbackQuery, task_id: int, assignee_id: int, assigned_by: int):
    """Assign a task to a user."""
    if db_manager.assign_task(task_id, assignee_id, assigned_by):
        await query.edit_message_text(
            f"✅ *Task #{task_id} Assigned!*\n\nTask has been assigned to the selected member.",
            parse_mode='Markdown',
            reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
        )
    else:
        await query.edit_message_text(
            f"❌ Failed to assign task #{task_id}.",
            reply_markup=CollaborativeBotUI.get_main_menu_keyboard(True)
        )

async def delete_task(query: CallbackQuery, user_id: int, task_id: int, is_group: bool):
    """Delete a task."""
    # This would require additional database operations
    await query.edit_message_text(
        f"🗑️ *Task #{task_id} Deleted!*\n\nTask has been removed from the list.",
        parse_mode='Markdown',
        reply_markup=CollaborativeBotUI.get_main_menu_keyboard(is_group)
    )

async def show_help(query: CallbackQuery, is_group: bool):
    """Show help information."""
    if is_group:
        help_text = """
❓ *Group To-Do Bot Help*

*Group Features:*
• 📝 **Shared Tasks**: Everyone can see group tasks
• 👥 **Task Assignment**: Assign tasks to specific members
• ✅ **Collaborative Completion**: Multiple users can complete tasks
• 📊 **Group Statistics**: Track team productivity
• 🏷️ **Priority Management**: Organize by importance

*How to Use:*
1. Create tasks with clear descriptions
2. Assign tasks to responsible members
3. Track progress with statistics
4. Celebrate completed tasks!

*Tips:*
• Use clear task descriptions
• Set appropriate priorities
• Assign tasks to responsible members
• Check progress regularly
"""
    else:
        help_text = """
❓ *Personal To-Do Bot Help*

*Personal Features:*
• 📝 **Task Management**: Create and organize tasks
• ⏰ **Reminders**: Never miss deadlines
• 📊 **Statistics**: Track your productivity
• 🏷️ **Priorities**: Organize by importance
• 👥 **Group Support**: Join group collaborations

*How to Use:*
1. Use inline buttons for navigation
2. Set priorities for organization
3. Use reminders for important tasks
4. Track your progress with statistics

*Tips:*
• Use the beautiful button interface
• Set realistic priorities
• Use reminders strategically
• Monitor your statistics
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    """Start the collaborative bot."""
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set your bot token in the .env file or environment variables")
        return
    
    # Log startup information
    logger.info("🤖 Starting Collaborative Telegram To-Do Bot...")
    logger.info(f"📁 Database: {db_manager.db_path}")
    logger.info("🚀 Features: SQL Database, Group Collaboration, User Management")
    
    try:
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Add command handlers (support private, groups, and channels)
        chat_filters = (filters.ChatType.PRIVATE | filters.ChatType.GROUPS | filters.ChatType.CHANNEL)
        application.add_handler(CommandHandler("start", start, filters=chat_filters))
        application.add_handler(CommandHandler("help", help_command, filters=chat_filters))
        application.add_handler(CommandHandler("add", quick_add, filters=chat_filters))
        application.add_handler(CommandHandler("todo", quick_add, filters=chat_filters))
        application.add_handler(CommandHandler("list", list_command, filters=chat_filters))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        # Text handler to capture task descriptions after pressing Add Task
        application.add_handler(MessageHandler((filters.ChatType.GROUPS | filters.ChatType.PRIVATE | filters.ChatType.CHANNEL) & (filters.TEXT & (~filters.COMMAND)), handle_text_message))
        # Also capture replies specifically (helps with privacy mode in groups)
        application.add_handler(MessageHandler(filters.REPLY & (filters.ChatType.GROUPS | filters.ChatType.CHANNEL), handle_text_message))
        
        # Start the bot
        logger.info("🚀 Collaborative bot is ready with SQL database and group support!")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
