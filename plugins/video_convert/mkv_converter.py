import logging
import os

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import Config
from plugins.audio import clear_server, clear_server_two, humanbytes
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^convmkv"))
async def mkv_conv(c, m):
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

    CHOICE_BUTTONS = ReplyKeyboardMarkup(
        [["Default Audio", "Multi Audio"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_choice = await c.ask(
            chat_id=m.message.chat.id,
            text=f"**Default Audio:** Convert to mkv with default Audio (Single)\n\n**Multi Audio:** Convert to mkv with Multi Stream (Multi Audio)\n\nNow select Option of Your Choice 👇",
            reply_markup=CHOICE_BUTTONS,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        try:
        #   await ask_choice.delete()
            await ask_choice.request.delete()
        except:
            pass
        ask_choice = ask_choice.text
    except Exception as e:
        await clear_server(m.from_user.id)
        try:
            await m.message.reply(
                "⚠️ Error: {e}",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Error {e} For {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
        return

    if ask_choice == "Default Audio":
        asked_choice = "Default_Audio"
    elif ask_choice == "Multi Audio":
        asked_choice = "Multi_Audio"
    elif ask_choice == "Cancel":
        asked_choice = "Cancel"
    else:
        asked_choice = "Cancel"

    if asked_choice == "Cancel":
        await clear_server(m.from_user.id)
        await m.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
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

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.mkv"
    if asked_choice == "Multi_Audio":
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-map",
            "0",
            "-async",
            "1",
            "-strict",
            "-2",
            "-codec",
            "copy",
            output_directory,
        ]
    else:
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-codec",
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

    captions = files_name + ".mkv"
    ft = "Video Converted to mkv ✅ "
    premium_upload = CH.U4GB_MKV_MP4Convert
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
