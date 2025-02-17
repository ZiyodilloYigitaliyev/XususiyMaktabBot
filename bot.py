from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.router import Router
from aiogram import F
from dotenv import load_dotenv
import asyncio
import requests
import logging
import os
from aiogram.filters import Command

# .env fayldan token va boshqa o'zgaruvchilarni yuklaymiz
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_ID_2 = os.getenv("CHANNEL_ID_2")  # Ikkinchi kanal ID sini .env dan oling
CHECK_USER_URL = os.getenv("CHECK_USER_URL", "https://scan-app-9206bf041b06.herokuapp.com/bot/check-user/")
REGISTER_USER_URL = os.getenv("REGISTER_USER_URL", "https://scan-app-9206bf041b06.herokuapp.com/bot/register-user/")
BASE_URL = os.getenv("BASE_URL", "https://backup-questions-e95023d8185c.herokuapp.com/main/get-pdf/")
CHANNEL_STATS_URL = os.getenv("CHANNEL_STATS_URL", "https://scan-app-9206bf041b06.herokuapp.com/bot/channel-stats/")

logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Foydalanuvchi ro'yxatdan o'tganligini API orqali tekshiramiz
def is_user_registered(user_id):
    try:
        response = requests.get(f"{CHECK_USER_URL}?user_id={user_id}")
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Foydalanuvchini tekshirishda xatolik: {e}")
        return False

# Foydalanuvchini API orqali ro'yxatdan o'tkazamiz
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

# Telefon raqamini yuborish uchun tugma
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqam yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Kanalga a'zolikni tekshiramiz (kanal ID sini parametr sifatida oladi)
async def is_user_subscribed(user_id, channel_id):
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Kanal (ID: {channel_id}) a'zoligini tekshirishda xatolik: {e}")
        return False

# Kanal statistikasi APIga yuborish (ikkala kanal uchun misol)
async def send_channel_stats():
    # Birinchi kanal uchun statistikani yuboramiz
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        member_count = await bot.get_chat_member_count(CHANNEL_ID)

        data = {
            "channel_id": chat.id,
            "channel_name": chat.title,
            "username": chat.username or "",
            "description": chat.description or "",
            "member_count": member_count
        }
        response = requests.post(CHANNEL_STATS_URL, json=data)

        if response.status_code == 201:
            logging.info("Birinchi kanal statistikasi APIga muvaffaqiyatli yuborildi.")
        else:
            logging.warning(f"Birinchi kanal statistikasi yuborishda xatolik: {response.text}")
    except Exception as e:
        logging.error(f"Birinchi kanal statistikasi olishda yoki yuborishda xatolik: {e}")

    # Ikkinchi kanal uchun statistikani yuboramiz
    try:
        chat2 = await bot.get_chat(CHANNEL_ID_2)
        member_count2 = await bot.get_chat_member_count(CHANNEL_ID_2)

        data2 = {
            "channel_id": chat2.id,
            "channel_name": chat2.title,
            "username": chat2.username or "",
            "description": chat2.description or "",
            "member_count": member_count2
        }
        response2 = requests.post(CHANNEL_STATS_URL, json=data2)

        if response2.status_code == 201:
            logging.info("Ikkinchi kanal statistikasi APIga muvaffaqiyatli yuborildi.")
        else:
            logging.warning(f"Ikkinchi kanal statistikasi yuborishda xatolik: {response2.text}")
    except Exception as e:
        logging.error(f"Ikkinchi kanal statistikasi olishda yoki yuborishda xatolik: {e}")

# /start buyrug'i kelganida foydalanuvchini xush kelibsiz deb javob qaytaramiz
@router.message(F.text == "/start")
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    # Ikkala kanalga ham a'zo ekanligini tekshiramiz
    subscribed_first = await is_user_subscribed(user_id, CHANNEL_ID)
    subscribed_second = await is_user_subscribed(user_id, CHANNEL_ID_2)

    if subscribed_first and subscribed_second:
        if is_user_registered(user_id):
            await message.answer("Assalomu alaykum! Siz ro'yxatdan o'tgansiz va hamma kanalga obuna bo'lgansiz. Davom etishingiz mumkin.")
        else:
            await message.answer(
                "Assalomu alaykum!\nIltimos, telefon raqamingizni yuboring, ro'yxatdan o'tishingiz kerak.",
                reply_markup=phone_keyboard
            )
        await send_channel_stats()  # Har bir /start buyrug'ida kanal statistikasi yangilanadi
    else:
        # Obuna bo'lmagan kanallar uchun linklarni yuboramiz
        kanal_1_urli = f"https://t.me/bukhara_maktabi"  
        kanal_2_urli = f"https://t.me/dehqonobodcity1"
        await message.answer(
            f"Assalomu alaykum!\nDavom etish uchun iltimos, quyidagi kanallarga obuna bo'ling:\n"
            f"1. [Kanal 1]({kanal_1_urli})\n"
            f"2. [Kanal 2]({kanal_2_urli})\n\n"
            f"Obuna bo'lgach, qaytadan /start buyrug'ini yuboring.",
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

# Foydalanuvchidan yuborilgan ID asosida PDF faylni olish
@router.message(F.text)
async def handle_id(message: types.Message, bot: Bot):
    user_id = message.text.strip()

    # ID 6 xonali raqam ekanligini tekshiramiz
    if not user_id.isdigit() or len(user_id) != 6:
        await message.answer("Noto'g'ri ID! Iltimos, faqat 6 ta raqamdan iborat ID yuboring❌")
        return

    try:
        # API orqali ma'lumotlarni olamiz
        response = requests.get(f"{BASE_URL}?user_id={user_id}")

        if response.status_code == 200:
            data = response.json()

            if "pdf_url" not in data:
                await message.answer("PDF fayl topilmadi ❌")
                return

            # API endi to'liq PDF URL qaytaradi, shuning uchun uni bevosita ishlatamiz
            pdf_url = data['pdf_url']

            # PDF faylni yuklab olish
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                pdf_path = f"temp_{user_id}.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(pdf_response.content)

                # FSInputFile yordamida PDF faylni yuborish
                input_file = FSInputFile(pdf_path)
                await bot.send_document(message.chat.id, input_file)

                # Yaratilgan vaqtinchalik faylni o'chiramiz
                os.remove(pdf_path)
            else:
                await message.answer("PDF yuklab olinmadi ❌")
        else:
            await message.answer("Bunday ID bo‘yicha ma'lumot topilmadi ❌")
    except Exception as e:
        logging.error(f"Xato yuz berdi: {e}")
        await message.answer("Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring.")
        
@router.message(Command("getid"))
async def get_channel_id(message: types.Message):
    try:
        chat = await bot.get_chat(message.chat.id)
        await message.answer(f"Kanal ID: {chat.id}")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# Botni ishga tushiramiz
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
