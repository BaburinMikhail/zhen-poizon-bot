
import logging
from aiogram import Bot, Dispatcher, types, executor
import requests
import os

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CATEGORY_DELIVERY = {
    "Обувь / Верхняя одежда": 1500,
    "Толстовки / Штаны": 1000,
    "Футболки / Шорты": 700,
    "Носки / Нижнее белье": 500,
    "Сумки": 1500
}

def get_cny_to_rub_rate():
    try:
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        rate = r.json()["Valute"]["CNY"]["Value"]
        return rate + 1
    except:
        return None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in CATEGORY_DELIVERY.keys():
        kb.add(cat)
    await message.answer(f"Привет, {message.from_user.first_name}!
"
                         "Я помогу рассчитать стоимость товара с Poizon.
"
                         "Выбери категорию товара:", reply_markup=kb)

@dp.message_handler(lambda msg: msg.text in CATEGORY_DELIVERY)
async def handle_category(message: types.Message):
    category = message.text
    await message.answer("Введи цену товара в юанях (¥):")
    dp.register_message_handler(lambda m: handle_price(m, category), content_types=types.ContentTypes.TEXT)

async def handle_price(message: types.Message, category):
    try:
        price_cny = float(message.text.replace(",", "."))
        rate = get_cny_to_rub_rate()
        if rate is None:
            await message.answer("Не удалось получить курс юаня. Попробуй позже.")
            return
        base_price = price_cny * rate
        markup_price = base_price * 1.2
        delivery = CATEGORY_DELIVERY[category]
        total = int(markup_price + delivery)
        await message.answer(f"💸 Общая стоимость заказа: <b>{total} ₽</b>

"
                             "Для оформления заказа напиши менеджеру: @MikhailBaburin",
                             parse_mode="HTML")
    except ValueError:
        await message.answer("Пожалуйста, введи корректную числовую цену.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
