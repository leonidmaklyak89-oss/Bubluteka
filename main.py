import os
import flask
from telebot import TeleBot, types

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

# ✅ Ваш актуальный Telegram ID жестко вшит в систему безопасности
ADMIN_ID = 7496178917  

bot = TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

# Переменные в памяти (сбрасываются при перезапуске сервера Render)
prices = {
    "scripts": 450,
    "bots": 1500,
    "parsers": 2000
}

# Динамический юзернейм админа поддержки (по умолчанию твой)
settings = {
    "support_admin": "@TEAMONSTORS"
}

# Состояния для изменений
user_states = {}

# Функция для создания главного меню с кнопками
def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_price = types.KeyboardButton("💰 Прайс-лист")
    btn_dev = types.KeyboardButton("💬 Написать разработчику")
    btn_support = types.KeyboardButton("👨‍💻 Поддержка")
    
    markup.row(btn_price, btn_dev)
    markup.row(btn_support)
    
    # Сверка ID: кнопка админки отобразится только на твоем устройстве
    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ Админ-панель")
        markup.row(btn_admin)
        
    return markup

# Меню админки с новой кнопкой смены юзернейма
def get_admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_edit_scripts = types.InlineKeyboardButton("Редактировать 'Скрипты'", callback_data="edit_scripts")
    btn_edit_bots = types.InlineKeyboardButton("Редактировать 'Боты'", callback_data="edit_bots")
    btn_edit_parsers = types.InlineKeyboardButton("Редактировать 'Парсеры'", callback_data="edit_parsers")
    btn_edit_admin = types.InlineKeyboardButton("👤 Изменить админа поддержки", callback_data="edit_support_admin")
    markup.add(btn_edit_scripts)
    markup.add(btn_edit_bots)
    markup.add(btn_edit_parsers)
    markup.add(btn_edit_admin) # Добавили кнопку в меню
    return markup

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def command_start(message):
    welcome_text = (
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
        f"Добро пожаловать в бот по заказу IT-кодов.\n"
        f"Используй меню ниже, чтобы узнать цены, связаться со мной или обратиться в поддержку!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode="HTML")

# Обработка текстовых сообщений и кнопок меню
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    # Проверяем, находится ли админ в процессе изменения данных
    if user_id == ADMIN_ID and user_id in user_states:
        state = user_states[user_id]
        
        # Если меняем юзернейм админа поддержки
        if state == "support_admin":
            new_username = message.text.strip()
            # Автоматически добавляем @, если пользователь забыл его ввести
            if not new_username.startswith("@"):
                new_username = "@" + new_username
                
            settings["support_admin"] = new_username
            del user_states[user_id]
            bot.send_message(user_id, f"✅ Юзернейм админа поддержки изменен на <b>{new_username}</b>!", reply_markup=get_main_keyboard(user_id), parse_mode="HTML")
            return
            
        # Если меняем цены
        else:
            if message.text.isdigit():
                prices[state] = int(message.text)
                del user_states[user_id]
                bot.send_message(user_id, f"✅ Цена успешно изменена!", reply_markup=get_main_keyboard(user_id))
            else:
                bot.send_message(user_id, "❌ Пожалуйста, введите только число (например: 500).")
            return

    # Стандартная логика кнопок
    if message.text == "💰 Прайс-лист":
        price_text = (
            "💰 <b>Ориентировочная цена работы:</b>\n"
            f"• Простые скрипты: от {prices['scripts']} руб.\n"
            f"• Telegram-боты: от {prices['bots']} руб.\n"
            f"• Парсеры и автоматизация: от {prices['parsers']} руб.\n\n"
            "⚠️ <b>Внимание:</b> итоговая стоимость может измениться в зависимости "
            "от ваших личных предпочтений, сложности и деталей задания."
        )
        bot.send_message(message.chat.id, price_text, parse_mode="HTML")
        
    elif message.text == "💬 Написать разработчику":
        dev_text = (
            "👨‍💻 Для обсуждения деталей, ТЗ и оплаты напишите мне напрямую:\n"
            "👉 @TEAMONSTORS\n\n"
            "Жду ваших идей!"
        )
        bot.send_message(message.chat.id, dev_text)

    elif message.text == "👨‍💻 Поддержка":
        # 📌 Теперь юзернейм берется динамически из переменной settings["support_admin"]
        support_text = (
            "📌 <b>Информация по тех. поддержке:</b>\n\n"
            f"👉 {settings['support_admin']} — <b>Администратор</b>. Все вопросы по нерабочим кодам и техническим проблемам направляйте ему.\n"
            "Отвечает в течение 1 дня точно.\n\n"
            "⚠️ Если администратор не отвечает больше 1 дня, пишите <b>владельцу</b>, он точно разберется и ответит!"
        )
        bot.send_message(message.chat.id, support_text, parse_mode="HTML")
        
    elif message.text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        bot.send_message(
            user_id, 
            f"⚙️ <b>Панель управления ботом</b>\n\n"
            f"Текущие цены:\n"
            f"• Скрипты: {prices['scripts']} руб.\n"
            f"• Боты: {prices['bots']} руб.\n"
            f"• Парсеры: {prices['parsers']} руб.\n\n"
            f"Текущий админ поддержки: {settings['support_admin']}\n\n"
            f"Выберите действие:", 
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        
    else:
        bot.send_message(
            message.chat.id, 
            "Пожалуйста, используйте кнопки в меню ниже 👇", 
            reply_markup=get_main_keyboard(user_id)
        )

# Обработка нажатий на инлайн-кнопки в админке
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.from_user.id != ADMIN_ID:
        return
        
    if call.data == "edit_scripts":
        user_states[ADMIN_ID] = "scripts"
        bot.send_message(ADMIN_ID, "Введите новую минимальную цену для <b>Простых скриптов</b> (только число):", parse_mode="HTML")
    elif call.data == "edit_bots":
        user_states[ADMIN_ID] = "bots"
        bot.send_message(ADMIN_ID, "Введите новую минимальную цену для <b>Telegram-ботов</b> (только число):", parse_mode="HTML")
    elif call.data == "edit_parsers":
        user_states[ADMIN_ID] = "parsers"
        bot.send_message(ADMIN_ID, "Введите новую минимальную цену для <b>Парсеров</b> (только число):", parse_mode="HTML")
    elif call.data == "edit_support_admin":
        user_states[ADMIN_ID] = "support_admin"
        bot.send_message(ADMIN_ID, "Отправьте новый юзернейм для тех. поддержки (например: <code>@new_admin_username</code>):", parse_mode="HTML")
        
    bot.answer_callback_query(call.id)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
