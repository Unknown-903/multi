import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import Config
from database.database import Database
from plugins.settings import OpenSettings

db = Database()

from main import USERBOT

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# -------------- Settings ----------------#
async def USettings(m: Message, user_id: int):
    
    tguploads = await db.get_tgpremium(user_id)
    yfilter = await db.get_yfilter(user_id)
    for_media = 1969772008
    for_url = 1969772008

    try:
        await m.edit(
            text="**⚙️ Config Bot Settings**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{'🔊 Trimmer Codec : Copy' if (await db.get_trimming_proc(id=Config.OWNER_ID)) is True else '🔊 Trimmer Codec : Default'}",
                            callback_data="trimming_proc",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"📁 Media Functions : {'On' if (await db.get_mediafunctions(id=Config.OWNER_ID)) is True else 'Off'}",
                            callback_data="usmediaf",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"🔗 URL Functions : {'On' if (await db.get_urlfunctions(id=Config.OWNER_ID)) is True else 'Off'}",
                            callback_data="usurlf",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"📁 File Split Size : {tguploads}",
                            callback_data="pstgupload",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"YTDL Filter : {yfilter}", callback_data="filterytdl"
                        )
                    ],
                    [InlineKeyboardButton("Close", callback_data="closec")],
                ]
            ),
        )

    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


@Client.on_message(filters.private & filters.command("usettings"))
async def urlsetti_(bot, update):
    user_id = update.from_user.id
    
    yfilter = await db.get_yfilter(user_id)
    tguploads = await db.get_tgpremium(user_id)
    for_media = 1969772008
    for_url = 1969772008

    try:
        set_tings = await update.reply(
            "**Processing....**", reply_to_message_id=update.id
        )
    except Exception as e:
        print(e)
        return
    try:
        await set_tings.edit(
            text="⚙️ **Config Bot Settings**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{'🔊 Trimmer Codec : Copy' if (await db.get_trimming_proc(id=Config.OWNER_ID)) is True else '🔊 Trimmer Codec : Default'}",
                            callback_data="trimming_proc",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"📁 Media Functions : {'On' if (await db.get_mediafunctions(id=Config.OWNER_ID)) is True else 'Off'}",
                            callback_data="usmediaf",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"🔗 URL Functions : {'On' if (await db.get_urlfunctions(id=Config.OWNER_ID)) is True else 'Off'}",
                            callback_data="usurlf",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"📁 File Split Size : {tguploads}",
                            callback_data="pstgupload",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"YTDL Filter : {yfilter}", callback_data="filterytdl"
                        )
                    ],
                    [InlineKeyboardButton("Close", callback_data="closec")],
                ]
            ),
        )
        logger.info(
            f"👨‍💼 (/usettings) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


@Client.on_callback_query(filters.regex("^noclo"))
async def scloes_(bot, update):
    try:
        await update.message.delete()
    except:
        pass


@Client.on_callback_query(filters.regex("^filterytdl"))
async def filterytd_(bot, update):
    yfilter = await db.get_yfilter(update.from_user.id)
    if yfilter == "mp4":
        await db.set_yfilter(update.from_user.id, yfilter="webm")
        alert_text = f"YTDL Filter : webm ✅\n\nNow bot will filter webm files Only in (Url Uploader/YouTube Downloader)"
    elif yfilter == "webm":
        await db.set_yfilter(update.from_user.id, yfilter="all")
        alert_text = f"YTDL Filter : all ✅\n\nNow bot will filter all Files in (Url Uploader/YouTube Downloader)"
    elif yfilter == "all":
        await db.set_yfilter(update.from_user.id, yfilter="mp4")
        alert_text = f"YTDL Filter : mp4 ✅\n\nNow bot will filter mp4 Files Only in (Url Uploader/YouTube Downloader)"

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        await USettings(update.message, user_id=update.from_user.id)
    else:
        await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^pstgupload"))
async def pstgupload_(bot, update):
    user_id = update.from_user.id
    tgpremium = await db.get_tgpremium(update.from_user.id)
    if tgpremium == "2GB":
        if Config.SESSION_STRING:
            try:
                check_premium = (await USERBOT.get_me()).is_premium
            except Exception:
                check_premium = False
            if check_premium:
                await db.set_tgpremium(update.from_user.id, tgupload="4GB")
                alert_text = f"📁 File Split Size : 4 GB ✅\n\nNow Bot will Split File Below than 4 GB"
            else:
                await db.set_tgpremium(update.from_user.id, tgupload="2GB")
                alert_text = f"⚠️ Owner does not have Telegram Premium.\n\nSo, 📁 File Split Size : 2 GB ✅\n\nNow Bot will Split File Below than 2 GB"
        else:
            await db.set_tgpremium(update.from_user.id, tgupload="2GB")
            alert_text = f"⚠️ Owner does not have Telegram Premium.\n\nSo, 📁 File Split Size : 2 GB ✅\n\nNow Bot will Split File Below than 2 GB"

    elif tgpremium == "4GB":
        await db.set_tgpremium(update.from_user.id, tgupload="2GB")
        alert_text = (
            f"📁 File Split Size : 2 GB ✅\n\nNow Bot will Split File Below than 2 GB"
        )

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass

    await USettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^trimming_proc"))
async def trimming_proc_(bot, update):
    trimming_proc = await db.get_trimming_proc(update.from_user.id)
    if trimming_proc is True:
        await db.set_trimming_proc(update.from_user.id, trimming_proc=False)
        alert_text = f"🔊 Trimmer Codec : Default\n\n⚠️ It's not for users"
    elif trimming_proc is False:
        await db.set_trimming_proc(update.from_user.id, trimming_proc=True)
        alert_text = f"🔊 Trimmer Codec : Copy\n\n⚠️ It's not for users"

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await USettings(update.message, user_id=update.from_user.id)


# ------------- Main Settings ------------#
@Client.on_callback_query(filters.regex("^usurlf"))
async def seturl_(bot, update):

    if update.from_user.id not in Config.AUTH_USERS:
        alert_text = f"⚠️ This Setting is Only for Owner"
        try:
            await update.answer(alert_text, show_alert=True)
        except:
            pass
        return
   # usr_id = 1969772008
    usr_id = Config.OWNER_ID
    urlsf = await db.get_urlfunctions(usr_id)
    if urlsf is True:
        await db.set_urlfunctions(usr_id, urlsf=False)
        alert_text = f"🔗 URL Functions Desabled ❌"
    elif urlsf is False:
        await db.set_urlfunctions(usr_id, urlsf=True)
        alert_text = f"🔗 URL Functions Enabled ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        await USettings(update.message, user_id=update.from_user.id)
    else:
        await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^usmediaf"))
async def setmediaf_(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        alert_text = f"⚠️ This Setting is Only for Owner"
        try:
            await update.answer(alert_text, show_alert=True)
        except:
            pass
        return
    
    usr_id = Config.OWNER_ID
    mediasf = await db.get_mediafunctions(usr_id)
    if mediasf is True:
        await db.set_mediafunctions(usr_id, mediasf=False)
        alert_text = f"📁 Media Functions Desabled ❌"
    elif mediasf is False:
        await db.set_mediafunctions(usr_id, mediasf=True)
        alert_text = f"📁 Media Functions Enabled ✅"

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        await USettings(update.message, user_id=update.from_user.id)
    else:
        await OpenSettings(update.message, user_id=update.from_user.id)
