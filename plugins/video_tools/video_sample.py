import asyncio
import datetime
import logging
import os

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
import pyromod
from config import Config
from plugins.audio import clear_server, clear_server_two, humanbytes
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
from plugins.audio_helper import Ranjan
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^disampl"))
async def disamplvid(c, m):
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

    SAMPLE_DURATIONS = ReplyKeyboardMarkup(
        [["30", "60", "90"], ["120", "150", "180"], ["Default"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        sample_duration = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text="Select the Duration of Video Sample\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=SAMPLE_DURATIONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await sample_duration.delete()
            await sample_duration.request.delete()
        except:
            pass
        sample_duration = sample_duration.text
    except asyncio.TimeoutError:
        try:
            ccc = await m.message.reply(
                ".", reply_markup=ReplyKeyboardRemove()
             )
            await ccc.delete()
        except:
            pass
        sample_duration = "Cancel"

    if sample_duration == "30":
        sample_duration = "30"
    elif sample_duration == "60":
        sample_duration = "60"
    elif sample_duration == "90":
        sample_duration = "90"
    elif sample_duration == "120":
        sample_duration = "120"
    elif sample_duration == "150":
        sample_duration = "150"
    elif sample_duration == "180":
        sample_duration = "180"
    else:
        sample_duration = "120"

    if sample_duration == "Cancel":
        await m.message.reply(f"⚠️ Process Time out, Resend and try again", reply_to_message_id=reply_msg.id)
        return
    sample_duration = int(sample_duration)

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

    if duration < 180:
        await clear_server(user_id, input)
        await CH.edit_msg(
            msg,
            "⚠️ For Video Sample Generation minimum Duration should be at least 3 minutes",
        )
        return

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

    reduced_sec = duration - int(duration * 10 / 100)
    start_time = Ranjan.get_random_start_at(reduced_sec, sample_duration)

    sticker = await CH.simple_sticker_send(c, m)

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}"
    subtitle_option = await Ranjan.fix_subtitle_codec(input)
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-ss",
        f"{start_time}",
        "-t",
        f"{sample_duration}",
        "-map",
        "0",
        "-c",
        "copy",
        output_directory,
    ]
    for option in subtitle_option:
        commands.insert(-1, option)
    texts = f"**Generating Sample Video....**"
    bool, output, msg = await CH.command_execute(c, m, msg, commands, output_directory, duration, texts)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(output_directory)
        return

    if output is None:
        await CH.delete_message(sticker)
        await clear_server_two(output_directory)
        texts = f"⚠️ **Error** : Something Went Wrong!!!\n\n👉 Resend your file And Try Again"        
        await CH.edit_msg(msg, texts)
        return

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        await CH.delete_message(sticker)
        return

    captions = new_file_name + f"\n\nSample Duration - {sample_duration}s"
    ft = "Video(s) Sample Generated ✅"
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
