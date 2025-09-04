import asyncio
import io
import logging
import os
import time

from pyrogram import Client, enums, filters

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg, msg_edit

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def get_media_info(video_file):
    file_genertor_command = [
        "ffprobe",
        "-i",
        video_file,
        "-v",
        "quiet",
        "-of",
        "json",
        "-show_streams",
        "-show_format",
        "-show_chapters",
        "-show_programs",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout


@Client.on_callback_query(filters.regex("^fprobe"))
async def fprobe_(bot, update):
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
        await bot.download_media(
            message=reply_msg,
            file_name=saved_file_path,
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
                await clear_server(user_id, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

    else:
        saved_file_path = reply_msg.text
        try:
            bc = await bot.send_message(
                chat_id=update.message.chat.id,
                text="🔗 URL Recived ",
                reply_to_message_id=reply_msg.id,
            )
        except Exception:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return
        COUNT.append(user_id)

    try:
        cd = await bc.edit(f"**Getting Info....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**Getting Info....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    try:
        media_info = await get_media_info(saved_file_path)
        logger.debug(media_info)
        media_info_file = io.BytesIO()
        media_info_file.name = "fprobe.json"
        media_info_file.write(media_info)
    except Exception as e:
        print(e)
        await clear_server(user_id, saved_file_path)
        await msg_edit(cd, f"⚠️ **Error** : {e}")
        return

    try:
        await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    except:
        pass
    try:
        await update.message.reply_document(
            document=media_info_file, quote=True, reply_to_message_id=reply_msg.id
        )
        logger.info(
            f"Media Info Generated ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f" ⚠️⚠️ can't send fprobe file To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        print(e)
        return

    await clear_server(user_id, saved_file_path)
    await delete_msg(cd)
    logger.info(
        f"MediaInfo Fprobe Generated ✅ by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
