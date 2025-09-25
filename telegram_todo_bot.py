#!/usr/bin/env python3
"""
Telegram To-Do Bot
A simple bot for managing tasks through Telegram chat.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TodoManager:
    """Manages todo items with JSON file persistence."""
    
    def __init__(self, filename: str = None):
        # Use environment variable for data directory or default to current directory
        data_dir = os.getenv('DATA_DIR', '.')
        if filename is None:
            filename = os.path.join(data_dir, "todos.json")
        self.filename = filename
        self.todos = self.load_todos()
    
    def load_todos(self) -> Dict[str, List[Dict]]:
        """Load todos from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading todos: {e}")
        return {}
    
    def save_todos(self):
        """Save todos to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving todos: {e}")
    
    def add_todo(self, user_id: str, task: str) -> int:
        """Add a new todo item."""
        if user_id not in self.todos:
            self.todos[user_id] = []
        
        todo_id = len(self.todos[user_id]) + 1
        todo_item = {
            "id": todo_id,
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat()
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
    
    def complete_todo(self, user_id: str, todo_id: int) -> bool:
        """Mark a todo as completed."""
        if user_id not in self.todos:
            return False
        
        for todo in self.todos[user_id]:
            if todo["id"] == todo_id:
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
    
    def clear_completed(self, user_id: str) -> int:
        """Clear all completed todos."""
        if user_id not in self.todos:
            return 0
        
        completed_count = sum(1 for todo in self.todos[user_id] if todo["completed"])
        self.todos[user_id] = [todo for todo in self.todos[user_id] if not todo["completed"]]
        self.save_todos()
        return completed_count

# Initialize todo manager
todo_manager = TodoManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🎯 *Welcome to your Personal To-Do Bot!*

Here are the available commands:

📝 *Adding Tasks:*
• `/add <task>` - Add a new task
• `/todo <task>` - Quick add a task

📋 *Viewing Tasks:*
• `/list` - Show pending tasks
• `/all` - Show all tasks (including completed)
• `/completed` - Show only completed tasks

✅ *Managing Tasks:*
• `/complete <id>` - Mark task as completed
• `/delete <id>` - Delete a task
• `/clear` - Clear all completed tasks

ℹ️ *Help:*
• `/help` - Show this help message

*Examples:*
• `/add Buy groceries`
• `/complete 1`
• `/delete 2`
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help information."""
    await start(update, context)

async def add_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new todo item."""
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a task description.\nExample: `/add Buy groceries`")
        return
    
    task = " ".join(context.args)
    todo_id = todo_manager.add_todo(user_id, task)
    
    await update.message.reply_text(f"✅ Task added successfully!\n📝 Task #{todo_id}: {task}")

async def list_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List pending todos."""
    user_id = str(update.effective_user.id)
    todos = todo_manager.get_todos(user_id, show_completed=False)
    
    if not todos:
        await update.message.reply_text("📝 No pending tasks! Great job! 🎉")
        return
    
    message = "📋 *Your Pending Tasks:*\n\n"
    for todo in todos:
        status = "✅" if todo["completed"] else "⏳"
        message += f"{status} *{todo['id']}.* {todo['task']}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def list_all_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all todos including completed ones."""
    user_id = str(update.effective_user.id)
    todos = todo_manager.get_todos(user_id, show_completed=True)
    
    if not todos:
        await update.message.reply_text("📝 No tasks found! Add some with `/add <task>`")
        return
    
    pending = [todo for todo in todos if not todo["completed"]]
    completed = [todo for todo in todos if todo["completed"]]
    
    message = "📋 *All Tasks:*\n\n"
    
    if pending:
        message += "⏳ *Pending:*\n"
        for todo in pending:
            message += f"• *{todo['id']}.* {todo['task']}\n"
        message += "\n"
    
    if completed:
        message += "✅ *Completed:*\n"
        for todo in completed:
            message += f"• *{todo['id']}.* {todo['task']}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def complete_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark a todo as completed."""
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a task ID.\nExample: `/complete 1`")
        return
    
    try:
        todo_id = int(context.args[0])
        if todo_manager.complete_todo(user_id, todo_id):
            await update.message.reply_text(f"✅ Task #{todo_id} marked as completed! 🎉")
        else:
            await update.message.reply_text(f"❌ Task #{todo_id} not found.")
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid task ID (number).")

async def delete_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a todo item."""
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a task ID.\nExample: `/delete 1`")
        return
    
    try:
        todo_id = int(context.args[0])
        if todo_manager.delete_todo(user_id, todo_id):
            await update.message.reply_text(f"🗑️ Task #{todo_id} deleted successfully!")
        else:
            await update.message.reply_text(f"❌ Task #{todo_id} not found.")
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid task ID (number).")

async def clear_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all completed todos."""
    user_id = str(update.effective_user.id)
    cleared_count = todo_manager.clear_completed(user_id)
    
    if cleared_count > 0:
        await update.message.reply_text(f"🧹 Cleared {cleared_count} completed task(s)!")
    else:
        await update.message.reply_text("📝 No completed tasks to clear.")

async def todo_quick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick add todo (alias for /add)."""
    await add_todo(update, context)

def main():
    """Start the bot."""
    # Get bot token from environment variable
    bot_token ="7784108003:AAFys4pF-XpXn1CgkUVVwsAIGIRYBfwsRYg"
    if not bot_token:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set your bot token: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # Log startup information
    logger.info("🤖 Starting Telegram To-Do Bot...")
    logger.info(f"📁 Data directory: {os.getenv('DATA_DIR', '.')}")
    logger.info(f"💾 Data file: {todo_manager.filename}")
    
    try:
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("add", add_todo))
        application.add_handler(CommandHandler("todo", todo_quick))
        application.add_handler(CommandHandler("list", list_todos))
        application.add_handler(CommandHandler("all", list_all_todos))
        application.add_handler(CommandHandler("completed", list_all_todos))
        application.add_handler(CommandHandler("complete", complete_todo))
        application.add_handler(CommandHandler("delete", delete_todo))
        application.add_handler(CommandHandler("clear", clear_completed))
        
        # Start the bot
        logger.info("🚀 Bot is ready and polling for messages...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
