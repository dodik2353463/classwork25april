from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import keyboards as kbss

from database import *

import take_info
from apscheduler.schedulers.asyncio import AsyncIOScheduler

router_start = Router()


class Set_time(StatesGroup):
    time = State()

start_txt = 'Привет!\nЭто бот подарит тебе настроение, рассказав о сегодяншнем празднике.'

@router_start.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(start_txt, reply_markup=kbss.main)

@router_start.message(F.text.lower().in_({'задать время рассылки', '/set_time'}))
async def set_settings_rassilka(message: Message, state: FSMContext):
    await message.answer('Отправьте время в формате ЧЧ:ММ')
    await state.set_state(Set_time.time)

@router_start.message(Set_time.time)
async def set_time(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer('Вы должны ввести сообщение. Попробуйте еще раз')
        return
    
    if ':' not in message.text:
        await message.answer('Введенное время должно содержать двоеточие (:)')
        return
    hours, minute = str(message.text).split(':')
    if not(hours.isdigit()) or not(minute.isdigit()):
        await message.answer('Час и минута - целые числа')
        return
    if len(hours) != 2 or len(minute) != 2:
        await message.answer('Час и минута должны состоять из двух цифр')
        return
    
    elif not(0 <= int(hours) <= 23):
        await message.answer('Неправильно указан час')
        return
    elif not(0 <= int(minute) <= 59):
        await message.answer('Неправильно указана минута')
        return
    
    FileClass.get_or_none(user_id_tg=message.from_user.id)
    if FileClass.get_or_none(user_id_tg=message.from_user.id) == None:
        FileClass.create(user_id_tg=message.from_user.id, time=f'{hours}:{minute}')
    else:
        user = FileClass.get(user_id_tg=message.from_user.id)
        user.time =  f'{hours}:{minute}'
        user.save()
    
    await message.answer(f'Установлено время рассылки на {hours}:{minute}')
    await state.clear()
    scheduler.add_job(send_message_time, trigger='cron', hour=hours, minute=minute, kwargs={'bot':bot_copy, 'id_user':message.from_user.id})

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

bot_copy = None

def tuti_fruti(bot):
    global bot_copy
    tot = 1
    bot_copy = bot
    info()
    while FileClass.get_or_none(id=tot) != None:
        user = FileClass.get(id=tot)
        scheduler.add_job(send_message_time, trigger='cron', hour=user.time.hour, minute=user.time.minute, kwargs={'bot':bot, 'id_user':user.user_id_tg})
        tot += 1
    scheduler.start()

async def send_message_time(bot: Bot, id_user):
    await bot.send_message(chat_id=id_user, text=f'{title_first}\n{abz_first}')

title_first, abz_first = '', ''
def info():
    global title_first, abz_first
    month, day = datetime.today().strftime('%m %d').split()
    title_first, abz_first = take_info.find_info_day(int(day), int(month))
