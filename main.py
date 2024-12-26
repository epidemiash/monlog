from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import initialize_config, load_config, save_config, set_channel, last_error_notification, CONFIG_PATH
from getmet import get_server_metrics, get_server_audit
from checklogs import scheduled_check_logs
from monitor import add_monitor, remove_monitor, edit_monitor, show_monitors, start_monitor, stop_monitor, check_logs, show_monitor_details, toggle_monitor_status, delete_monitor, edit_monitor_prompt


# обрабатываем старт, делаем сверку на админа
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    config = load_config()
    allowed_user_id = config.get('allowed_user_id')

    if user_id != allowed_user_id:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота!")
        return

    await show_main_menu(update)

# показываем меню с условием
async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("\ud83e\ude84 Добавить монитор", callback_data='add_monitor')],
        [InlineKeyboardButton("\ud83d\udda5 Мои мониторы", callback_data='show_monitors')],
        [InlineKeyboardButton("\u2699\ufe0f Показать команды", callback_data='show_commands')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🚀 Основное меню\n\n Ты можешь добавить новый монитор, посмотреть текущие (включая их статус), а так же посмотреть дополнительные команды.", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "🙋‍♂️Приветствую! \n\nДанный бот позволит тебе добавлять мониторинг лога на твоих серверах или нодах. \n\nЧтобы начать нажми 'Добавить монитор'.\n",
            reply_markup=reply_markup,
        )

# обработчик для кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    if callback_data == 'add_monitor':
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❕Чтобы добавить монитор, отправь мне команду /add_mon со своими параметрами:\n\n"
            "/add_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последний строк для мониторинга> <ключевые слова (через запятую)> <исключения (через запятую)>",
            reply_markup=reply_markup,
        )
    elif callback_data == 'show_monitors':
        await show_monitors(update, context)
    elif callback_data.startswith('monitor:'):
        monitor_name = callback_data.split(':')[1]
        await show_monitor_details(update, context, monitor_name)
    elif callback_data.startswith('toggle:'):
        monitor_name = callback_data.split(':')[1]
        await toggle_monitor_status(update, context, monitor_name)
    elif callback_data.startswith('/edit_mon'):  # Обработка кнопки "Изменить"
        monitor_name = query.message.reply_markup.inline_keyboard[0][0].callback_data.split(':')[1]
        config = load_config()
        monitor = config.get('servers', {}).get(monitor_name)

        if not monitor:
            await query.message.reply_text(f"❌ Монитор '{monitor_name}' не найден.")
            return

        # Формируем команду для редактирования
        messcommand = (
            f"Скопируйте текущую команду, измените ее и отправьте мне:\n\n"
            f"/edit_mon {monitor_name} {monitor['host']} {monitor['login']} {monitor['password']} "
            f"{monitor['log_path']} {monitor['lines_to_tail']} {','.join(monitor['keywords'])} "
            f"{','.join(monitor['exclusions'])}"
        )

        await query.message.reply_text(messcommand)
    elif callback_data.startswith('delete:'):
        monitor_name = callback_data.split(':')[1]
        config = load_config()
        monitor = config.get('servers', {}).get(monitor_name)

        if not monitor:
            await query.message.reply_text(f"❌ Монитор '{monitor_name}' не найден.")
            return

        # Удаляем монитор
        del config['servers'][monitor_name]
        save_config(config)

        # Отправляем сообщение о завершении удаления
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к списку мониторов", callback_data='show_monitors')],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(f"✅ Монитор '{monitor_name}' успешно удалён.", reply_markup=reply_markup)
    elif callback_data.startswith("/getm"):
        server_name = callback_data.split(" ")[1]  
        await get_server_metrics(update, context) 
    elif callback_data.startswith("/audit"):
        server_name = callback_data.split(" ")[1] 
        await get_server_audit(update, context)  
    elif callback_data == 'show_commands':
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚙️ Основные команды:\n\n"
            "/add_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последний строк> <ключевые слова (через запятую)> <исключения (через запятую)>\n"
            "/rem_mon <название>\n"
            "/edit_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последний строк> <ключевые слова (через запятую)>\n"
            "/set_channel <id канала> - Указать канал для уведомлений\n"
            "/start_mon <название> - запуск монитора\n"
            "/stop_mon <название> - остановка монитора\n\n"
            "🛠 Дополнительные команды:\n\n"
            "/check_logs - Проверить логи для всех мониторов моментально\n"
            "/audit - Провести аудит сервера\n"
            "/getm <название> - Проверить метрики сервера\n",
            reply_markup=reply_markup,
        )
    elif callback_data == 'main_menu':
        await show_main_menu(update)






# показываем доступные команды
async def show_commands(update: Update):
    
    commands = (
        "/add_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последних строк> <ключевые слова (через запятую)>\n"
        "/rem_mon <название>\n"
        "/edit_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последних строк> <ключевые слова (через запятую)>\n"
        "/set_channel <id канала> - Указать канал для уведомлений\n"
        "/check_logs - Проверить логи для всех мониторов\n"
        "/audit <название> - Провести аудит сервера\n"
        "/getm <название> - Проверить метрики сервера\n"
    )
    await update.message.reply_text(commands)



def main():
    initialize_config()
    config = load_config()
    token = config['telegram_token']
    check_logs_interval = config.get('check_logs_interval', 300)  

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_mon", add_monitor))
    application.add_handler(CommandHandler("rem_mon", remove_monitor))
    application.add_handler(CommandHandler("edit_mon", edit_monitor))
    application.add_handler(CommandHandler("show", show_monitors))
    application.add_handler(CommandHandler("set_channel", set_channel))
    application.add_handler(CommandHandler("check_logs", check_logs))
    application.add_handler(CommandHandler("getm", get_server_metrics))
    application.add_handler(CommandHandler("audit", get_server_audit))
    application.add_handler(CommandHandler("start_mon", start_monitor))
    application.add_handler(CommandHandler("stop_mon", stop_monitor))
    application.add_handler(CallbackQueryHandler(button))
    

    job_queue = application.job_queue
    job_queue.run_repeating(scheduled_check_logs, interval=check_logs_interval, first=0) 

    application.run_polling()

if __name__ == '__main__':
    main()