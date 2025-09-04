import logging
import os
import asyncio

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from plugins.audio import clear_server, clear_server_two, humanbytes
from config import Config
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
db = Database()

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^apulsator8D"))
async def audio_8D(c, m):
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

    limits = CH.songsEqDurLimit
    bool = await CH.audio_dur_limito(c, m, limits)
    if bool:
        return

    SOUND_TYPE = ReplyKeyboardMarkup(
        [["Sine", "Triangle"], ["Square", "Sawup", "Sawdown"]], resize_keyboard=True
    ) 
    try:
        sound_8D = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text="Choose 8D Sound Type According to your Choice. \n\nModes are Sine, Triangle, Square, Sawup And Sawdown\n\n**Sine & Triangle Mode are my favorite**\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=SOUND_TYPE,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await sound_8D.delete()
            await sound_8D.request.delete()
        except:
            pass
        sound_8D_type = sound_8D.text
    except asyncio.TimeoutError:
        try:
            ccc = await m.message.reply(
               ".", reply_markup=ReplyKeyboardRemove()
            )
            await ccc.delete()
        except:
            pass
        sound_8D_type = "Triangle"
    if sound_8D_type == "Sine":
        sound_8D_type = "sine"
    elif sound_8D_type == "Square":
        sound_8D_type = "square"
    elif sound_8D_type == "Triangle":
        sound_8D_type = "triangle"
    elif sound_8D_type == "Sawup":
        sound_8D_type = "sawup"
    elif sound_8D_type == "Sawdown":
        sound_8D_type = "sawdown"
    else:
        sound_8D_type = "sine"

    REPEAT_TIME = ReplyKeyboardMarkup(
        [["2", "5", "8"], ["10", "20", "25"], ["40", "50", "80"]],
        resize_keyboard=True,
    ) 
    try:
        repeat_num = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text="Choose 8D Sound Mode-Loop repeating Duration in seconds\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=REPEAT_TIME,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await repeat_num.delete()
            await repeat_num.request.delete()
        except:
            pass
        TEXTS_SEC = ["2", "5", "8", "10", "20", "25", "40", "50", "80"]
        if repeat_num.text in TEXTS_SEC:
            repeat_number = repeat_num.text
        else:
            repeat_number = "20"
    except asyncio.TimeoutError:
        try:
            cccc = await m.message.reply(
                ".", reply_markup=ReplyKeyboardRemove()
            )
            await cccc.delete()
        except:
            pass
        repeat_number = "20"

    round_repeat = 1 / int(repeat_number)
    round_repeat = str(round_repeat) 

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

    limits = CH.songsEqDurLimit
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

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.mp3"
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-filter_complex",
        f"apulsator=mode={sound_8D_type}:hz={round_repeat}",
        "-b:a",
        f"{audio_bitrate}K",
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
            + f".mp3"
            + f"\n\nFile Size : {humanbytes(output_size)}\nBit Rate : {audio_bitrate} kbps\n8D Sound Type : {sound_8D_type}-{repeat_number}s"
        )
    except:
        captions = "File Name : " + new_file_name + f".mp3"

    ft = "Audio Converted to 8D ✅ "
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
