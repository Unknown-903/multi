import logging
import os

from pyrogram import Client, filters

from config import Config
from plugins.audio import clear_server, clear_server_two, humanbytes
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^reorderst"))
async def videoreoder_(c, m):
    await CH.delete_message(m.message)
    reply_msg = m.message.reply_to_message   
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

    try:
        file_audio = m.message.reply_to_message
        media = file_audio.audio or file_audio.document or file_audio.video
        files_name = media.file_name
        if "." in files_name:
            try:
                splited = files_name.split(".")
                extensions = splited[-1]
            except:
                extensions = "mkv"
        else:
            extensions = "mkv"
        files_name = os.path.splitext(files_name)[0]  # +'.mp4'

    except:
        files_name = "Default_Name"
        extensions = "mkv"


    if (await db.get_auto_rename(m.from_user.id)) is True:
        try:
            files_name = f"{cfile_name}"
        except:
            files_name = "Default_Name"

    VIDEO_EXTENSIONS = ["mp4", "mkv"]
    if extensions.lower() in VIDEO_EXTENSIONS:
        pass
    else:
        extensions = "mkv"

    new_file_name = f"{files_name}.{extensions}"

    sticker = await CH.simple_sticker_send(c, m)

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}"
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-map",
        "0:v:0",
        "-map",
        "0:a",
        "-c",
        "copy",
        output_directory,
    ]
    texts = CH.converting_txt
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

    captions = new_file_name
    ft = "Video Reordered ✅ "
    premium_upload = CH.U4GB_VReOrder
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(sticker, msg)
        try:
            await media_uploader(c, m, output, captions, ft, premium_upload)
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

    await CH.video_upload(c, m, msg, input, output, duration, captions, ft)
    await CH.waiting_time(c, m)
