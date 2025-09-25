"""
Configuration file for the Telegram To-Do Bot
"""

import os

# Bot configuration
BOT_TOKEN = os.getenv('7784108003:AAFys4pF-XpXn1CgkUVVwsAIGIRYBfwsRYg')

# Data storage configuration
DATA_FILE = "todos.json"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Bot settings
MAX_TASK_LENGTH = 500  # Maximum characters for a task description
MAX_TASKS_PER_USER = 100  # Maximum tasks per user
