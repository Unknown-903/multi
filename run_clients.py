import asyncio
import logging
import pyromod
from pyrogram import idle
from pyromod import listen
from config import Config
from main import BOT, USERBOT
from plugins.audio import COUNT

logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


async def booted(bot):
    chats = Config.AUTH_USERS

    try:
        #COUNT.append(1868056307)
        # COUNT.append(1868056307)
        # COUNT.append(1868056307)
        # COUNT.append(1868056307)
        # COUNT.append(1868056307)
        logger.info(f"Added Counting")
    except Exception as e:
        logger.info(f"⚠️ Main Error: {e}")

    for i in chats:
        try:
            await bot.send_message(i, "The Bot is Restarted ♻️ Now")
        except Exception:
            logger.info(f"⚠️ Not found id {i}")


async def start_bots():
    print("Processing.....")
    '''   
    try:
        await BOT.start()
        logger.info(f"Bot is Running....🏃‍♂️")
    except Exception as e:
        logger.info(f"⚠️ Bot Error: {e}")
    '''

    await BOT.start()   
    if Config.SESSION_STRING:
        try:
            await USERBOT.start()
            logger.info(f"UserBot is Running....🏃")
        except Exception as e:
            logger.info(f"⚠️ UserBot Error: {e}")

    await booted(BOT)
    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_bots())
    except KeyboardInterrupt:
        logger.info(f"⚠️ Bots Stopped!! Problem in loop run")
