import asyncio
import datetime
import logging
import os
import time

from pyrogram import Client, enums, filters
from pyrogram.emoji import *
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import Config
from database.database import Database
from plugins.progress import Progress
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    delete_msg,
    dmsg_edit,
    msg_edit,
    humanbytes,
)
from plugins.audio_helper import Ranjan
from plugins.processors import media_uploader, Chitranjan as CH
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^mvscreenshot"))
async def mscreenshotss_(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    msg = None

    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

    NO_PHOTO = ReplyKeyboardMarkup(
        [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["10"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        no_of_photos = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text="Select the number of screenshots\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=NO_PHOTO,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await no_of_photos.delete()
            await no_of_photos.request.delete()
        except:
            pass
        no_of_photos = no_of_photos.text
    except asyncio.TimeoutError:
        try:
            ccc = await m.message.reply(
                ".", reply_markup=ReplyKeyboardRemove()
            )
            await ccc.delete()
        except:
            pass
        no_of_photos = "Cancel"

    if no_of_photos == "1":
        no_of_photos = "1"
    elif no_of_photos == "2":
        no_of_photos = "2"
    elif no_of_photos == "3":
        no_of_photos = "3"
    elif no_of_photos == "4":
        no_of_photos = "4"
    elif no_of_photos == "5":
        no_of_photos = "5"
    elif no_of_photos == "6":
        no_of_photos = "6"
    elif no_of_photos == "7":
        no_of_photos = "7"
    elif no_of_photos == "8":
        no_of_photos = "8"
    elif no_of_photos == "9":
        no_of_photos = "9"
    elif no_of_photos == "10":
        no_of_photos = "10"
    else:
        no_of_photos = "9"

    if no_of_photos == "Cancel":
        texts = f"⚠️ Process Time out, Resend and try again"
        await m.message.reply(
            f"{texts}", reply_to_message_id=reply_msg.id
        )
        return
    no_of_photos = int(no_of_photos)

    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
        os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

    if reply_msg.media:
        texts = CH.processing_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        texts = CH.downloading_txt
        bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
        if bool:
            return

        await CH.start_counting(m)

        bool, real_video = await CH.file_download(c, m, msg, input)
        if bool:
            return

        texts = f"Media Downloaded Successfully ✅"
        bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
        if bool:
            return

    else:
        input = reply_msg.text
        texts = CH.url_recieved_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        await CH.start_counting(m)
    # ----------------- STARTING ------------------#
    bool, duration = await CH.find_duration(m, msg, input)
    if bool:
        return

    if duration < 6:
        await clear_server(user_id, input)
        await msg_edit(
            msg,
            "⚠️ **Error** : Duration is less than 6 Sec\n\n👉 __For Screenshot Generation, Video length should be minimum 6 sec__",
        )
        return
    # ---------------- Script ---------------------#
    screenshots = []
    num_screenshots = no_of_photos
    reduced_sec = duration - int(duration * 2 / 100)

    ffmpeg_cmd = [
        "ffmpeg",
        "-ss",
        "",  # To be replaced in loop
        "-i",
        input,
        "-vf",
        "scale=1280:-1",
        "-y",
        "-vframes",
        "1",
        "",  # To be replaced in loop
    ]

    # For Equally Spaced Screenshot - screenshot_mode == 0 Else 1 Random
    screenshot_mode = 1  # For Equally Spaced put 0
    screenshot_secs = [
        int(reduced_sec / num_screenshots) * i
        if screenshot_mode == 0
        else Ranjan.get_random_start_at(reduced_sec)
        for i in range(1, 1 + num_screenshots)
    ]

    screenshot_dir = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}"
    if not os.path.isdir(screenshot_dir):
        os.makedirs(screenshot_dir)

    for i, sec in enumerate(screenshot_secs):
        thumbnail_file = os.path.join(screenshot_dir, f"{i+1}.png")
        ffmpeg_cmd[2] = str(sec)
        ffmpeg_cmd[-1] = thumbnail_file
        logger.debug(ffmpeg_cmd)
        output = await Ranjan.run_subprocess(ffmpeg_cmd)
        logger.debug(
            "FFmpeg output\n %s \n %s",
            output[0].decode(),
            output[1].decode(),
        )

        try:
            msg = await msg.edit(
                "`{current}` of `{total}` Screenshots Generated ✅".format(
                    current=i + 1, total=num_screenshots
                )
            )
        except FloodWait as f:
            asyncio.sleep(f.x)
            msg = await msg.edit(
                "`{current}` of `{total}` Screenshots Generated ✅".format(
                    current=i + 1, total=num_screenshots
                )
            )

        if os.path.exists(thumbnail_file):
            screenshots.append(
                InputMediaPhoto(
                    thumbnail_file,
                    caption="Screenshot at {time}".format(
                        time=datetime.timedelta(seconds=sec)
                    ),
                )
            )
            continue

    if not screenshots:
        await clear_server(user_id, input, screenshot_dir, thumbnail_file)
        await msg_edit(msg, f"⚠️ **Error** in Generating Screenshots")
        return

    try:
        msg = await msg.edit(
            "{count} Screenshots\n\n**Uploading....**".format(
                count=num_screenshots, total_count=len(screenshots)
            )
        )
    except:
        await delete_msg(msg)
        try:
            msg = await msg.message.reply(
                "{count} Screenshots\n\n**Uploading....**".format(
                    count=num_screenshots, total_count=len(screenshots)
                ),
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, input, thumbnail_file, screenshot_dir)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
            return

    try:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
        except:
            pass
        await c.send_media_group(
            chat_id=m.message.chat.id,
            media=screenshots,
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f" Screenshots Generated ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        await clear_server(user_id, input, thumbnail_file, screenshot_dir)
        print(e)
        await msg_edit(msg, f"**Error** : {e}")
        return

    await delete_msg(msg)

    await clear_server(user_id, input, thumbnail_file, screenshot_dir)
