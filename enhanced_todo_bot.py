#!/usr/bin/env python3
"""
Enhanced Telegram To-Do Bot with Inline Buttons, Reminders & Beautiful Design
A feature-rich bot for managing tasks through Telegram chat.
"""

import json
import os
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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

class EnhancedTodoManager:
    """Enhanced todo manager with reminders and better data structure."""
    
    def __init__(self, filename: str = None):
        data_dir = os.getenv('DATA_DIR', './data')
        os.makedirs(data_dir, exist_ok=True)
        
        if filename is None:
            filename = os.path.join(data_dir, "enhanced_todos.json")
        self.filename = filename
        self.todos = self.load_todos()
        self.reminders = self.load_reminders()
    
    def load_todos(self) -> Dict[str, List[Dict]]:
        """Load todos from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading todos: {e}")
        return {}
    
    def load_reminders(self) -> Dict[str, List[Dict]]:
        """Load reminders from JSON file."""
        reminder_file = self.filename.replace('.json', '_reminders.json')
        if os.path.exists(reminder_file):
            try:
                with open(reminder_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading reminders: {e}")
        return {}
    
    def save_todos(self):
        """Save todos to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving todos: {e}")
    
    def save_reminders(self):
        """Save reminders to JSON file."""
        reminder_file = self.filename.replace('.json', '_reminders.json')
        try:
            with open(reminder_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving reminders: {e}")
    
    def add_todo(self, user_id: str, task: str, priority: str = "medium") -> int:
        """Add a new todo item with priority."""
        if user_id not in self.todos:
            self.todos[user_id] = []
        
        todo_id = len(self.todos[user_id]) + 1
        todo_item = {
            "id": todo_id,
            "task": task,
            "completed": False,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "reminder": None
        }
        
        self.todos[user_id].append(todo_item)
        self.save_todos()
        return todo_id
    
    def get_todos(self, user_id: str, show_completed: bool = False) -> List[Dict]:
        """Get todos for a user."""
        if user_id not in self.todos:
            return []
        
        if show_completed:
            return self.todos[user_id]
        else:
            return [todo for todo in self.todos[user_id] if not todo["completed"]]
    
    def get_todo_by_id(self, user_id: str, todo_id: int) -> Optional[Dict]:
        """Get a specific todo by ID."""
        if user_id not in self.todos:
            return None
        
        for todo in self.todos[user_id]:
            if todo["id"] == todo_id:
                return todo
        return None
    
    def complete_todo(self, user_id: str, todo_id: int) -> bool:
        """Mark a todo as completed."""
        todo = self.get_todo_by_id(user_id, todo_id)
        if todo:
            todo["completed"] = True
            todo["completed_at"] = datetime.now().isoformat()
            self.save_todos()
            return True
        return False
    
    def delete_todo(self, user_id: str, todo_id: int) -> bool:
        """Delete a todo item."""
        if user_id not in self.todos:
            return False
        
        for i, todo in enumerate(self.todos[user_id]):
            if todo["id"] == todo_id:
                del self.todos[user_id][i]
                self.save_todos()
                return True
        return False
    
    def set_priority(self, user_id: str, todo_id: int, priority: str) -> bool:
        """Set priority for a todo."""
        todo = self.get_todo_by_id(user_id, todo_id)
        if todo:
            todo["priority"] = priority
            self.save_todos()
            return True
        return False
    
    def add_reminder(self, user_id: str, todo_id: int, reminder_time: str) -> bool:
        """Add a reminder for a todo."""
        todo = self.get_todo_by_id(user_id, todo_id)
        if todo:
            todo["reminder"] = reminder_time
            self.save_todos()
            
            # Add to reminders tracking
            if user_id not in self.reminders:
                self.reminders[user_id] = []
            
            self.reminders[user_id].append({
                "todo_id": todo_id,
                "reminder_time": reminder_time,
                "task": todo["task"]
            })
            self.save_reminders()
            return True
        return False
    
    def clear_completed(self, user_id: str) -> int:
        """Remove all completed todos for a user and return how many were removed."""
        if user_id not in self.todos:
            return 0
        before = len(self.todos[user_id])
        self.todos[user_id] = [t for t in self.todos[user_id] if not t.get("completed")]
        removed = before - len(self.todos[user_id])
        if removed:
            self.save_todos()
        return removed
    
    def get_priority_emoji(self, priority: str) -> str:
        """Get emoji for priority level."""
        priority_emojis = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🔴",
            "urgent": "🚨"
        }
        return priority_emojis.get(priority, "🟡")
    
    def get_priority_name(self, priority: str) -> str:
        """Get formatted priority name."""
        priority_names = {
            "low": "Low",
            "medium": "Medium",
            "high": "High", 
            "urgent": "Urgent"
        }
        return priority_names.get(priority, "Medium")

# Initialize enhanced todo manager
todo_manager = EnhancedTodoManager()

# Simple in-memory state to handle add-task flows per user
# Structure: user_states[user_id] = { 'awaiting_task': True, 'priority': 'medium', 'reminder_offset': '1h' | '3h' | 'tomorrow' | 'week' | None }
user_states: Dict[str, Dict] = {}

class BotUI:
    """Handles all UI components and formatting."""
    
    @staticmethod
    def get_main_menu_keyboard() -> InlineKeyboardMarkup:
        """Get main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📝 Add Task", callback_data="add_task"),
                InlineKeyboardButton("📋 My Tasks", callback_data="list_tasks")
            ],
            [
                InlineKeyboardButton("✅ Completed", callback_data="completed_tasks"),
                InlineKeyboardButton("⏰ Reminders", callback_data="reminders")
            ],
            [
                InlineKeyboardButton("📊 Statistics", callback_data="stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_task_keyboard(todo_id: int, completed: bool = False) -> InlineKeyboardMarkup:
        """Get keyboard for individual task actions."""
        keyboard = []
        
        if not completed:
            keyboard.append([
                InlineKeyboardButton("✅ Complete", callback_data=f"complete_{todo_id}"),
                InlineKeyboardButton("⏰ Remind", callback_data=f"remind_{todo_id}")
            ])
            keyboard.append([
                InlineKeyboardButton("🔴 High", callback_data=f"priority_{todo_id}_high"),
                InlineKeyboardButton("🟡 Medium", callback_data=f"priority_{todo_id}_medium"),
                InlineKeyboardButton("🟢 Low", callback_data=f"priority_{todo_id}_low")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{todo_id}"),
            InlineKeyboardButton("🔙 Back", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_priority_keyboard() -> InlineKeyboardMarkup:
        """Get priority selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🚨 Urgent", callback_data="priority_urgent"),
                InlineKeyboardButton("🔴 High", callback_data="priority_high")
            ],
            [
                InlineKeyboardButton("🟡 Medium", callback_data="priority_medium"),
                InlineKeyboardButton("🟢 Low", callback_data="priority_low")
            ],
            [
                InlineKeyboardButton("⏰ 1h", callback_data="quicktime_1h"),
                InlineKeyboardButton("⏰ 3h", callback_data="quicktime_3h"),
                InlineKeyboardButton("🌅 Tomorrow", callback_data="quicktime_tomorrow"),
                InlineKeyboardButton("📅 Next Week", callback_data="quicktime_week")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_task(todo: Dict, show_actions: bool = True) -> str:
        """Format a single task for display."""
        status = "✅" if todo["completed"] else "⏳"
        priority_emoji = todo_manager.get_priority_emoji(todo["priority"])
        priority_name = todo_manager.get_priority_name(todo["priority"])
        
        reminder_text = ""
        if todo.get("reminder"):
            reminder_text = f"\n⏰ Reminder: {todo['reminder']}"
        
        task_text = f"{status} *{todo['id']}.* {todo['task']}\n"
        task_text += f"{priority_emoji} Priority: {priority_name}{reminder_text}"
        
        return task_text
    
    @staticmethod
    def format_tasks_list(todos: List[Dict], title: str = "📋 Your Tasks") -> str:
        """Format a list of tasks."""
        if not todos:
            return f"{title}\n\n📝 No tasks found! Add some with the 'Add Task' button below."
        
        message = f"{title}\n\n"
        for todo in todos:
            message += BotUI.format_task(todo) + "\n\n"
        
        return message

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu."""
    welcome_text = """
🎯 *Welcome to your Enhanced To-Do Bot!* ✨

🚀 *Features:*
• 📝 Smart task management
• ⏰ Reminders & notifications  
• 🎨 Beautiful inline interface
• 📊 Progress tracking
• 🏷️ Priority levels
• 📱 Mobile-optimized

Choose an option below to get started! 👇
"""
    
    await update.message.reply_text(
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=BotUI.get_main_menu_keyboard()
    )

    # Initialize user state if not present
    user_id = str(update.effective_user.id)
    if user_id not in user_states:
        user_states[user_id] = { 'awaiting_task': False, 'priority': 'medium', 'reminder_offset': None }

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    help_text = """
❓ *Help & Commands*

*Main Commands:*
• `/start` - Show main menu
• `/add <task>` - Quick add task
• `/list` - Show your tasks

*Features:*
• 🎯 **Priority Levels**: Urgent, High, Medium, Low
• ⏰ **Reminders**: Set custom reminder times
• 📊 **Statistics**: Track your productivity
• 🎨 **Beautiful UI**: Inline buttons for easy navigation

*Quick Tips:*
• Use the inline buttons for best experience
• Set priorities to organize your tasks
• Use reminders to never miss important tasks
• Check statistics to track your progress

Need more help? Just use the buttons below! 👇
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=BotUI.get_main_menu_keyboard()
    )

async def quick_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick add task via command."""
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a task description.\nExample: `/add Buy groceries`",
            reply_markup=BotUI.get_main_menu_keyboard()
        )
        return
    
    task = " ".join(context.args)
    todo_id = todo_manager.add_todo(user_id, task)
    
    await update.message.reply_text(
        f"✅ *Task Added Successfully!*\n\n📝 Task #{todo_id}: {task}\n🟡 Priority: Medium\n\nUse the buttons below to manage your tasks:",
        parse_mode='Markdown',
        reply_markup=BotUI.get_main_menu_keyboard()
    )

# Callback Query Handlers
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    data = query.data
    
    if data == "main_menu":
        await show_main_menu(query)
    elif data == "add_task":
        await show_add_task(query)
    elif data == "list_tasks":
        await show_task_list(query, user_id)
    elif data == "completed_tasks":
        await show_completed_tasks(query, user_id)
    elif data == "reminders":
        await show_reminders(query, user_id)
    elif data == "stats":
        await show_statistics(query, user_id)
    elif data == "settings":
        await show_settings(query)
    elif data == "help":
        await show_help(query)
    elif data.startswith("quicktime_"):
        offset = data.split("_", 1)[1]
        # Set quick reminder offset for next task
        state = user_states.get(user_id, { 'awaiting_task': False, 'priority': 'medium', 'reminder_offset': None })
        state['reminder_offset'] = offset
        user_states[user_id] = state
        await query.edit_message_text(
            f"⏰ *Quick time set:* {offset.replace('h',' hours').title()}\n\nNow send your task description.",
            parse_mode='Markdown',
            reply_markup=BotUI.get_priority_keyboard()
        )
    elif data.startswith("complete_"):
        todo_id = int(data.split("_")[1])
        await complete_task(query, user_id, todo_id)
    elif data.startswith("delete_"):
        todo_id = int(data.split("_")[1])
        await delete_task(query, user_id, todo_id)
    elif data == "clear_completed":
        count = todo_manager.clear_completed(user_id)
        await query.edit_message_text(
            f"🧹 Cleared {count} completed task(s).",
            reply_markup=BotUI.get_main_menu_keyboard()
        )
    elif data.startswith("priority_"):
        if "_" in data.split("_")[1]:
            # Priority for existing task
            parts = data.split("_")
            todo_id = int(parts[1])
            priority = parts[2]
            await set_task_priority(query, user_id, todo_id, priority)
        else:
            # Priority for new task
            priority = data.split("_")[1]
            await handle_new_task_priority(query, user_id, priority)
    elif data.startswith("remind_"):
        parts = data.split("_")
        # Formats supported:
        # remind_{todoId}  -> open options
        # reminder_{todoId}_{option} from show_reminder_options
        if len(parts) == 2:
            todo_id = int(parts[1])
            await show_reminder_options(query, user_id, todo_id)
        else:
            await query.answer()

async def show_main_menu(query: CallbackQuery):
    """Show main menu."""
    welcome_text = """
🎯 *Enhanced To-Do Bot* ✨

Choose what you'd like to do:
"""
    await query.edit_message_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=BotUI.get_main_menu_keyboard()
    )

async def show_add_task(query: CallbackQuery):
    """Show add task interface."""
    text = """
📝 *Add New Task*

Please send me the task description, and I'll add it to your list!

*Example:* "Buy groceries for the week"

You can also preselect a priority or a quick reminder time using the buttons below, then send your task description:
"""
    # Mark user as awaiting task input
    user_id = str(query.from_user.id)
    state = user_states.get(user_id, { 'awaiting_task': False, 'priority': 'medium', 'reminder_offset': None })
    state['awaiting_task'] = True
    user_states[user_id] = state
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=BotUI.get_priority_keyboard()
    )

async def show_task_list(query: CallbackQuery, user_id: str):
    """Show user's task list."""
    todos = todo_manager.get_todos(user_id, show_completed=False)
    # If no tasks, keep existing UI
    if not todos:
        text = BotUI.format_tasks_list(todos, "📋 *Your Active Tasks*")
        keyboard = [
            [InlineKeyboardButton("➕ Add Task", callback_data="add_task")],
            [InlineKeyboardButton("✅ Completed Tasks", callback_data="completed_tasks")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Otherwise, show header + each task with its own inline keyboard
    await query.edit_message_text("📋 *Your Active Tasks*", parse_mode='Markdown')
    for t in todos:
        status = "⏳"
        text = BotUI.format_task(t)
        kb = BotUI.get_task_keyboard(t["id"], completed=False)
        try:
            await query.message.reply_text(text, parse_mode='Markdown', reply_markup=kb)
        except Exception:
            pass
    # Footer with clear button
    footer_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧹 Clear Completed", callback_data="clear_completed")],
        [InlineKeyboardButton("➕ Add Task", callback_data="add_task"), InlineKeyboardButton("✅ Completed", callback_data="completed_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])
    await query.message.reply_text("Use the buttons on each task to manage them.", reply_markup=footer_kb)

async def show_completed_tasks(query: CallbackQuery, user_id: str):
    """Show completed tasks."""
    todos = todo_manager.get_todos(user_id, show_completed=True)
    completed = [todo for todo in todos if todo["completed"]]
    
    if not completed:
        text = "✅ *Completed Tasks*\n\n🎉 No completed tasks yet! Complete some tasks to see them here."
    else:
        text = "✅ *Completed Tasks*\n\n"
        for todo in completed:
            text += BotUI.format_task(todo, show_actions=False) + "\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🧹 Clear Completed", callback_data="clear_completed")],
        [InlineKeyboardButton("📋 Active Tasks", callback_data="list_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_reminders(query: CallbackQuery, user_id: str):
    """Show reminders interface."""
    text = """
⏰ *Reminders*

Set reminders for your tasks to never miss important deadlines!

*How to set reminders:*
1. Go to your task list
2. Click on a task
3. Use the "⏰ Remind" button
4. Choose when you want to be reminded

*Available reminder times:*
• In 1 hour
• In 3 hours  
• Tomorrow
• Next week
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 My Tasks", callback_data="list_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_statistics(query: CallbackQuery, user_id: str):
    """Show user statistics."""
    todos = todo_manager.get_todos(user_id, show_completed=True)
    
    total = len(todos)
    completed = len([t for t in todos if t["completed"]])
    pending = total - completed
    
    # Priority breakdown
    priorities = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
    for todo in todos:
        if not todo["completed"]:
            priorities[todo["priority"]] += 1
    
    text = f"""
📊 *Your Statistics*

📈 *Overview:*
• Total Tasks: {total}
• Completed: {completed} ✅
• Pending: {pending} ⏳
• Completion Rate: {(completed/total*100):.1f}% if total > 0 else 0

🏷️ *Priority Breakdown:*
• 🚨 Urgent: {priorities['urgent']}
• 🔴 High: {priorities['high']}
• 🟡 Medium: {priorities['medium']}
• 🟢 Low: {priorities['low']}

🎯 *Keep up the great work!*
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 My Tasks", callback_data="list_tasks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_settings(query: CallbackQuery):
    """Show settings interface."""
    text = """
⚙️ *Settings*

*Current Settings:*
• Data Storage: JSON file
• Auto-save: Enabled
• Notifications: Enabled

*Available Options:*
• Change data storage location
• Enable/disable notifications
• Set default priority level
• Export/import tasks

*Coming Soon:*
• Custom themes
• Advanced reminder options
• Task categories
• Team collaboration
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_help(query: CallbackQuery):
    """Show help information."""
    help_text = """
❓ *Help & Guide*

*Getting Started:*
1. Use "📝 Add Task" to create new tasks
2. Set priorities to organize your work
3. Use reminders to stay on track
4. Check statistics to see your progress

*Task Management:*
• Click on any task to see options
• Use priority buttons to organize
• Set reminders for important tasks
• Mark tasks as completed when done

*Tips & Tricks:*
• Use urgent priority for critical tasks
• Set reminders for time-sensitive items
• Check statistics regularly
• Keep your task list organized

*Need more help?* Contact support or check the documentation.
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def complete_task(query: CallbackQuery, user_id: str, todo_id: int):
    """Complete a task."""
    if todo_manager.complete_todo(user_id, todo_id):
        await query.edit_message_text(
            f"✅ *Task #{todo_id} Completed!* 🎉\n\nGreat job! Keep up the excellent work!",
            parse_mode='Markdown',
            reply_markup=BotUI.get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            f"❌ Task #{todo_id} not found.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )

async def delete_task(query: CallbackQuery, user_id: str, todo_id: int):
    """Delete a task."""
    if todo_manager.delete_todo(user_id, todo_id):
        await query.edit_message_text(
            f"🗑️ *Task #{todo_id} Deleted!*\n\nTask has been removed from your list.",
            parse_mode='Markdown',
            reply_markup=BotUI.get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            f"❌ Task #{todo_id} not found.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )

async def set_task_priority(query: CallbackQuery, user_id: str, todo_id: int, priority: str):
    """Set priority for a task."""
    if todo_manager.set_priority(user_id, todo_id, priority):
        priority_emoji = todo_manager.get_priority_emoji(priority)
        priority_name = todo_manager.get_priority_name(priority)
        
        await query.edit_message_text(
            f"🏷️ *Priority Updated!*\n\nTask #{todo_id} priority set to {priority_emoji} {priority_name}",
            parse_mode='Markdown',
            reply_markup=BotUI.get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            f"❌ Task #{todo_id} not found.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )

async def handle_new_task_priority(query: CallbackQuery, user_id: str, priority: str):
    """Handle priority selection for new task."""
    priority_emoji = todo_manager.get_priority_emoji(priority)
    priority_name = todo_manager.get_priority_name(priority)
    
    # Update state for upcoming task
    state = user_states.get(user_id, { 'awaiting_task': False, 'priority': 'medium', 'reminder_offset': None })
    state['priority'] = priority
    state['awaiting_task'] = True
    user_states[user_id] = state

    await query.edit_message_text(
        f"🏷️ *Priority Selected: {priority_emoji} {priority_name}*\n\nNow send me the task description and I'll add it with this priority!",
        parse_mode='Markdown',
        reply_markup=BotUI.get_main_menu_keyboard()
    )

async def show_reminder_options(query: CallbackQuery, user_id: str, todo_id: int):
    """Show reminder options for a task."""
    text = f"""
⏰ *Set Reminder for Task #{todo_id}*

Choose when you want to be reminded:

*Quick Options:*
• In 1 hour
• In 3 hours
• Tomorrow morning
• Next week

*Custom Option:*
• Set specific date and time
"""
    
    keyboard = [
        [
            InlineKeyboardButton("⏰ 1 Hour", callback_data=f"reminder_{todo_id}_1h"),
            InlineKeyboardButton("⏰ 3 Hours", callback_data=f"reminder_{todo_id}_3h")
        ],
        [
            InlineKeyboardButton("🌅 Tomorrow", callback_data=f"reminder_{todo_id}_tomorrow"),
            InlineKeyboardButton("📅 Next Week", callback_data=f"reminder_{todo_id}_week")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data=f"task_{todo_id}")
        ]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_reminder_choice(query: CallbackQuery, user_id: str, todo_id: int, option: str):
    """Handle quick reminder option for a specific task."""
    mapping = {
        '1h': '1h',
        '3h': '3h',
        'tomorrow': 'tomorrow',
        'week': 'week'
    }
    offset = mapping.get(option)
    if not offset:
        await query.edit_message_text(
            "❌ Invalid reminder option.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )
        return
    timestamp = _compute_quick_reminder_timestamp(offset)
    if not timestamp:
        await query.edit_message_text(
            "❌ Failed to compute reminder time.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )
        return
    if todo_manager.add_reminder(user_id, todo_id, timestamp):
        await query.edit_message_text(
            f"⏰ Reminder set for task #{todo_id}: {timestamp}",
            reply_markup=BotUI.get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            f"❌ Task #{todo_id} not found.",
            reply_markup=BotUI.get_main_menu_keyboard()
        )

def _compute_quick_reminder_timestamp(offset: Optional[str]) -> Optional[str]:
    """Compute ISO timestamp string for a quick reminder offset label."""
    if not offset:
        return None
    now = datetime.now()
    try:
        if offset == '1h':
            return (now + timedelta(hours=1)).isoformat()
        if offset == '3h':
            return (now + timedelta(hours=3)).isoformat()
        if offset == 'tomorrow':
            # Tomorrow at 9 AM
            tomorrow = now + timedelta(days=1)
            target = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)
            return target.isoformat()
        if offset == 'week':
            # One week from now at 9 AM
            week = now + timedelta(days=7)
            target = datetime(week.year, week.month, week.day, 9, 0, 0)
            return target.isoformat()
    except Exception:
        return None
    return None

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free text when awaiting task description to create a task quickly."""
    user_id = str(update.effective_user.id)
    state = user_states.get(user_id)
    if not state or not state.get('awaiting_task'):
        return  # Ignore regular text not in add flow

    task = update.message.text.strip()
    if not task:
        await update.message.reply_text("❌ Please type a task description.")
        return

    priority = state.get('priority', 'medium')
    reminder_offset = state.get('reminder_offset')
    reminder_time = _compute_quick_reminder_timestamp(reminder_offset)

    todo_id = todo_manager.add_todo(user_id, task, priority=priority)
    # If reminder computed, attach to item
    if reminder_time:
        todo_manager.add_reminder(user_id, todo_id, reminder_time)

    # Reset state
    user_states[user_id] = { 'awaiting_task': False, 'priority': 'medium', 'reminder_offset': None }

    msg = f"✅ *Task Added!*\n\n📝 Task #{todo_id}: {task}\n{todo_manager.get_priority_emoji(priority)} Priority: {todo_manager.get_priority_name(priority)}"
    if reminder_time:
        msg += f"\n⏰ Reminder set: {reminder_time}"
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=BotUI.get_main_menu_keyboard())

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/list - show pending tasks"""
    user_id = str(update.effective_user.id)
    todos = todo_manager.get_todos(user_id, show_completed=False)
    text = BotUI.format_tasks_list(todos, "📋 *Your Active Tasks*")
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/all - show all tasks"""
    user_id = str(update.effective_user.id)
    todos = todo_manager.get_todos(user_id, show_completed=True)
    pending = [t for t in todos if not t["completed"]]
    completed = [t for t in todos if t["completed"]]
    if not todos:
        await update.message.reply_text("📝 No tasks found. Use /add to create one.")
        return
    message = "📋 *All Tasks*\n\n"
    if pending:
        message += "⏳ *Pending:*\n"
        for t in pending:
            message += f"• {t['id']}. {t['task']}\n"
        message += "\n"
    if completed:
        message += "✅ *Completed:*\n"
        for t in completed:
            message += f"• {t['id']}. {t['task']}\n"
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmd_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/completed - show only completed tasks"""
    user_id = str(update.effective_user.id)
    todos = [t for t in todo_manager.get_todos(user_id, show_completed=True) if t["completed"]]
    if not todos:
        await update.message.reply_text("✅ No completed tasks yet.")
        return
    text = "✅ *Completed Tasks*\n\n"
    for t in todos:
        text += f"• {t['id']}. {t['task']}\n"
    await update.message.reply_text(text, parse_mode='Markdown')

# Reminder System
class ReminderScheduler:
    """Handles reminder scheduling and notifications."""
    
    def __init__(self, application: Application):
        self.application = application
        self.running = False
    
    def start(self):
        """Start the reminder scheduler."""
        self.running = True
        thread = threading.Thread(target=self._run_scheduler, daemon=True)
        thread.start()
        logger.info("⏰ Reminder scheduler started")
    
    def _run_scheduler(self):
        """Run the reminder scheduler in a separate thread."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in reminder scheduler: {e}")
    
    def stop(self):
        """Stop the reminder scheduler."""
        self.running = False
        logger.info("⏰ Reminder scheduler stopped")

async def send_daily_summary(context: ContextTypes.DEFAULT_TYPE):
    """Send daily summary of completed and pending tasks to each user."""
    application = context.application
    for user_id, todos in list(todo_manager.todos.items()):
        try:
            pending = [t for t in todos if not t.get('completed')]
            completed = [t for t in todos if t.get('completed')]
            if not pending and not completed:
                continue
            text = """📅 *Your Daily To-Do Summary*

"""
            if pending:
                text += "⏳ *Pending:*\n"
                for t in pending:
                    text += f"• {t['id']}. {t['task']}\n"
                text += "\n"
            if completed:
                text += "✅ *Completed:*\n"
                for t in completed:
                    text += f"• {t['id']}. {t['task']}\n"
            await application.bot.send_message(chat_id=int(user_id), text=text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send summary to {user_id}: {e}")

# Global reminder scheduler
reminder_scheduler = None

def main():
    """Start the enhanced bot."""
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set your bot token in the .env file or environment variables")
        return
    
    # Log startup information
    logger.info("🤖 Starting Enhanced Telegram To-Do Bot...")
    logger.info(f"📁 Data directory: {os.getenv('DATA_DIR', './data')}")
    logger.info(f"💾 Data file: {todo_manager.filename}")
    
    try:
        application = Application.builder().token("7784108003:AAFys4pF-XpXn1CgkUVVwsAIGIRYBfwsRYg").build()
        job_queue = application.job_queue

        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("add", quick_add))
        application.add_handler(CommandHandler("todo", quick_add))
        application.add_handler(CommandHandler("list", cmd_list))
        application.add_handler(CommandHandler("all", cmd_all))
        application.add_handler(CommandHandler("completed", cmd_completed))
        
        # Add callback query handler (route reminder choices too)
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        application.add_handler(CallbackQueryHandler(lambda u, c: handle_reminder_choice(
            u.callback_query, str(u.effective_user.id), int(u.callback_query.data.split('_')[1]), u.callback_query.data.split('_')[2]
        ), pattern=r"^reminder_\\d+_(1h|3h|tomorrow|week)$"))

        # Handle free text for quick add flow
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))
        
        # Start reminder scheduler
        global reminder_scheduler
        reminder_scheduler = ReminderScheduler(application)
        reminder_scheduler.start()

        # Schedule daily summary (default 21:00 server time or env DAILY_SUMMARY_HOUR)
        try:
            hour = int(os.getenv('DAILY_SUMMARY_HOUR', '21'))
            minute = int(os.getenv('DAILY_SUMMARY_MINUTE', '0'))
        except ValueError:
            hour, minute = 21, 0
        application.job_queue.run_daily(send_daily_summary, time=datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0).time())
        
        # Start the bot
        logger.info("🚀 Enhanced bot is ready with inline buttons and reminders!")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
