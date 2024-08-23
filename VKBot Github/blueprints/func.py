#!/usr/bin/env python3
from vkbottle import CtxStorage
from vkbottle.bot import Blueprint, Message, rules, MessageEvent
from vkbottle.dispatch.rules.base import FromUserRule 
import sqlite3, random

import pyowm
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.commons.enums import SubscriptionTypeEnum
from pyowm.utils.measurables import kelvin_to_celsius
from pyowm.commons.enums import SubscriptionTypeEnum

from blueprints.some import get_user #type: ignore

ctx_storage = CtxStorage()

bp = Blueprint("oth")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]


#///////////////////////////////WEATHER///////////////////////////////
config = {              #конфиг для погоды
            'subscription_type': SubscriptionTypeEnum.FREE,
            'language': 'ru',
            'connection': {
                'use_ssl': True,
                'verify_ssl_certs': True,
                'use_proxy': False,
                'timeout_secs': 5
            },
            'proxies': {
                'http': 'http://user:pass@host:port',
                'https': 'socks5://user:pass@host:port'
            }
        }

@bp.on.chat_message(text=["погода <city>", "Погода <city>", "!погода <city>", "/погода <city>", ".погода <city>"])
async def weather_handler(message: Message, city=None):
    if city is not None:
        owm = pyowm.OWM('b887abca0a53adba4d15acef28c0bb2d', config=config)
        member = await get_user(message.from_id)
        
        try:
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(city)
            w = observation.weather
            wind_dict_in_meters_per_sec = observation.weather.wind()
            shitty_wind_speed = str(wind_dict_in_meters_per_sec['speed']); splited_wind = shitty_wind_speed.split("."); wind_speed = splited_wind[0]      #Убираем всё что после точки в скорости ветра
            shitty_temp = str(kelvin_to_celsius(w.temp['temp'])); splited_temp = shitty_temp.split("."); temp = splited_temp[0]                           #Убираем всё что после точки в температуре
            
            await message.answer(f"[id{member.id}|{member.first_name} {member.last_name}], в городе {str(city.title())} сейчас {w.detailed_status}.\n\nТемпература: {str(temp)}°C\nВлажность воздуха: {str(w.humidity)}%\nСкорость ветра: {wind_speed}м/с", disable_mentions=1)
  
        except pyowm.commons.exceptions.NotFoundError:
            await message.answer(f"[id{member.id}|{member.first_name} {member.last_name}], указанный город не найден.", disable_mentions=1)

#///////////////////////////////MMR///////////////////////////////
@bp.on.message(FromUserRule(), text="!ммр")
async def message_handler(message: Message):

    #if member.id == 482856358:
     #  await message.answer("Твой ММР равен 1000000000000000000000000000000000000000000000000000000" + "\n Чел ты Канеки Кен.")
    luckyness = random.randint(1, 6)
    if luckyness == 1 or luckyness == 2 or luckyness == 3:
        mmr = random.randint(0, 7000)
    elif luckyness == 4 or luckyness == 5:
        mmr = random.randint(0, 10000)
    else:
        mmr = random.randint(0, 13000)
    if mmr <= 1000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль C ранга то есть чмо и ничтожество")
    elif mmr <= 2000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль B ранга")
    elif mmr <= 3000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль B+ ранга")
    elif mmr <= 4000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль A ранга")
    elif mmr <= 5000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль A+ ранга")
    elif mmr <= 7000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль S ранга")
    elif mmr <= 9000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль S+ ранга")
    elif mmr <= 11000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль SS ранга")
    elif mmr <= 13000:
        await message.answer("Твой ММР: " + str(mmr) + "/13000\nТы гуль SS+  ранга")
