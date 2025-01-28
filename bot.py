from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
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
CHANNEL_ID = "@1980274573"  # Kanal ID sini kiriting
CHECK_USER_URL = "https://scan-app-9206bf041b06.herokuapp.com/bot/check-user/"  # Foydalanuvchini tekshirish uchun API URL
REGISTER_USER_URL = "https://scan-app-9206bf041b06.herokuapp.com/bot/register-user/"  # Foydalanuvchini ro'yxatdan o'tkazish uchun API URL
BASE_URL = "https://your-api.com/resource"  # GET so'rovi uchun API URL

logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Foydalanuvchi ro'yxatdan o'tganini API orqali tekshirish
def is_user_registered(user_id):
    try:
        response = requests.get(f"{CHECK_USER_URL}?user_id={user_id}")
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Foydalanuvchini tekshirishda xatolik: {e}")
        return False

# Foydalanuvchini API orqali ro'yxatdan o'tkazish
def register_user(user_id, phone_number):
    try:
        data = {
            "user_id": user_id,
            "phone_number": phone_number,
        }
        response = requests.post(REGISTER_USER_URL, json=data)
        return response.status_code == 201
    except Exception as e:
        logging.error(f"Foydalanuvchini ro'yxatdan o'tkazishda xatolik: {e}")
        return False

# Telefon raqami uchun tugma
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqam yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Kanalga a'zolikni tekshirish
async def is_user_subscribed(user_id):
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Kanal a'zoligini tekshirishda xatolik: {e}")
        return False


@router.message(F.text == "/start")
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    if await is_user_subscribed(user_id):  # Agar kanalga obuna bo'lsa
        if is_user_registered(user_id):  # Agar ro'yxatdan o'tgan bo'lsa
            await message.answer("Assalomu alaykum! Siz ro'yxatdan o'tgansiz va kanalga obuna bo'lgansiz. Davom etishingiz mumkin.")
        else:
            await message.answer(
                "Assalomu alaykum!\nIltimos, telefon raqamingizni yuboring, ro'yxatdan o'tishingiz kerak.",
                reply_markup=phone_keyboard
            )
    else:  # Kanalga obuna bo'lmasa
        kanal_urli = f"https://t.me/bukhara_maktabi"
        await message.answer(
            f"Assalomu alaykum!\nDavom etish uchun [kanalimizga obuna bo'ling]({kanal_urli}) va qaytadan /start komandasini yuboring.",
            parse_mode="Markdown"
        )
# Telefon raqamini qabul qilish
@router.message(F.contact)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    if register_user(user_id, phone_number):
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Endi davom etishingiz mumkin.", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Ro'yxatdan o'tishda xatolik yuz berdi. Keyinroq qayta urinib ko'ring.")

# ID qabul qilish
@router.message(F.text)
async def handle_id(message: types.Message):
    user_id = message.text.strip()

    if not user_id.isdigit() or len(user_id) != 6:
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
