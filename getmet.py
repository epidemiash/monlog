import paramiko
from config import initialize_config, load_config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# сбор метрик с сервера
async def get_server_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Определяем, имя сервера пришло из команды или кнопки
    server_name = None
    if update.callback_query:  # Если вызов из кнопки
        server_name = update.callback_query.data.split(" ")[1]
    elif len(context.args) >= 1:  # Если вызов из команды
        server_name = context.args[0]
    
    if not server_name:
        await update.message.reply_text("Пожалуйста, укажите имя сервера. Использование: /getm <имя сервера>")
        return

    # Загружаем конфигурацию
    config = load_config()
    server = config.get('servers', {}).get(server_name)

    if not server:
        await update.message.reply_text(f"Сервер с именем '{server_name}' не найден в конфигурации.")
        return

    host = server['host']
    username = server['login']
    password = server['password']

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)

        # Команды для получения метрик
        commands = {
            "cpu": "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",  # CPU загрузка
            "mem": "free -m | awk '/Mem:/ {print $3 \"MB из \" $2 \"MB\"}'",  # Память
            "disk": "df -h / | awk 'NR==2 {print $4}'"  # Свободное место на /
        }

        results = {}
        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            results[key] = stdout.read().decode().strip()

        metrics_report = (
            f"Метрики для сервера **{server_name} ({host})**:\n"
            f"💡 CPU: {results.get('cpu', 'N/A')}%\n"
            f"💡 Память: {results.get('mem', 'N/A')}\n"
            f"💡 Свободное место на диске: {results.get('disk', 'N/A')}\n"
        )
        ssh_client.close()

    except Exception as e:
        metrics_report = f"❌ Ошибка при сборе метрик с сервера '{server_name}': {e}"

    # Отправляем сообщение
    if update.callback_query:
        await update.callback_query.message.reply_text(metrics_report)
    else:
        await update.message.reply_text(metrics_report)





# Функция для аудита сервера
async def get_server_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Определяем имя сервера из кнопки или команды
    server_name = None
    if update.callback_query:  # Если вызов из кнопки
        server_name = update.callback_query.data.split(" ")[1]
    elif len(context.args) >= 1:  # Если вызов из команды
        server_name = context.args[0]
    
    if not server_name:
        await update.message.reply_text("Пожалуйста, укажите имя сервера. Использование: /audit <имя сервера>")
        return

    # Загружаем конфигурацию
    config = load_config()
    server = config.get('servers', {}).get(server_name)

    if not server:
        await update.message.reply_text(f"Сервер с именем '{server_name}' не найден в конфигурации.")
        return

    host = server['host']
    username = server['login']
    password = server['password']

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)

        # Команды для получения информации
        commands = {
            "hostname": "hostname",
            "os": "cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2",
            "uptime": "uptime -p",
            "uptime_since": "uptime -s",
            "cpu_model": "lscpu | grep 'Model name' | cut -d':' -f2 | xargs",
            "cpu_cores": "nproc",
            "total_mem": "free -h | awk '/^Mem:/ {print $2}'",
            "total_disk": "df -h / | awk 'NR==2 {print $2}'",
            "public_ip": "curl -s https://api.ipify.org",
            "load_average": "uptime | awk -F'load average:' '{print $2}' | xargs",
            "reboot_required": "[ -f /var/run/reboot-required ] && echo 'YES' || echo 'NO'",
            "ssh_root_login": "grep '^PermitRootLogin' /etc/ssh/sshd_config | awk '{print $2}'",
            "firewall_status": "ufw status | grep 'Status:' | awk '{print $2}'",
            "failed_logins": "grep 'Failed password' /var/log/auth.log 2>/dev/null | wc -l",
            "unattended_upgrades": "dpkg -l | grep unattended-upgrades | wc -l",
            "password_policy": "grep 'minlen' /etc/security/pwquality.conf 2>/dev/null | awk '{print $3}'",
            "suid_files": "find / -type f -perm -4000 2>/dev/null | wc -l",
            "system_updates": "apt-get -s upgrade | grep -P '^ upgraded' | awk '{print $1}'",
            "ssh_port": "grep '^Port' /etc/ssh/sshd_config | awk '{print $2}' || echo 22",
            "intrusion_prevention": "systemctl is-active fail2ban || systemctl is-active crowdsec || echo 'inactive'"
        }

        results = {}
        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            result = stdout.read().decode().strip()
            results[key] = result if result else "-"

        # Форматирование результатов аудита
        audit_report = (
            f"Аудит сервера {server_name} ({host}):\n\n"
            f"🖥️ Хостнейм: {results.get('hostname', '-')}\n"
            f"💻 Операционная система: {results.get('os', '-')}\n"
            f"⏳ Аптайм: {results.get('uptime', '-')} (с {results.get('uptime_since', '-')})\n"
            f"⚙️ Модель CPU: {results.get('cpu_model', '-')}\n"
            f"🧵 Количество ядер: {results.get('cpu_cores', '-')}\n"
            f"🗄️ Общая память: {results.get('total_mem', '-')}\n"
            f"💾 Общий объём диска: {results.get('total_disk', '-')}\n"
            f"🌐 Публичный IP: {results.get('public_ip', '-')}\n"
            f"📊 Средняя нагрузка: {results.get('load_average', '-')}\n\n"
            f"🔄 Требуется перезагрузка: {results.get('reboot_required', '-')}\n"
            f"🔐 Root доступ по SSH: {results.get('ssh_root_login', '-')}\n"
            f"🛡️ Статус брандмауэра: {results.get('firewall_status', '-')}\n"
            f"⚠️ Неудачные попытки входа: {results.get('failed_logins', '-')}\n"
            f"🔄 Автообновления: {'Включены' if results.get('unattended_upgrades', '0') != '0' else 'Отключены'}\n"
            f"🔑 Политика паролей (minlen): {results.get('password_policy', '-')}\n"
            f"🔍 Найдено SUID файлов: {results.get('suid_files', '-')}\n"
            f"🔧 Доступные системные обновления: {results.get('system_updates', '-')}\n"
            f"🚪 Порт SSH: {results.get('ssh_port', '-')}\n"
            f"🛡️ Система предотвращения вторжений (Fail2ban,CrowdSec and others): {results.get('intrusion_prevention', '-')}\n"
        )

        ssh_client.close()

    except Exception as e:
        audit_report = f"❌ Ошибка при выполнении аудита сервера '{server_name}': {e}"

    # Отправляем сообщение
    if update.callback_query:
        await update.callback_query.message.reply_text(audit_report)
    else:
        await update.message.reply_text(audit_report)

