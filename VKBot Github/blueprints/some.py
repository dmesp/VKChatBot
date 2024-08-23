#!/usr/bin/env python3
import sqlite3
from vkbottle.bot import Blueprint, Message, rules

bp = Blueprint("func")
bp.labeler.vbml_ignore_case = True
bp.labeler.auto_rules = [rules.FromUserRule(True)]

async def peer_id_fix(id):
    peer_id = "2"
    zeros = 9 - len(id)
    for i in range(zeros):
        peer_id += "0"
    peer_id += str(id)
    return peer_id

async def admin_checker(peer_id, user_id):
    db = sqlite3.connect('database/sql/Conf_DB.db')
    sql = db.cursor()
    sql.execute(f"SELECT bot_for_adm FROM configs WHERE peer_id = '{peer_id}'")
    bot_only_for_admins = sql.fetchone()[0]
    
    if bot_only_for_admins == 1: 
        members = await bp.api.messages.get_conversation_members(peer_id=peer_id)
        admins = [member.member_id for member in members.items if member.is_admin]

        if user_id in admins or user_id == 482856358:
            return "user_is_admin"
        else:
            return "user_is_not_admin"           
    elif bot_only_for_admins == 0: 
        return "bot_not_for_admins"

async def bot_usement_checker(peer_id, user_id):
    db = sqlite3.connect('database/sql/Conf_DB.db')
    sql = db.cursor()
    sql.execute(f"SELECT bot_for_adm FROM configs WHERE peer_id = '{peer_id}'")
    bot_only_for_admins = sql.fetchone()[0]
    
    if bot_only_for_admins == 1: 
        members = await bp.api.messages.get_conversation_members(peer_id=peer_id)
        admins = [member.member_id for member in members.items if member.is_admin]

        if user_id in admins or user_id == 482856358:
            return "allowed"
        else:
            return "denied"           
    elif bot_only_for_admins == 0:
        return "allowed"

async def get_user(user_id):
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
