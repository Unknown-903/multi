import logging

from pyrogram import Client, filters

from config import Config
from plugins.audio import COUNT

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(
    filters.command(["count_increase", "ci"]) & filters.user(Config.AUTH_USERS)
)
async def ciunti_(bot, update):
    # extra = [1, 2, 3]
    COUNT.append(1851062714)
    await update.reply(
        f"1 User increased ✅ /pv",
        reply_to_message_id=update.id,
    )
