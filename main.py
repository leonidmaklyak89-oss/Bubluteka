import os
import flask
from telebot import TeleBot, types

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

# Функция для создания главного меню с кнопками
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_price = types.KeyboardButton("💰 Прайс-лист")
    btn_dev = types.KeyboardButton("💬 Написать разработчику")
    markup.add(btn_price, btn_dev)
    return markup

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def command_start(message):
    welcome_text = (
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
        f"Добро пожаловать в бот по заказу IT-кодов.\n"
        f"Используй меню ниже, чтобы узнать цены или связаться со мной!"
    )
    # Используем HTML-разметку для жирного шрифта в имени
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# Обработка текстовых кнопок
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "💰 Прайс-лист":
        price_text = (
            "💰 <b>Ориентировочная цена работы:</b>\n"
            "• Простые скрипты: от 450 руб.\n"
            "• Telegram-боты: от 1500 руб.\n"
            "• Парсеры и автоматизация: от 2000 руб.\n\n"
            "⚠️ <b>Внимание:</b> итоговая стоимость может измениться в зависимости "
            "от ваших личных предпочтений, сложности и деталей задания."
        )
        # Переключено на HTML, теперь теги <b> работают без багов со спецсимволами
        bot.send_message(message.chat.id, price_text, parse_mode="HTML")
        
    elif message.text == "💬 Написать разработчику":
        dev_text = (
            "👨‍💻 Для обсуждения деталей, ТЗ и оплаты напишите мне напрямую:\n"
            "👉 @TEAMONSTORS\n\n"
            "Жду ваших идей!"
        )
        bot.send_message(message.chat.id, dev_text)
        
    else:
        bot.send_message(
            message.chat.id, 
            "Пожалуйста, используйте кнопки в меню ниже 👇", 
            reply_markup=get_main_keyboard()
        )

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
    # Сначала удаляем старый вебхук перед установкой нового
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
    
