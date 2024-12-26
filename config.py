import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

CONFIG_PATH = 'servers_config.json'

# храним время последних уведомлений (чтобы не было дублирований)
last_error_notification = {}

# для чтения конфига
def load_config():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)

# запись в конфиг
def save_config(config):
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file, indent=2)

# создаем если нет конфига
def initialize_config():
    if not os.path.exists(CONFIG_PATH):
        config = {
            "telegram_token": "",
            "telegram_channel": "",
            "servers": {}
        }
        save_config(config)

# Функции для загрузки и сохранения конфигурации
def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'servers': {}}

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)

# задаем канал уведомлений
async def set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Использование: /set_channel <id канала>")
        return
    channel_id = args[0]
    config = load_config()
    config['telegram_channel'] = channel_id
    save_config(config)
    await update.message.reply_text(f"Канал установлен: {channel_id}")
