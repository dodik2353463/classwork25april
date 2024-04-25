import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlrs_start_menu import router_start, tuti_fruti

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router_start)
    tuti_fruti(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('KONEC')
