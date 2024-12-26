import paramiko
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import initialize_config, load_config, save_config, set_channel, last_error_notification, CONFIG_PATH

# проходим по каждому монитору и чекаем указанный лог
async def check_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    channel_id = config.get('telegram_channel')
    monitors = config.get('servers', {})

    if not channel_id:
        if update:
            await update.message.reply_text("Канал для уведомлений не установлен. Используйте /set_channel для установки.")
        return

    for name, server in monitors.items():
        if server.get('status') != 'on':  # Проверяем, включен ли монитор
            continue

        host = server['host']
        username = server['login']
        password = server['password']
        log_path = server['log_path']
        keywords = [kw.lower() for kw in server['keywords']]  # Нечувствительность к регистру
        exclusions = [ex.lower() for ex in server.get('exclusions', [])]  # Исключения
        lines_to_tail = server.get('lines_to_tail', 50)

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(host, username=username, password=password)

            command = f"tail -n {lines_to_tail} {log_path}"
            stdin, stdout, stderr = ssh_client.exec_command(command)

            logs = stdout.readlines()

            last_error_notification.setdefault(name, {})

            for line in logs:
                lower_line = line.lower()
                if any(keyword in lower_line for keyword in keywords) and not any(exc in lower_line for exc in exclusions):
                    now = datetime.now()
                    matched_keywords = [kw for kw in keywords if kw in lower_line]

                    for keyword in matched_keywords:
                        last_notification = last_error_notification[name].get(keyword)

                        if not last_notification or (now - last_notification).total_seconds() >= 300:
                            # Формируем количество знаков "!" в зависимости от типа события
                            if "error" in keyword:
                                prefix = "⛔️ ERROR"
                            elif "crit" in keyword:
                                prefix = "❌ CRIT"
                            elif "warn" in keyword:
                                prefix = "⚠️ WARN"
                            elif "info" in keyword:
                                prefix = "ℹ️ INFO"
                            else:
                                prefix = ""

                            message = f"{prefix} на {name}: {line.strip()}"
                            await context.bot.send_message(chat_id=channel_id, text=message)

                            last_error_notification[name][keyword] = now

            ssh_client.close()

        except Exception as e:
            error_message = f"📍 Упс, похоже сервер {name} недоступен: {str(e)}"
            try:
                await context.bot.send_message(chat_id=channel_id, text=error_message)
            except Exception as send_error:
                print(f"Ошибка при отправке сообщения: {send_error}")

# переодически вызываем check_logs
async def scheduled_check_logs(context: ContextTypes.DEFAULT_TYPE):
    await check_logs(None, context)