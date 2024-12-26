import paramiko
from datetime import datetime, timedelta
from config import initialize_config, load_config, save_config, last_error_notification, CONFIG_PATH
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes



# добавление нового монитора
# добавление нового монитора
async def add_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 7:  # Минимальное количество обязательных аргументов
            await update.message.reply_text(
                "Неправильное использование. Использование: /add_mon <название> <хост> <логин> <пароль> <путь к логу> <кол-во последний строк> <ключевые слова (через запятую)> <исключения (через запятую)>"
            )
            return

        # Извлекаем обязательные аргументы
        name, host, login, password, log_path, lines_to_tail, keywords = args[:7]

        # Объединяем оставшиеся аргументы как строку исключений
        exclusions = ' '.join(args[7:])  # Все оставшиеся аргументы объединяются в одну строку

        # Преобразование и проверки
        lines_to_tail = int(lines_to_tail)
        keywords = keywords.split(',')
        exclusions = exclusions.split(',')

        # Сохраняем конфигурацию
        config = load_config()
        config['servers'][name] = {
            'host': host,
            'login': login,
            'password': password,
            'log_path': log_path,
            'lines_to_tail': lines_to_tail,
            'keywords': keywords,
            'exclusions': exclusions,
            'status': 'on'
        }

        save_config(config)

        # Кнопки управления
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к списку мониторов", callback_data='show_monitors')],
            [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"✅ Монитор '{name}' успешно добавлен.", reply_markup=reply_markup)
    except ValueError:
        await update.message.reply_text("Ошибка: параметр <кол-во последний строк> должен быть числом.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")




# удаление монитора
async def remove_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text(
                "Неправильное использование. Использование: /rem_mon <название>"
            )
            return

        name = args[0]

        config = load_config()
        if name in config['servers']:
            del config['servers'][name]
            save_config(config)

            # Кнопки управления
            keyboard = [
                [InlineKeyboardButton("🔙 Вернуться к списку мониторов", callback_data='show_monitors')],
                [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(f"✅ Монитор '{name}' успешно удалён.", reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"❌ Монитор '{name}' не найден.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")


async def delete_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE, monitor_name: str):
    config = load_config()
    if monitor_name in config['servers']:
        del config['servers'][monitor_name]
        save_config(config)

        # Кнопки управления
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к списку мониторов", callback_data='show_monitors')],
            [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            f"✅ Монитор '{monitor_name}' был успешно удалён.",
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(f"❌ Монитор '{monitor_name}' не найден.")



# редактирование монитора
# редактирование монитора
async def edit_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 7:
            await update.message.reply_text(
                "❌ Неправильное использование. Использование:\n\n"
                "/edit_mon <название> <хост> <логин> <пароль> <путь к логу> "
                "<кол-во последних строк> <ключевые слова (через запятую)> [исключения (через запятую)]"
            )
            return

        name, host, login, password, log_path, lines_to_tail, *keywords_and_exclusions = args
        lines_to_tail = int(lines_to_tail)

        # Разделяем ключевые слова и исключения
        if "|" in ' '.join(keywords_and_exclusions):
            keywords_part, exclusions_part = ' '.join(keywords_and_exclusions).split("|", 1)
            keywords = keywords_part.split(',')
            exclusions = exclusions_part.split(',')
        else:
            keywords = ' '.join(keywords_and_exclusions).split(',')
            exclusions = []

        config = load_config()
        if name not in config['servers']:
            await update.message.reply_text(f"❌ Монитор '{name}' не найден.")
            return

        # Обновляем данные монитора
        config['servers'][name] = {
            'host': host,
            'login': login,
            'password': password,
            'log_path': log_path,
            'lines_to_tail': lines_to_tail,
            'keywords': keywords,
            'exclusions': exclusions  # Добавляем исключения
        }

        save_config(config)

        # Кнопки для навигации
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к мониторам", callback_data='show_monitors')],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Уведомление об успешном обновлении
        await update.message.reply_text(f"✅ Монитор '{name}' успешно обновлен!", reply_markup=reply_markup)

    except ValueError:
        await update.message.reply_text("❌ Ошибка: параметр <кол-во последних строк> должен быть числом.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")


async def edit_monitor_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, monitor_name: str):
    config = load_config()
    monitor = config.get('servers', {}).get(monitor_name)

    if not monitor:
        await update.callback_query.edit_message_text(f"❌ Монитор '{monitor_name}' не найден.")
        return

    # Формируем сообщение с текущими параметрами
    message = (
        f"✏️ Изменение монитора '{monitor_name}':\n\n"
        f"**Текущие параметры:**\n"
        f"- **IP/Хост:** {monitor['host']}\n"
        f"- **Путь к логу:** {monitor['log_path']}\n"
        f"- **Кол-во строк для мониторинга:** {monitor['lines_to_tail']}\n"
        f"- **Ключевые слова:** {', '.join(monitor['keywords'])}\n"
        f"- **Исключения:** {', '.join(monitor['exclusions'])}\n\n"
        f"Отправьте команду в формате:\n"
        f"`/edit_mon {monitor_name} <хост> <логин> <пароль> <путь к логу> <кол-во строк> <ключевые слова> [исключения]`",
    )

    await update.callback_query.edit_message_text(message, parse_mode='Markdown')



# показываем мониторы
# показываем мониторы
async def show_monitors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    monitors = config.get('servers', {})

    if monitors:
        keyboard = []
        for name, data in monitors.items():
            # Определяем статус монитора
            status = data.get('status', 'off')
            icon = '🔴' if status == 'off' else '🟢'  # Красный/зеленый индикатор

            # Создаем кнопку с названием монитора и статусом
            keyboard.append([InlineKeyboardButton(f"{icon} {name}", callback_data=f"monitor:{name}")])
        
        # Добавляем кнопку возврата в главное меню
        keyboard.append([InlineKeyboardButton("🔙 Вернуться в меню", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = "🖥️ Выберите монитор для управления:"
    else:
        message = "❌ У вас пока нет добавленных мониторов."
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем или обновляем сообщение
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)


# Детали монитора       
async def show_monitor_details(update: Update, context: ContextTypes.DEFAULT_TYPE, monitor_name: str):
    config = load_config()
    monitor = config.get('servers', {}).get(monitor_name)

    if not monitor:
        await update.callback_query.edit_message_text(f"❌ Монитор '{monitor_name}' не найден.")
        return

    # Формируем сообщение
    status = "🟢 Включен" if monitor.get('status') == 'on' else "🔴 Выключен"
    message = (
        f"📋 **Информация о мониторе**\n\n"
        f"**Название:** {monitor_name}\n"
        f"**Статус:** {status}\n"
        f"**IP/Хост:** {monitor['host']}\n"
        f"**Путь к логу:** {monitor['log_path']}\n"
        f"**Кол-во строк для мониторинга:** {monitor['lines_to_tail']}\n"
        f"**Ключевые слова:** {', '.join(monitor['keywords'])}\n"
        f"**Исключения:** {', '.join(monitor['exclusions'])}\n"
    )

    # Кнопки управления
    keyboard = [
    [InlineKeyboardButton("🛑 Остановить" if monitor.get('status') == 'on' else "▶️ Включить", callback_data=f"toggle:{monitor_name}")],
    [InlineKeyboardButton("✏️ Изменить", callback_data=f"/edit_mon {monitor_name}"),
     InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete:{monitor_name}")],
    [InlineKeyboardButton("📊 Показать нагрузку", callback_data=f"getm:{monitor_name}"),
     InlineKeyboardButton("🔍 Аудит", callback_data=f"audit:{monitor_name}")],
    [InlineKeyboardButton("🔙 Вернуться к списку", callback_data='show_monitors')]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')





async def toggle_monitor_status(update: Update, context: ContextTypes.DEFAULT_TYPE, monitor_name: str):
    config = load_config()
    monitor = config.get('servers', {}).get(monitor_name)

    # Проверка: существует ли монитор
    if not monitor:
        await update.callback_query.edit_message_text(f"❌ Монитор '{monitor_name}' не найден.")
        return

    # Изменяем статус монитора
    current_status = monitor.get('status', 'off')
    new_status = 'on' if current_status == 'off' else 'off'
    monitor['status'] = new_status
    save_config(config)  # Сохраняем изменения в конфиг

    # Уведомление пользователя о действии
    status_action = "включен" if new_status == 'on' else "выключен"
    await update.callback_query.answer(f"Монитор '{monitor_name}' {status_action}.")

    # Формируем обновленное сообщение
    status_text = "🟢 Включен" if new_status == 'on' else "🔴 Выключен"
    message = (
        f"📋 **Информация о мониторе**\n\n"
        f"**Название:** {monitor_name}\n"
        f"**Статус:** {status_text}\n"
        f"**IP/Хост:** {monitor['host']}\n"
        f"**Путь к логу:** {monitor['log_path']}\n"
        f"**Кол-во строк для мониторинга:** {monitor['lines_to_tail']}\n"
        f"**Ключевые слова:** {', '.join(monitor['keywords'])}\n"
        f"**Исключения:** {', '.join(monitor['exclusions'])}\n"
    )

    # Обновляем кнопки управления
    keyboard = [
        [InlineKeyboardButton("🛑 Остановить" if new_status == 'on' else "▶️ Включить", callback_data=f"toggle:{monitor_name}")],
        [InlineKeyboardButton("✏️ Изменить", callback_data=f"/edit_mon {monitor_name}")],
        [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete:{monitor_name}")],
        [InlineKeyboardButton("🔙 Вернуться к списку", callback_data='show_monitors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Обновляем сообщение
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')





# Обработчик для изменения статуса монитора
async def toggle_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    config = load_config()
    monitors = config.get('servers', {})

    if not query.data:
        return

    action, monitor_name = query.data.split(":")

    if monitor_name in monitors:
        if action == 'start':
            monitors[monitor_name]['status'] = 'on'
            await query.edit_message_text(f"\u041c\u043e\u043d\u0438\u0442\u043e\u0440 {monitor_name} \u0432\u043a\u043b\u044e\u0447\u0435\u043d.")
        elif action == 'stop':
            monitors[monitor_name]['status'] = 'off'
            await query.edit_message_text(f"\u041c\u043e\u043d\u0438\u0442\u043e\u0440 {monitor_name} \u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d.")

        save_config(config)  # Сохранение обновленного конфига

    # После изменения статуса, заново отображаем список мониторов
    await show_monitors(update, context)



# Включение монитора
async def start_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Пожалуйста, укажите имя монитора. Использование: /start_mon <название>")
        return

    monitor_name = context.args[0]
    config = load_config()

    if monitor_name not in config.get('servers', {}):
        await update.message.reply_text(f"Монитор с именем '{monitor_name}' не найден.")
        return

    # Изменяем статус на 'on'
    config['servers'][monitor_name]['status'] = 'on'
    save_config(config)
    await update.message.reply_text(f"Монитор '{monitor_name}' включен.")

# Отключение монитора
async def stop_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Пожалуйста, укажите имя монитора. Использование: /stop_mon <название>")
        return

    monitor_name = context.args[0]
    config = load_config()

    if monitor_name not in config.get('servers', {}):
        await update.message.reply_text(f"Монитор с именем '{monitor_name}' не найден.")
        return

    # Изменяем статус на 'off'
    config['servers'][monitor_name]['status'] = 'off'
    save_config(config)
    await update.message.reply_text(f"Монитор '{monitor_name}' отключен.")


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

