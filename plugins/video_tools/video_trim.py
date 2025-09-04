import asyncio
import datetime
import logging
import os
import pyromod 
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import Config
from plugins.audio import clear_server, clear_server_two, humanbytes
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
from plugins.audio_helper import Ranjan
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@Client.on_callback_query(filters.regex("^opcut"))
async def trimmerv(c, m):
    await CH.delete_message(m.message)
    reply_msg = m.message.reply_to_message   
    user_id = m.from_user.id
    msg = None
    thumb = None

    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

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
                f"⚠️ **Error** : Duration is less than 1 Sec\n\n👉 __For Trimming Video, Video length should be minimum 6 sec__",
                reply_to_message_id=reply_msg.id,
            )                  
            return

        STARTING_TIME = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            start_time = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\n**✶ Send me Start Time of video**",
                    reply_markup=STARTING_TIME,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await start_time.delete()
                await start_time.request.delete()
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
 
        if start_time.text == "Cancel":
            await m.message.reply(
                f"Process Cancelled ✅",
                reply_to_message_id=reply_msg.id,
            )
            return
        else:
            start_time = f"{start_time.text}"

        logger.info(
            f"Video start time is 👉 {start_time} For user {m.from_user.id} @{m.from_user.username}"
        )
        ENDING_TIME = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            end_time = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\nStart Time:  `{start_time}`\nEnd Time: ..........\n\n**✶ Send me End Time of video**",
                    reply_markup=ENDING_TIME,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await end_time.delete()
                await end_time.request.delete()
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

        if end_time.text == "Cancel":
            await m.message.reply(
                f"Process Cancelled ✅",
                reply_to_message_id=reply_msg.id,
            )
            return
        else:
            end_time = f"{end_time.text}"

        logger.info(
            f"Video End time is 👉 {end_time} For user {m.from_user.id} @{m.from_user.username}"
        )

    extension = None
    if (await db.get_auto_rename(m.from_user.id)) is True:
        texts = f"**Now Send Name of Output Video**"
        bool, cfile_name = await CH.first_ask_name(c, m, texts)
        if bool:
            return

    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
        os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

    new_file_name = "Default_Name"
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

    bool, duration = await CH.find_duration(m, msg, input)
    if bool:
        return

    if duration < 6:
        await clear_server(user_id, input)
        await msg_edit(
            msg,
            "⚠️ For Trimming Video minimum Duration should be at least 6 Seconds",
        )
        return

    if reply_msg.video:
        pass
    else:
        STARTING_TIME = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            start_time = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\n**✶ Send me Start Time of video**",
                    reply_markup=STARTING_TIME,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await start_time.delete()
                await start_time.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.message.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await clear_server(user_id, input)
            await msg_edit(bc, f"⚠️ Process Time Out")
            return
 
        if start_time.text == "Cancel":
            await clear_server(user_id, input)
            await msg_edit(msg, f"Process Cancelled  ✅")
            return
        else:
            start_time = f"{start_time.text}"

        logger.info(
            f"Video start time is 👉 {start_time} For user {m.from_user.id} @{m.from_user.username}"
        )
        ENDING_TIME = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            end_time = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\nStart Time:  `{start_time}`\nEnd Time: ..........\n\n**✶ Send me End Time of video**",
                    reply_markup=ENDING_TIME,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await end_time.delete()
                await end_time.request.delete()
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

        if end_time.text == "Cancel":
            await clear_server(user_id, input)
            await msg_edit(msg, f"Process Cancelled  ✅")
            return
        else:
            end_time = f"{end_time.text}"

        logger.info(
            f"Video End time is 👉 {end_time} For user {m.from_user.id} @{m.from_user.username}"
        )
    if reply_msg.media:
        try:
            media_file = m.message.reply_to_message
            media = media_file.audio or media_file.document or media_file.video
            files_name = media.file_name
            if "." in files_name:
                try:
                    splited = files_name.split(".")
                    extensions = splited[-1]
                except:
                    extension = None
            else:
                extension = None
            files_name = os.path.splitext(files_name)[0]  # +'.mp4'

        except:
            files_name = "Default_Name"
            extension = None
    else:
        try:
            files_name = os.path.basename(input)
            extension = None
            files_name = os.path.splitext(files_name)[0]  # +'.mp4'
        except:
            files_name = "Default_Name"
            extension = None

    VIDEO_EXTENSIONS = ["mp4", "mkv"]
    if extension is None:
        extension = "mkv"
    if extension.lower() in VIDEO_EXTENSIONS:
        pass
    else:
        extension = "mkv"

    if (await db.get_auto_rename(m.from_user.id)) is True:
        try:
            files_name = f"{cfile_name}"
        except:
            files_name = "Default_Name"

    new_file_name = f"{files_name}.{extension.lower()}"

    sticker = await CH.simple_sticker_send(c, m)

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}"
    subtitle_option = await Ranjan.fix_subtitle_codec(input)
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-ss",
        f"{start_time}",
        "-to",
        f"{end_time}",
        "-map",
        "0",
        "-c",
        "copy",
        output_directory,
    ]
    for option in subtitle_option:
        commands.insert(-1, option)
    texts = f"**Please wait. ✂️ Trimming Now....**"
    bool, output, msg = await CH.command_execute(c, m, msg, commands, output_directory, duration, texts)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(output_directory)
        return

    if output is None:
        await CH.delete_message(sticker)
        await clear_server_two(output)
        texts = f"⚠️ **Error** : Something Went Wrong!!!\n\n👉 Resend your file And Try Again"        
        await CH.edit_msg(msg, texts)
        return

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        await CH.delete_message(sticker)
        return

    captions = new_file_name + f"\n\n✂️ Trimmed - {start_time} To {end_time}\n\nVideo Trimmed by Trimmer 1"
    ft = "✂️ Video Trimmed 1 ✅"
    premium_upload = CH.U4GB_Trimmer
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(sticker, msg)
        try:
            await media_uploader(c, m, output, captions, ft, premium_upload)
        except:
            pass
        await clear_server(m.from_user.id, input, output)
        return

    bool, tduration = await CH.find_duration(m, msg, output)
    if bool:
        await clear_server_two(input)
        return

    await CH.delete_message(sticker)

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(output)
        return

    await CH.video_upload(c, m, msg, input, output, tduration, captions, ft)
    await CH.waiting_time(c, m)
