import os
import flask
from telebot import TeleBot, types

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = TeleBot(TOKEN, threaded=False)
app = flask.Flask(__name__)

@bot.message_handler(commands=['start'])
def command_start(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}!\nБот на telebot успешно работает на Render! 🚀")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Код проверен. Получено: {message.text}")

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
