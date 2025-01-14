# MonLog Bot

MonLog Bot — это инструмент для мониторинга логов серверов и отправки уведомлений через Telegram. 

Вид и управление ботом:

<img src="https://anticod.ru/github/monlog1.jpg" alt="Вид в боте">
<img src="https://anticod.ru/github/monlog2.jpg" alt="Вид в боте">
<img src="https://anticod.ru/github/monlog3.jpg" alt="Вид в боте">
<img src="https://anticod.ru/github/monlog4.jpg" alt="Вид в боте">
<img src="https://anticod.ru/github/monlog5.jpg" alt="Вид в боте">
<img src="https://anticod.ru/github/monlog6.jpg" alt="Вид в боте">

Уведомления в канал:

<img src="https://anticod.ru/github/monlog7.jpg" alt="Уведомления">


## 🚀 Установка

1. **Авторизуйтесь на своем сервере под root:**
    ```bash
    su - root
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

- Токен бота берем у @BotFather
- Пересылаем сообщение из канала для будующих уведомлений боту @myidbot
- Получаем свой ID пользователя у бота @getmyid_bot

Файл `servers_config.json` должен быть отредактирован следующим образом:
```json
{
    "telegram_token": "ваш_токен",
    "telegram_channel": "-1001234567890",
    "allowed_user_id": 123456789,
    "check_logs_interval": 300,
    "servers": {}
}

