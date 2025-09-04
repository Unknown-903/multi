import asyncio
import datetime
import logging
import os
import time

from pyrogram import Client, enums, filters
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


@Client.on_callback_query(filters.regex("^mvshots"))
async def manual_shots_(c, m):
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

    valid_positions = []
    invalid_positions = []
    manual_shots = 10
    if reply_msg.video:
        try:
            files_video = m.message.reply_to_message
            medias = files_video.video
            duration = medias.duration
        except Exception as e:
            await m.message.reply(
                f"**⚠️ Error : **{e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if duration < 6:
            await m.message.reply(
                f"⚠️ **Error** : Duration is less than 6 Sec\n\n👉 __For Screenshot Generation, Video length should be minimum 6 sec__",
                reply_to_message_id=reply_msg.id,
            )                  
            return

        PROCESS_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            manual_shots = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ Total Duration - {datetime.timedelta(seconds=duration)} ({duration}s)\n\nNow send your list of seconds separated by `,`(comma).\nEx: `5,10,15,20,40`.\nThis will generate screenshots at 5, 10, 15, 20, and 40 seconds.\n\n**None :** The list can have a maximum of 10 valid positions",
                    reply_markup=PROCESS_CANCEL,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await manual_shots.delete()
                await manual_shots.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.message.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await m.message.reply(
                f"⚠️ Error : Process Time Out",
                reply_to_message_id=reply_msg.id,
            )
            return

        if manual_shots.text == "Cancel":
            await m.message.reply(
                f"Process Cancelled ✅",
                reply_to_message_id=reply_msg.id,
            )
            return
        else:
            manual_shots = manual_shots.text

        try:
            raw_user_input = [int(i.strip()) for i in manual_shots.split(",")]
        except Exception as e:
            await m.message.reply(
                f"⚠️ **Error** : {e}\n\nPlease follow this format 👇\n\nDuration List Separate by Comma (,) \nFor Example 👉 `5,10,15,20,40`",
                reply_to_message_id=reply_msg.id,
            )
            return

        for pos in raw_user_input:
            if 0 > pos > duration:
                invalid_positions.append(str(pos))
            else:
                valid_positions.append(pos)
    
        if not valid_positions:
            await m.message.reply(
                f"⚠️ **Error** Invalid positions are {valid_positions}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if len(valid_positions) > 10:
            await m.message.reply(
                f"⚠️ **Error** : Send below than 10\n\n👉 You sent for {len(valid_positions)} screenshots",
                reply_to_message_id=reply_msg.id,
            )
            return

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
    if reply_msg.video:
        pass
    else:
        PROCESS_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            manual_shots = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ Total Duration - {datetime.timedelta(seconds=duration)} ({duration}s)\n\nNow send your list of seconds separated by `,`(comma).\nEx: `5,10,15,20,40`.\nThis will generate screenshots at 5, 10, 15, 20, and 40 seconds.\n\n**None :** The list can have a maximum of 10 valid positions",
                    reply_markup=PROCESS_CANCEL,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await manual_shots.delete()
                await manual_shots.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.message.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await clear_server(user_id, input)
            await msg_edit(msg, f"⚠️ Process Time Out")
            return

        if manual_shots.text == "Cancel":
            await clear_server(user_id, input)
            await msg_edit(msg, f"Process Cancelled  ✅")
            return
        else:
            manual_shots = manual_shots.text

        try:
            raw_user_input = [int(i.strip()) for i in manual_shots.split(",")]
        except Exception as e:
            await clear_server(user_id, input)
            print(e)
            await msg_edit(
                msg,
                f"⚠️ **Error** : {e}\n\nPlease follow this format 👇\n\nDuration List Separate by Comma (,) \nFor Example 👉 `5,10,15,20,40`",
            )
            return

        for pos in raw_user_input:
            if 0 > pos > duration:
                invalid_positions.append(str(pos))
            else:
                valid_positions.append(pos)
    
        if not valid_positions:
            await clear_server(user_id, input)
            await msg_edit(msg, f"⚠️ **Error** Invalid positions are {valid_positions}")
            return

        if len(valid_positions) > 10:
            await clear_server(user_id, input)
            await msg_edit(
                msg,
                f"⚠️ **Error** : Send below than 10\n\n👉 You sent for {len(valid_positions)} screenshots",
            )
            return

    if len(invalid_positions) >= 1:
        INVALID_POSITION = "Found {invalid_positions_count} invalid positions ({invalid_positions}).\n\nGenerating screenshots after ignoring these!."
        txt = INVALID_POSITION.format(
            invalid_positions_count=len(invalid_positions),
            invalid_positions=", ".join(invalid_positions),
        )
        await update.message.reply(txt, reply_to_message_id=reply_msg.id)
        #await clear_server(user_id, input)
        #return

    else:
        try:
            msg = await msg.edit(f"**Generating Screenshots....**")
        except:
            await delete_msg(msg)
            try:
                msg = await m.message.reply(
                    "**Generating Screenshots....**",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, input)
                logger.info(
                    f" ⚠️⚠️ can't send bco message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
                return

    screenshots = []

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

    logger.info(
        "Generating screenshots at positions %s from location: %s for %s",
        valid_positions,
        input,
        m.message.chat.id,
    )

    screenshot_dir = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}"
    if not os.path.isdir(screenshot_dir):
        os.makedirs(screenshot_dir)

    for i, sec in enumerate(valid_positions):
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
                    current=i + 1, total=len(valid_positions)
                )
            )
        except FloodWait as f:
            asyncio.sleep(f.x)
            msg = await msg.edit(
                "`{current}` of `{total}` Screenshots Generated ✅".format(
                    current=i + 1, total=len(valid_positions)
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
                count=len(valid_positions), total_count=len(screenshots)
            )
        )
    except:
        await delete_msg(msg)
        try:
            msg = await m.message.reply(
                "{count} Screenshots\n\n**Uploading....**".format(
                    count=len(valid_positions), total_count=len(screenshots)
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
            f" Manual Screenshots Generated ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        await clear_server(user_id, input, thumbnail_file, screenshot_dir)
        print(e)
        await msg_edit(msg, f"**Error** : {e}")
        return

    await delete_msg(msg)

    await clear_server(user_id, input, thumbnail_file, screenshot_dir)
