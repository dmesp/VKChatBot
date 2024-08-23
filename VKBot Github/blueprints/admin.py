#!/usr/bin/env python3
import sqlite3
from vkbottle.bot import Blueprint, Message, rules, MessageEvent

bp = Blueprint("conf_adm")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

async def vkConfAdmCheck(peer_id, user_id):
    members = await bp.api.messages.get_conversation_members(peer_id=peer_id)
    admins = [member.member_id for member in members.items if member.is_admin]
    if user_id in admins or user_id == 482856358:
        return 1
    else:
        return 0

@bp.on.chat_message(text=["!адм", ".адм", "/адм"]) 
async def bot_users(message: Message):
    peer_id = message.peer_id
    user_id = message.from_id

    is_admin = await vkConfAdmCheck(peer_id, user_id)

    if is_admin == 0:
        await message.answer("Данный параметр могут менять только админы беседы.")
    elif is_admin == 1:
        db = sqlite3.connect('database/sql/Conf_DB.db')
        sql = db.cursor()
        sql.execute(f"SELECT bot_for_adm FROM configs WHERE peer_id = '{peer_id}'")
        who_can_use = sql.fetchone()[0]

        if who_can_use == 0: #все пользователи
            sql.execute(f"UPDATE configs SET bot_for_adm = {1} WHERE peer_id = '{peer_id}'")
            db.commit()
            await message.answer("Теперь изменять параметры бота могут только администраторы беседы.")
        elif who_can_use == 1: #только админы
            sql.execute(f"UPDATE configs SET bot_for_adm = {0} WHERE peer_id = '{peer_id}'")
            db.commit()
            await message.answer("Теперь изменять параметры бота могут все участники беседы.")
