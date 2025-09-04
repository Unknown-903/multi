from pyrogram import Client, filters

from config import Config
from database.database import Database

db = Database()


@Client.on_message(
    filters.private & filters.command("status") & filters.user(Config.AUTH_USERS)
)
async def sts(c, m):
    total_users = await db.total_users_count()
    text = f"Total users till date : {total_users}"
    await m.reply_text(text=text, quote=True)
