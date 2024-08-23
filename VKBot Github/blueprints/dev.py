#!/usr/bin/env python3
import requests 
import os, asyncio, datetime, requests
from vkbottle.bot import Blueprint, Message, rules, MessageEvent
from bs4 import BeautifulSoup
from memory_profiler import memory_usage 


bp = Blueprint("dev_coms")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

from blueprints.some import peer_id_fix, get_user #type: ignore

#/////////////////////////////////////////////////////////////////////////////////////

def ram_use():
	x = str(memory_usage())
	replaced = x.replace("[", ""); replaced = replaced.replace("]", "")
	return replaced[0:4] + " MБ🥀"

@bp.on.message(text="!рам")
async def message_handler(message: Message):
    await message.answer(ram_use())

@bp.on.chat_message(text=["!юид"])
async def USER_GENERATION(message: Message):
    reply = message.reply_message.from_id
    await message.answer(str(reply))

@bp.on.chat_message(text=["!мид"])
async def USER_GENERATION(message: Message):
    reply = message.reply_message
    await message.answer(str(reply.conversation_message_id))

@bp.on.chat_message(text=["!чид"])
async def chatID(message: Message):
    id = message.chat_id
    await message.answer(str(id))

@bp.on.chat_message(text=["!рид"])
async def USER_GENERATION(message: Message):
    reply = message.reply_message
    await message.answer(str(reply))

@bp.on.chat_message(text=["!инф"])
async def USER_GENERATION(message: Message):
    reply = message
    await message.answer(str(reply))

@bp.on.chat_message(text=["стикид"])
async def USER_GENERATION(message: Message):
    reply_message = message.reply_message.attachments
    attachments = reply_message[0]
    sticker = attachments.sticker
    await message.answer(f"ID стикера\n" + str(sticker.sticker_id))

@bp.on.chat_message(text=["стикер <conf_id> <stick_id>"])
async def admin_anon(message: Message, conf_id=None, sid=None):
    peer_id = await peer_id_fix(id)
    await bp.api.messages.send(peer_id=peer_id, sticker_id=sid, random_id=0)

@bp.on.message(text="!выкл <time>")
async def hi_handler(message: Message, time=None):
    member = await get_user(message.from_id)
    if member.id == 482856358:
        if int(time) is not None and int(time) < 120:
            await message.answer(f"Откиснем через {time} минут.")
            await asyncio.sleep(int(time) * 60) 
            await message.answer("прощайте")
            os.system('shutdown -s') 
    else:
        await message.answer("тебе нельзя.")

@bp.on.private_message(text=["гнон <id> <msg>", "г <id> <msg>"])
async def admin_anon(message: Message, id=None, msg=None):
    peer_id = await peer_id_fix(id)
    await bp.api.messages.send(peer_id=peer_id, message= str(msg), random_id=0)

@bp.on.private_message(text=["ск <id>"])
async def fwd_message_delete(message: Message, id=None):
    fwd_message_list = message.fwd_messages
    fwd_message_list_lenght = len(fwd_message_list)
    fwd_message_id_list = []
    msg_peer = await peer_id_fix(id)
    for i in range(fwd_message_list_lenght):
        fwd_message = fwd_message_list[i]
        fwd_message_id_list.append(fwd_message.conversation_message_id)
    try:
        await bp.api.messages.delete(cmids=fwd_message_id_list, peer_id=msg_peer, delete_for_all=1)
        await message.reply("Удалено.")
    except Exception as e:
        await message.answer("Произошла ошибка:\n" + str(e))

@bp.on.private_message(text=["удалить <id> <msg_id>"])
async def fwd_message_delete(message: Message, id=None, msg_id=None):
    fwd_message_id_list = []
    msg_peer = await peer_id_fix(id)
    fwd_message_id_list.append(msg_id)
    try:
        await bp.api.messages.delete(cmids=fwd_message_id_list, peer_id=msg_peer, delete_for_all=1)
        await message.reply("Удалено.")
    except Exception as e:
        await message.answer("Произошла ошибка:\n" + str(e))
