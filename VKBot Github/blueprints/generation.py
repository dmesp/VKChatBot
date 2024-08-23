#!/usr/bin/env python3
import re
import sqlite3
import aiofiles
import os
import asyncio
from gtts import gTTS

from random import choice, randint

from markovify import NewlineText

from vkbottle import GroupEventType, Callback, Keyboard, KeyboardButtonColor, VoiceMessageUploader
from vkbottle.tools import Keyboard, KeyboardButtonColor
from vkbottle.bot import Blueprint, Message, rules, MessageEvent
from vkbottle.dispatch.rules.base import FromUserRule, ChatActionRule

from blueprints.some import bot_usement_checker, get_user #type: ignore

bp = Blueprint("generation")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////

async def getUser(user_id):
	try: 
		return (await bp.api.users.get(user_ids=user_id))[0]
	except: 
		return None

async def getid(pattern):
	pattern = str(pattern)
	if pattern.isdigit(): 
		return pattern
	elif "vk.com/" in pattern:
		your_id = (await bp.api.users.get(user_ids=pattern.split("/")[-1]))[0]
		return your_id.id
	elif "[id" in pattern:
		your_id = pattern.split("|")[0]
		your_id = (await bp.api.users.get(user_ids = your_id.replace("[id", "")))[0]

async def adm_check(peer_id, user_id):
    members = await bp.api.messages.get_conversation_members(peer_id=peer_id)
    admins = [member.member_id for member in members.items if member.is_admin]
    if user_id in admins:
        return True
    else:
        return False

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@bp.on.chat_message(ChatActionRule("chat_invite_user"))
async def invited(message: Message) -> None:
    if message.group_id == -message.action.member_id:
        await message.answer("Для нормальной работы мне НЕОБХОДИМЫ права администратора!\nПри удаление меня из беседы, база данных будет стёрта.\nСписок команд https://vk.com/@petrobratik-petrohelp-first")
        peer_id = message.peer_id

        db = sqlite3.connect('database/sql/Conf_DB.db')
        sql = db.cursor()

        sql.execute(f"INSERT INTO configs VALUES (?, ?, ?, ?)", (peer_id, 20, True, True))
        db.commit()

@bp.on.private_message(text="Начать")
async def startMessage(message: Message) -> None:
    await message.answer("https://vk.com/@petrobratik-petrohelp-first")

@bp.on.chat_message(text=["!помощь", "!начать", "/помощь", "/начать"])
async def chatHelper(message: Message,) -> None:
    await message.answer("Список команд бота вы можете найти тут:\nhttps://vk.com/@petrobratik-petrohelp-first")

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
async def adminRider(peer_id):
    db = sqlite3.connect("database/sql/Conf_DB.db")
    sql = db.cursor()
    sql.execute(f"SELECT bot_for_adm FROM configs WHERE peer_id = '{peer_id}'")
    return sql.fetchone()[0]

async def chanceRider(peer_id):
    db = sqlite3.connect("database/sql/Conf_DB.db")
    sql = db.cursor()
    sql.execute(f"SELECT gen_chance FROM configs WHERE peer_id = '{peer_id}'") 
    return sql.fetchone()[0]   

async def chanceWriter(peer_id, gen_chance):
    db = sqlite3.connect("database/sql/Conf_DB.db")
    sql = db.cursor()
    sql.execute(f"UPDATE configs SET gen_chance = ? WHERE peer_id = ?", (gen_chance, peer_id,))
    db.commit()

@bp.on.chat_message(FromUserRule(), text=["!шанс <chance>", "/шанс <chance>", ".шанс <chance>"])
async def CHANCE_CHANGER(message: Message, chance=None):
    if chance is not None: 
        if await bot_usement_checker(message.peer_id, message.from_id) == "allowed":
            if int(chance) >= 0 and int(chance) <= 100: 
                await chanceWriter(message.peer_id, chance)
                await message.answer("Шанс изменен на " + chance + "%.")
            else:
                await message.answer("Шанс должен быть в диапазоне от 0 до 100")
        else:
            await message.reply("Этот параметр могут менять только админы.")

@bp.on.chat_message(FromUserRule(), text=["!шанс", "/шанс", ".шанс"])
async def SENDER(message: Message):
    gen_chance = await chanceRider(message.peer_id)

    if gen_chance != 0:
        await message.answer("Шанс: " + str(gen_chance) + "%", keyboard=KEYBOARD_CHANCEOFF)
    elif gen_chance == 0:
        await message.answer("На данный момент генерация отключена. Хотите включить?", keyboard=KEYBOARD_CHANCE_CHOOSE)


KEYBOARD_CHANCE_CHOOSE = ( #КЛАВИАТУРА ВЫБОРА ВКЛЮЧИТЬ ЛИ ГЕНЕРАЦИЮ
    Keyboard(one_time=False, inline=True)
    .add(Callback("Да", payload={"cmd": "choose"}), color=KeyboardButtonColor.POSITIVE)
)

KEYBOARD_CHANCEON = ( #ВЫБОР ШАНСА ГЕНЕРАЦИИ
    Keyboard(one_time=False, inline=True)
    .add(Callback("Включить на 20%.", payload={"chance": "20"}), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Callback("Включить на 50%.", payload={"chance": "50"}), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Callback("Включить на 75%.", payload={"chance": "75"}), color=KeyboardButtonColor.SECONDARY)
    .get_json()
)

KEYBOARD_CHANCEOFF = ( #КЛАВИАТУРА ОТКЛЮЧЕНИЯ ГЕНЕРАЦИИ
    Keyboard(one_time=False, inline=True)
    .add(Callback("Отключить генерацию.", payload={"off": "gen_off"}), color=KeyboardButtonColor.NEGATIVE)
    .get_json()
)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT,MessageEvent,rules.PayloadRule({"off": "gen_off"}),)
async def show_snackbar(event: MessageEvent):
    peer_id = event.peer_id
    user_id = event.user_id
    if await bot_usement_checker(peer_id, user_id) == "allowed":
        await chanceWriter(peer_id, 0)
        member = await get_user(user_id)
        await event.edit_message(f"Генерация была отключенa.\n([id{member.id}|{member.first_name} {member.last_name}])", disable_mentions=1)
    else:
        await event.show_snackbar("Доступно только администраторам беседы.")

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT,MessageEvent,rules.PayloadRule({"cmd": "choose"}),)
async def show_snackbar(event: MessageEvent):
    await event.edit_message("Выбирайте что вам угодно.", keyboard=KEYBOARD_CHANCEON)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT,MessageEvent)
async def show_snackbar(event: MessageEvent):
    peer_id = event.peer_id
    user_id = event.user_id
    if await bot_usement_checker(peer_id, user_id) == "allowed":
        event_dict = event.payload
        chance = event_dict["chance"]
        if chance == "20":
            await chanceWriter(peer_id, 20)
            await event.edit_message("Шанс генерации выставлен на 20%")
        elif chance == "50":
            await chanceWriter(peer_id, 50)
            await event.edit_message("Шанс генерации выставлен на 50%")
        elif chance == "75":
            await chanceWriter(peer_id, 75)
            await event.edit_message("Шанс генерации выставлен на 75%")
    else:
        await event.show_snackbar("Доступно только администраторам беседы.")

#/////////////////////////////////////////////////GENERATION/////////////////////////////////////////////////#

@bp.on.chat_message(text=["г", "!г", ".г", "/г", "г <user_message>", "!г <user_message>",  ".г <user_message>", "/г <user_message>", ".g <user_message>", "!g <user_message>", "g <user_message>", ])
async def USER_GENERATION(message: Message, user_message=None):
    peer_id = message.peer_id

    async with aiofiles.open(f"database/{peer_id}.txt", encoding="utf-8") as f:
        db = await f.read()
    text_model = NewlineText(input_text=db, well_formed=False, state_size=1)
    sentence = text_model.make_sentence(tries=10)

    try:
        reply = message.reply_message.text
        await message.answer(str(reply) + " " + sentence.lower())
    except AttributeError:
        if user_message is not None:   
            await message.answer(user_message + " " +sentence.lower())
        elif user_message is None:
            await message.answer(sentence.lower())

#RANDOM GENERATION
@bp.on.chat_message(FromUserRule())
async def TALK(message: Message) -> None:              
    if str(message.attachments) == '[]':
        text = message.text
        peer_id = message.peer_id 
        if "/" not in text and "[" not in text and "]" not in text and len(text) > 1 and text[0] != "!" and len(text) < 301:
            # Удаление пустых строк из полученного сообщения
            while "\n\n" in text:
                text = text.replace("\n\n", "\n")

            # Преобразование [id1|@durov] в @id1
            pattern = re.compile(r"\[id(\d*?)\|.*?]")
            user_ids = tuple(set(pattern.findall(text)))
            for user_id in user_ids:
                text = re.sub(rf"\[id{user_id}\|.*?]", f"@id{user_id}", text)

            # Запись нового сообщения в историю беседы
            async with aiofiles.open(f"database/{peer_id}.txt", "a", encoding="utf-8") as f:
                await f.write(f"\n{text}")
        else:
            pass

        gen_chance = await chanceRider(peer_id)            
        if randint(1, 100) > int(gen_chance):
            pass

        else:
            file_name = f"database/{peer_id}.txt"
            async with aiofiles.open(file_name, encoding="utf-8") as f:
                db = await f.read()
            text_model = NewlineText(input_text=db, well_formed=False, state_size=1)
            sentence = text_model.make_sentence(tries=10) or choice(db.splitlines())
            await message.answer(str(sentence))
    else:
        pass
            
