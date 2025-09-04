import logging
import random

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import re

from pyshorteners import Shortener
from unshortenit import UnshortenIt


@Client.on_callback_query(filters.regex("^shortunshort"))
async def short_unshort_(bot, update):
    await update.message.delete()
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    update.from_user.id
    if update.from_user.id not in Config.AUTH_USERS:
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
    global link
    link = reply_msg.text
    type1 = "https://*"
    type2 = "http://*"
    logger.info(link)

    if (re.search(type1, link)) or (re.search(type2, link)):
        BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Short", callback_data="lshort"),
                    InlineKeyboardButton("Unshort", callback_data="lunshort"),
                ]
            ]
        )
        Text = "Select from below options whether you want to short or unshort your URL"
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=Text,
            reply_markup=BUTTONS,
            reply_to_message_id=reply_msg.id,
        )
    else:
        await update.reply_text(
            "**⚠️ Wrong URL format !!!**\n\nURL must start with http:// or https://\n\nAnd it should not have spaces in it.",
            reply_to_message_id=reply_msg.id,
        )


@Client.on_callback_query()
async def button(bot, update):
    diksha_baby = update.data
    if diksha_baby == "lunshort":
        try:
            unshortener = UnshortenIt()
            url = unshortener.unshorten(link)
            CM = f"**Unshortened Link** 👇\n\n{url}"
            URL = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Unshortened Link", url=url)],
                ]
            )
            await update.message.edit_text(
                text=CM,
                reply_markup=URL,
                disable_web_page_preview=True,
            )
            logger.info(
                f"{url} Link is Unshorted ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as error:
            print(
                f"URL Is Already an UnShortened URL ⚠️\n⚡ Error : {error} @{update.from_user.username}"
            )
            try:
                await update.message.edit(f"⚠️ URL Is Already a UnShortened URL")
            except:
                pass

    elif diksha_baby == "lshort":
        try:
            s = Shortener(api_key=random.choice(Config.BITLY_KEY))
            # s = Shortener(api_key=Config.BITLY_KEY)
            shortened_url = s.bitly.short(link)
            Chitranjan = f"**Shortened Link** 👇\n\n{shortened_url}"
            Diksha = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Shortened Link", url=shortened_url)],
                ]
            )
            await update.message.edit_text(
                text=Chitranjan,
                reply_markup=Diksha,
                disable_web_page_preview=True,
            )
            logger.info(shortened_url)
            logger.info(
                f"✅ A Link is Shortened By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as error:
            print(
                f"URL Is Already a Shortened URL ⚠️\n⚡ Error : {error} @{update.from_user.username}"
            )
            try:
                await update.message.edit(f"⚠️ URL Is Already a Shortened URL")
            except:
                pass

    else:
        raise ContinuePropagation
