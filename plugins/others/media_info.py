import asyncio
import logging
import os
import time

from html_telegraph_poster import TelegraphPoster
from pyrogram import Client, filters

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg, msg_edit

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def get_media_info(video_file):
    file_genertor_command = [
        "mediainfo",
        video_file,
        "--Output=HTML",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    output_text = stdout.decode()  # .strip()
    output_error = stderr.decode()
    return output_text, output_error


@Client.on_callback_query(filters.regex("^infomedia"))
async def infomedia_(bot, update):
    await delete_msg(update.message)
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
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

    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.audio or file_video.document
            description_ = media.file_name
        except:
            description_ = "Default_Name.mkv"

    else:
        try:
            description_ = os.path.basename(saved_file_path)
        except:
            description_ = "Default_Name.mkv"

    try:
        saved_file_path = Config.DOWNLOAD_LOCATION + "/" + description_
    except:
        saved_file_path = Config.DOWNLOAD_LOCATION + "/" + "Default_Name.mkv"

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
        file_video = update.message.reply_to_message
        media = file_video.video or file_video.audio or file_video.document
        description_ = media.file_name
    except:
        description_ = " "

    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.document or file_video.audio
            description_ = media.file_name
        except:
            description_ = "Default_Name"

    else:
        try:
            description_ = os.path.basename(saved_file_path)
        except:
            description_ = "Default_Name"

    try:
        media_info = None
        output_error = None
        media_info, output_error = await get_media_info(saved_file_path)
    except Exception as e:
        print(e)
        await clear_server(user_id, saved_file_path)
        await msg_edit(cd, f"⚠️ **Error** : {output_error}")
        return

    try:
        client = TelegraphPoster(use_api=True)
        client.create_api_token("Mediainfo")
        page = client.post(
            title="@DKBOTZ",
            author=f"@DKBOTZ",
            author_url=f"https://t.me/DKBOTZ",
            text=media_info,
        )
        show_to = page["url"]
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        await msg_edit(cd, f"⚠️ **Error** : {e}")
        return

    try:
        ef = await cd.edit(f"**MediaInfo of** `{description_}` 👇\n\n{show_to}")
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                "**MediaInfo of** `{description_}` 👇\n\n{show_to}",
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    await clear_server(user_id, saved_file_path)
