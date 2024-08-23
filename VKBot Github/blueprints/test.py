#!/usr/bin/env python3
import requests
from array import *
from bs4 import BeautifulSoup
from vkbottle import Callback, Keyboard, KeyboardButtonColor, PhotoMessageUploader, GroupEventType, TemplateElement, template_gen
from vkbottle.tools import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Blueprint, Message, rules

bp = Blueprint("test")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

from blueprints.some import peer_id_fix    # type: ignore

@bp.on.chat_message(text="ф <a>")
async def parser(message: Message, a=None):
    response = requests.get("https://www.anekdot.ru") 
    soup = BeautifulSoup(response.content, 'html.parser') 
    a = int(a)
    tag = soup.select('.text')[a]
    print(tag)
    await message.answer(str(tag.text))

async def peer_id_fix(id):
    peer_id = "2"
    zeros = 9 - len(id)
    for i in range(zeros):
        peer_id += "0"
    peer_id += str(id)
    return peer_id

KEYBOARD_SNUS = (
    Keyboard(one_time=False, inline=True)
    .add(Callback("КУПИТЬ КУПИТЬ", payload={"cmd": "snackbar2"}), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Callback("КУПИТЬ КУПИТЬ", payload={"cmd": "snackbar2"}), color=KeyboardButtonColor.SECONDARY)
    .get_json()
)

template = template_gen(
    TemplateElement(
        buttons=KEYBOARD_SNUS, action={"type": "open_photo"}, title="Mint", description="25", photo_id="-180661523_457239041",
    ),
    TemplateElement(
        buttons=KEYBOARD_SNUS, action={"type": "open_photo"}, title="Mint", description="25", photo_id="-180661523_457239042",
    ),
    TemplateElement(
        buttons=KEYBOARD_SNUS, action={"type": "open_photo"}, title="Mint", description="25", photo_id="-180661523_457239041",
    ),
)

@bp.on.message(text="!снс")
async def template_handler(message: Message):
    await message.answer("держи", template=template)

@bp.on.private_message(text=["отв <id> <msg>"])
async def message_reply(message: Message, id=None, msg=None):  
    msg_peer = await peer_id_fix(id)
    fwd_message_id = message.fwd_messages[0].conversation_message_id
    fwd_message_id_list = []
    fwd_message_id_list.append(fwd_message_id)
    fwd_message_id_list.append("50763")
    await message.answer(str(message.fwd_messages))
    await bp.api.messages.send(peer_id=msg_peer, forward_messages=fwd_message_id_list, message=str(msg), random_id=0)

@bp.on.message(text=["отв2 <id> <msg>"])
async def message_reply(message: Message, id=None, msg=None):  
    msg_peer = await peer_id_fix(id)
    reply_message = message.reply_message.conversation_message_id
    fwd_message_id_list = []
    fwd_message_id_list.append(reply_message)
    await message.answer(str(message.fwd_messages))
    await bp.api.messages.send(peer_id=msg_peer, forward_messages=fwd_message_id_list, message=str(msg), random_id=0)
