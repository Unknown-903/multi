import asyncio
import datetime
import logging

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from config import Config
from database.database import Database

db = Database()

log = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Utilities:
    @staticmethod
    def TimeFormatter(seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        formatted_txt = f"{days} days, " if days else ""
        formatted_txt += f"{hours} hrs, " if hours else ""
        formatted_txt += f"{minutes} min, " if minutes else ""
        formatted_txt += f"{seconds} sec, " if seconds else ""
        return formatted_txt[:-2]


@Client.on_callback_query()
async def __(c, m):
    await foo(c, m, cb=True)


@Client.on_message(filters.private)
async def _(c, m):
    await foo(c, m)


async def foo(c, m, cb=False):
    chat_id = m.from_user.id

    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        if Config.LOG_CHANNEL:
            try:
                await c.send_message(
                    Config.LOG_CHANNEL, f"New User {m.from_user.mention}"
                )
            except FloodWait:
                await asyncio.sleep(5)
                await c.send_message(
                    Config.LOG_CHANNEL, f"New User {m.from_user.mention}"
                )
            except Exception as e:
                print(e)
                return
    # ------------------------------------#
    paid_status = await db.get_paid_status(chat_id)
    if paid_status["is_paid"]:
        current_date = datetime.datetime.now()
        paid_duration = paid_status["paid_duration"]
        paid_on = paid_status["paid_on"]
        paid_reason = paid_status["paid_reason"]
        integer_paid_duration = int(paid_duration)
        will_expire = paid_on + datetime.timedelta(days=integer_paid_duration)
        if will_expire < current_date:
            try:
                await db.remove_paid(chat_id)
            except Exception as e:
                log.info(f"⚠️ Error: {e}")
            try:
                await c.send_message(
                    m.chat.id,
                    f"👋 Your paid plan has Expired on {will_expire}\n\nIf you want to use the bot, You can do so by Paying.",
                )
            except Exception as e:
                log.info(f"⚠️ Error: {e}")
            for i in Config.AUTH_USERS:
                try:
                    await c.send_message(
                        i,
                        f"🌟 **Plan Expired:** \n\n**User Id:** `{m.from_user.id}`\n\n**User Name:** @{m.from_user.username}\n\n**Plan Validity:** {paid_duration} Days\n\n**Joined On** : {paid_on}\n\n**Discription** : {paid_reason}",
                    )
                except Exception:
                    log.info(f"⚠️ Not found id {i}")

    # ------------------------------------#
    ban_status = await db.get_ban_status(chat_id)
    if ban_status["is_banned"]:
        if (
            datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])
        ).days > ban_status["ban_duration"]:
            await db.remove_ban(chat_id)

    last_used_on = await db.get_last_used_on(chat_id)
    if last_used_on != datetime.date.today().isoformat():
        await db.update_last_used_on(chat_id)

    await m.continue_propagation()
