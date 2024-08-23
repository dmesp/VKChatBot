import sys
from loguru import logger

from vkbottle import Bot, load_blueprints_from_package

bot = Bot("")
logger.remove()
logger.add(sys.stderr, level="INFO")

for bp in load_blueprints_from_package("blueprints"):
    bp.load(bot)

bot.run_forever()