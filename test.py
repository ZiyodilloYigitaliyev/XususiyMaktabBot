import asyncio
from aiogram import Bot

BOT_TOKEN = "7934223335:AAEC2IMl6Naph9AJlnvQ17w9TfjG2gu7Pio"  # Bot tokeningizni shu yerga yozing
CHANNEL_USERNAME = "@dehqonobodcity1"  # Kanal username sini yozing

async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        # Kanal haqidagi ma'lumotlarni olish
        chat = await bot.get_chat(CHANNEL_USERNAME)
        print("Kanal ID:", chat.id)
    except Exception as e:
        print("Xatolik yuz berdi:", e)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
