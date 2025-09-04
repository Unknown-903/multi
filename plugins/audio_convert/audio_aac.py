import logging
import os

from pyrogram import Client, filters

from plugins.audio import clear_server, clear_server_two, humanbytes
from config import Config
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
db = Database()

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^acc_audio"))
async def aac_audio(c, m):
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

    limits = CH.audioConvDurLimit
    bool = await CH.audio_dur_limito(c, m, limits)
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

    limits = CH.audioConvDurLimit
    bool = await CH.audio_dur_limit(c, m, msg, duration, input, limits)
    if bool:
        return

    if reply_msg.media:
        files_name = await CH.WE_file_name(reply_msg)

    else:
        files_name = await CH.url_WE_name(input)

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

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.m4a"
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-vn",
        "-c:a",
        "aac",
        "-async",
        "1",
        "-strict",
        "-2",
        "-b:a",
        f"{audio_bitrate}K",
        "-compression_level",
        f"{0}",
        output_directory,
    ]
    texts = CH.converting_txt
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

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        await CH.delete_message(sticker)
        return

    try:
        captions = (
            "File Name : "
            + new_file_name
            + ".m4a"
            + f"\n\nBit Rate : {audio_bitrate} kbps\nFile Size : {humanbytes(output_size)}"
        )
    except:
        captions = "File Name : " + new_file_name + ".m4a"

    ft = "Audio Converted to AAC ✅ "
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

    await CH.audio_upload(c, m, msg, input, output, duration, captions, ft)
    await CH.waiting_time(c, m)
