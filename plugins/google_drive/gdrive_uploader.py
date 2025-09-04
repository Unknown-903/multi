import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg
from plugins.google_drive.google_drive_api import Google_Drive_Upload

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

DOWNLOAD_LOCATION = "./downloads/"


@Client.on_callback_query(filters.regex("^updrive"))
async def upr_drive(bot, update):
    UPLOAD_TYPES = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Google Drive Uploader", callback_data="apidrive"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )
    aa = "✶ **Google Drive Uploader:** Your file will upload in private And **Default folder :** MultiUsageBot\n\n"
    bb = "For Uploading to Google Drive. Click on below button 👇\n\n"

    try:
        await update.message.edit(
            text=f"{aa}{bb}",
            reply_markup=UPLOAD_TYPES,
        )
    except Exception as a:
        logger.info(f"⚠️ WError: {a}")


@Client.on_callback_query(filters.regex("^apidrive"))
async def api_drive(bot, update):
    user_id = update.from_user.id
    gdrive = await db.get_gdrive_status(user_id)
    if gdrive["is_verified"]:
        pass
    else:
        alert_text = f"⚠️ You haven't logged in yet.\n\n👉 So, please /login first"
        try:
            await update.answer(alert_text, show_alert=True)
        except:
            pass
        return
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if os.path.isdir(download_path):
        await update.message.reply(
            "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__",
            reply_to_message_id=reply_msg.id,
        )
        return

    if len(COUNT) > Config.NUMBER:
        ab = await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"**⚠️ Already {Config.NUMBERS} Process Running**\n\n👉 Try again after a few minutes",
            reply_to_message_id=reply_msg.id,
        )
        return
    #  if user_id in COUNT:
    #      ab = await bot.send_message(
    #          chat_id=update.message.chat.id,
    #          text="Already Your 1 Request Processing",
    #          reply_to_message_id=reply_msg.id
    #      )
    #      return

    up_file = None
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )
    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    if reply_msg.media:
        try:
            ab = await update.message.reply(
                "**Downloading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        COUNT.append(user_id)

        progress_bar = Progress(update.from_user.id, bot, ab)
        c_time = time.time()
        up_file = await bot.download_media(
            message=reply_msg,
            file_name=DOWNLOAD_LOCATION,
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Downloading....**", c_time),
        )

        if (
            CANCEL_PROCESS[update.message.chat.id]
            and ab.id in CANCEL_PROCESS[update.message.chat.id]
        ):
            await clear_server(user_id, saved_file_path)
            return

        try:
            bc = await ab.edit(f"File Downloaded Successfully ✅")
        except:
            await delete_msg(ab)
            try:
                bc = await update.message.reply(
                    "File Downloaded Successfully ✅",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, up_file, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

    else:
        await clear_server(user_id, saved_file_path)
        return

    try:
        cd = await bc.edit(f"**Uploading....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**Uploading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, up_file, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    try:
        successful, msg = await Google_Drive_Upload(
            bot, update, up_file
        )  # file.mime_type
        if successful:
            try:
                cd = await bc.edit(
                    f"Successfully Uploaded to Gdrive ✅\n\n**Link:** {msg}"
                )
            except:
                await delete_msg(bc)
                try:
                    cd = await update.message.reply(
                        f"Successfully Uploaded to Gdrive ✅\n\n**Link:** {msg}",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    pass
            logger.info(
                f"Successfully Uploaded to Gdrive API ✅ by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        else:
            await delete_msg(cd)
            try:
                await update.message.reply(f"{msg}", reply_to_message_id=reply_msg.id)
            except:
                pass
    except Exception as a:
        await delete_msg(cd)
        try:
            await update.message.reply(
                f"⚠️ Error f: {a}", reply_to_message_id=reply_msg.id
            )
        except:
            pass
    await clear_server(user_id, up_file, saved_file_path)
