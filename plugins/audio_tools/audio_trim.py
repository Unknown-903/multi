import logging
import os
import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from plugins.audio import clear_server, clear_server_two, humanbytes
from config import Config
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
db = Database()

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^trimaud"))
async def audio_trimmer(c, m):
    await CH.delete_message(m.message)
    reply_msg = m.message.reply_to_message    
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

    if (await db.get_auto_rename(m.from_user.id)) is True:
        texts = f"**Now Send Name of Output Audio**"
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

        bool, real_audio = await CH.file_download(c, m, msg, input)
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

    STARTING_TIME = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    try:
        start_time = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text=f"**Total Audio duration: ** `{datetime.timedelta(seconds=duration)}`\n\n**✶ Send me Start Time of Audio**",
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
        await clear_server(m.from_user.id, input)
        await CH.edit_msg(bc, f"⚠️ Process Time Out")
        return

    if start_time.text == "Cancel":
        await clear_server(m.from_user.id, input)
        await CH.edit_msg(bc, f"Process Cancelled  ✅")
        return
    else:
        start_time = f"{start_time.text}"

    logger.info(
        f"Audio start time is 👉 {start_time} For user {m.from_user.id} @{m.from_user.username}"
    )
    ENDING_TIME = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    try:
        end_time = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text=f"**Total Audio duration: ** `{datetime.timedelta(seconds=duration)}`\n\nStart Time:  `{start_time}`\nEnd Time: ..........\n\n**✶ Send me End Time of Audio**",
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
        await clear_server(m.from_user.id, input)
        await CH.edit_msg(bc, f"⚠️ Process Time Out")
        return

    if end_time.text == "Cancel":
        await clear_server(m.from_user.id, input)
        await CH.edit_msg(bc, f"Process Cancelled  ✅")
        return
    else:
        end_time = f"{end_time.text}"

    logger.info(
        f"Audio End time is 👉 {end_time} For user {m.from_user.id} @{m.from_user.username}"
    )
    
    if reply_msg.media:
        try:
            media = reply_msg.video or reply_msg.document or reply_msg.audio
            description_ = media.file_name
            if "." in description_:
                try:
                    splitit = description_.split(".")
                    extension = splitit[-1]
                except:
                    extension = "mp3"
            else:
                extension = "mp3"
            files_name = os.path.splitext(description_)[0]  # +'.mp4'
        except:
            files_name = "Default_Name"
            extension = "mp3"
    else:
        try:
            file_name = os.path.basename(saved_file_path)
            extension = "mp3"
            files_name = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            files_name = "Default_Name"
            extension = "mp3"

    if (await db.get_auto_rename(m.from_user.id)) is True:
        try:
            files_name = f"{cfile_name}"
        except:
            files_name = "Default_Name"

    new_file_name = files_name

    sticker = await CH.simple_sticker_send(c, m)

    try:
        audio_bitrate = await db.get_mainquality_a(m.from_user.id)
    except:
        audio_bitrate = 128

    AUDIO_EXTENSIONS = ["aac", "m4a", "mp3", "ac3","wav", "flac", "opus", "wmv", "ogg"]
    if extension.lower() in AUDIO_EXTENSIONS:
        pass
    else:
        extension = "mp3"

    if (extension.lower() == "m4a") or (extension.lower() == "aac"):
        extension = "mp3"
        output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.{extension.lower()}"
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-ss",
            f"{start_time}",
            "-to",
            f"{end_time}",
            "-b:a",
            f"{audio_bitrate}K",
            output_directory,
        ]
    else:
        output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.{extension.lower()}"
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-ss",
            f"{start_time}",
            "-to",
            f"{end_time}",
            "-acodec",
            "copy",
            "-b:a",
            f"{audio_bitrate}K",
            output_directory,
        ]
    texts = "**Trimming Audio File....**"
    bool, output, msg = await CH.command_execute(c, m, msg, commands, output_directory, duration, texts)
    if bool:
        await CH.delete_message(sticker)
        await clear_server(m.from_user.id, input, output)
        return

    if output is None:
        await CH.delete_message(sticker)
        await clear_server(m.from_user.id, input, output)
        texts = f"⚠️ **Error** : Something Went Wrong!!!\n\n👉 Resend your file And Try Again"        
        await CH.edit_msg(msg, texts)
        return

    bool, tduration = await CH.find_duration(m, msg, output)
    if bool:
        await clear_server_two(input)
        return

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        await CH.delete_message(sticker)
        return

    try:
        captions = (
            "File Name : "
            + new_file_name
            + f".{extension}"
            + f"\n\nFile Size : {humanbytes(output_size)}\nBit Rate : {audio_bitrate} kbps\nTrimmed - {start_time} To {end_time}"
        )
    except:
        captions = "File Name : " + new_file_name + f".{extension}"

    ft = "Audio Trimmed ✅ "
    selected_format = "Others"
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(sticker, msg)
        try:
            await media_uploader(c, m, output, captions, ft)
        except:
            pass
        await clear_server(m.from_user.id, input, output)
        return

    await CH.delete_message(sticker)

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(output)
        return

    await CH.audio_upload(c, m, msg, input, output, tduration, captions, ft)
    await CH.waiting_time(c, m)
