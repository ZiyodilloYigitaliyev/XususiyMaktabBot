from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.router import Router
from aiogram import F
from dotenv import load_dotenv
import asyncio
import requests
import logging
import os

# .env fayldan tokenni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://your-api.com/resource"  # GET so'rovi uchun API bazaning URL

logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ID ni tekshirish funksiyasi
def is_valid_id(id_value):
    return id_value.isdigit() and len(id_value) == 6

# Start komandasiga javob
@router.message(F.text == "/start")
async def send_welcome(message: types.Message):
    await message.answer("Assalomu alaykum!\n Menga 6 ta raqamdan iborat ID yuboring.")

# ID qabul qilish
@router.message(F.text)
async def handle_id(message: types.Message):
    user_id = message.text.strip()

    if not is_valid_id(user_id):
        await message.answer("Noto'g'ri ID! Iltimos, faqat 6 ta raqamdan iborat ID yuboring❌")
        return

    # API GET so'rovi
    try:
        response = requests.get(f"{BASE_URL}?id={user_id}")
        if response.status_code == 200:
            pdf_path = "downloaded_file.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)

            # PDF ni foydalanuvchiga yuborish
            await bot.send_document(message.chat.id, InputFile(pdf_path))
        else:
            await message.answer("Kechirasiz, bazada ma'lumot topilmadi🙁")
    except Exception as e:
        logging.error(f"Xato yuz berdi: {e}")
        await message.answer("Xatolik yuz berdi. Keyinroq qayta urinib ko'ring.")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
