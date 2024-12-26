# MonLog Bot

MonLog Bot — это инструмент для мониторинга логов серверов и отправки уведомлений через Telegram. 

## 🚀 Установка

1. **Создайте каталог для проекта:**
    ```bash
    mkdir monlog
    cd monlog
    ```

2. **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/epidemiash/monlog.git .
    ```

3. **Выдайте права на выполнение скриптов:**
    ```bash
    chmod +x *.sh
    ```

4. **Настройте конфигурацию:**
    Отредактируйте файл `servers_config.json`:
    ```bash
    nano servers_config.json
    ```
    - Укажите токен Telegram-бота.
    - Задайте ID чата для уведомлений.
    - Введите свой пользовательский ID.

5. **Установите зависимости:**
    ```bash
    ./install.sh
    ```

6. **Запустите бота:**
    Отправьте боту команду:
    ```
    /start
    ```

## ⚙️ Настройка конфигурации

Файл `servers_config.json` должен быть отредактирован следующим образом:
```json
{
    "telegram_token": "ваш_токен",
    "telegram_channel": "-1001234567890",
    "allowed_user_id": 123456789,
    "check_logs_interval": 300,
    "servers": {}
}