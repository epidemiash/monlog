#!/bin/bash

# Проверка, что скрипт запущен от имени root
if [ "$EUID" -ne 0 ]; then
  echo "Скрипт установки должен быть запущен под пользователем root. Выход.."
  exit 1
fi

show() {
    echo -e "\033[33m$1\033[0m"
}

show "#################################################"
show "#            Monitoring of node logs            #"
show "#               by XVVCVCNC                     #"
show "#################################################"

# Задержка 3 секунды
sleep 3

# Обновление пакетов
show "Проверяем и ставим обновления ОС.."
sudo apt update -y && sudo apt upgrade -y

show "Устанавливаю Python/PIP"
sudo apt install -y python3 python3-pip

show "Устанавливаем виртуальное окружение"
python3 -m venv /root/monlog/venv

show "Активируем виртуальное окружение и устанавливаем зависимости"
source /root/monlog/venv/bin/activate
pip install --upgrade pip
pip install -r /root/monlog/requirements.txt
show "Проверяем обновления..."
pip install python-telegram-bot[job-queue]
pip install --upgrade paramiko
pip install --upgrade psutil
pip install --upgrade python-telegram-bot

show "Создаем системный сервис для бота"
sudo bash -c 'cat > /etc/systemd/system/telegram_monitor_bot.service <<EOF
[Unit]
Description=Telegram Monitoring Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/monlog
ExecStart=/root/monlog/venv/bin/python /root/monlog/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'

show "Перезагружаем конфигурацию systemd"
sudo systemctl daemon-reload

show "Включаем и запускаем службу"
sudo systemctl enable telegram_monitor_bot.service
sudo systemctl start telegram_monitor_bot.service
 
show "Проверяем статус службы"
systemctl status telegram_monitor_bot.service
