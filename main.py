import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Включаем логирование, чтобы видеть ошибки в панели Render
logging.basicConfig(level=logging.INFO)

# Получаем настройки из скрытых переменных хостинга
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL") 
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Ответ на команду /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Этот бот создан для заработка и успешно работает на Render! 🚀"
    )

# Эхо-режим: бот повторяет текст (для проверки работоспособности)
@dp.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer(f" Код проверен. Получено сообщение: {message.text}")

# Настройка вебхука при запуске
async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=WEBHOOK_URL)

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    setup_application(app, dp, bot=bot)
    
    # Render автоматически передает нужный порт в переменную PORT
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
