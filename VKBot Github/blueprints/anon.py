#!/usr/bin/env python3
import sqlite3
from vkbottle import GroupEventType, Callback, Keyboard, KeyboardButtonColor, GroupEventType
from vkbottle.tools import Keyboard, KeyboardButtonColor
from vkbottle.bot import Blueprint, Message, rules, MessageEvent

from blueprints.some import peer_id_fix, admin_checker # type: ignore

#//////////////////////////////////////////RULES\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
bp = Blueprint("anon")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

#//////////////////////////////////////////FUNCS\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
async def anon_condition_reader(peer_id):
    """Получение параметра анонимных сообщений"""
    db = sqlite3.connect("database/sql/Conf_DB.db")
    sql = db.cursor()
    sql.execute(f"SELECT anon_allower FROM configs WHERE peer_id = '{peer_id}'")
    return sql.fetchone()[0]

async def anon_condition_writer(peer_id):
    """Запись параметра анонимных сообщений"""
    oldPosition = await anon_condition_reader(peer_id)
    db = sqlite3.connect("database/sql/Conf_DB.db")
    sql = db.cursor()

    if oldPosition == 1:
        sql.execute(f"UPDATE configs SET anon_allower = ? WHERE peer_id = '{peer_id}'", (0,))
        db.commit()
        return "Анонимные сообщения от участников беседы отключены."
    elif oldPosition == 0:
        sql.execute(f"UPDATE configs SET anon_allower = ? WHERE peer_id = '{peer_id}'", (1,))
        db.commit()
        return "Анонимные сообщения от участников беседы включены."

#//////////////////////////////////////////ANON MSG SCRIPTS\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@bp.on.chat_message(text=["!анон", "/анон", ".анон"])
async def anon_turner(message: Message):
    peer_id = message.peer_id
    admin_allower = await admin_checker(peer_id, message.from_id)

    if admin_allower == "bot_not_for_admins":
        await message.answer(await anon_condition_writer(peer_id))

    else:
        if admin_allower == "user_is_admin":
            await message.answer(await anon_condition_writer(peer_id))
        elif admin_allower == "user_is_not_admin":
            await message.answer("Ты не администратор.")
           
@bp.on.private_message(text=["анон <id> <msg>", """<prefix>ан <id> <msg>"""])
async def anon_message(message: Message, id=None, msg=None):
    try:            
        peer_id = await peer_id_fix(id) #creating normal peer_id from chat_ide
        anon_allower = await anon_condition_reader(peer_id) #проверяем разрешены ли анонимные сообщения
        if anon_allower == 1:
            await bp.api.messages.send(peer_id=peer_id, message= "Анонимное сообщение:\n" + str(msg), random_id=0)
        else:
            await message.answer("В беседе запрещены анонимные сообщения.")

    except TypeError as e:
        await message.answer("Бота нет в беседе с таким ID.\nУзнать ID можно введя команду !ид в беседе.")

@bp.on.private_message(text=["анон", "анон <id>"])
async def anon_helper_button(message: Message):
    await message.answer("Введите сообщение в формате: \n анон <id беседы> <сообщение>", keyboard=KEYBOARD_ANON_HELPER)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT,MessageEvent,rules.PayloadRule({"cmd": "idHelp"}),)
async def anon_guide(event: MessageEvent):
    await event.edit_message("ID беседы можно узнать введя команду !ид в нужной беседе.\n Если бот отвечает 'Запрещено', значит в беседе отключены анонимные сообщения.")

KEYBOARD_ANON_HELPER = (
    Keyboard(one_time=False, inline=True)
    .add(Callback("Как узнать ID беседы", payload={"cmd": "idHelp"}), color=KeyboardButtonColor.SECONDARY))