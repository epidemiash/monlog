#!/bin/bash

# Остановка и удаление службы
echo "Удаление службы telegram_monitor_bot.service..."
sudo systemctl stop telegram_monitor_bot.service
sudo systemctl disable telegram_monitor_bot.service
sudo rm /etc/systemd/system/telegram_monitor_bot.service

# Перезагрузка демона systemd
sudo systemctl daemon-reload

# Удаление всех файлов, связанных с ботом
echo "Удаление файлов бота..."
rm -rf ~/monlog

# Удаление виртуального окружения, если оно есть
if [ -d "/root/monlog/venv" ]; then
    echo "Удаление виртуального окружения..."
    rm -rf /root/monlog/venv
fi

echo "Скрипт завершен. Все файлы и службы удалены."
