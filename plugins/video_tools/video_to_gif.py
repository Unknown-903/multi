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

@Client.on_callback_query(filters.regex("^gifvideo"))
async def gifvideos(c, m):
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

    NO_SEC = ReplyKeyboardMarkup(
        [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["10"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        gif_secconds = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text="Select the Duration of GIF in Seconds\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=NO_SEC,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await gif_secconds.delete()
            await gif_secconds.request.delete()
        except:
            pass
        gif_secconds = gif_secconds.text
    except asyncio.TimeoutError:
        try:
            ccc = await m.message.reply(
                ".", reply_markup=ReplyKeyboardRemove()
            )
            await ccc.delete()
        except:
            pass
        gif_secconds = "Cancel"
    if gif_secconds == "1":
        gif_secconds = "1"
    elif gif_secconds == "2":
        gif_secconds = "2"
    elif gif_secconds == "3":
        gif_secconds = "3"
    elif gif_secconds == "4":
        gif_secconds = "4"
    elif gif_secconds == "5":
        gif_secconds = "5"
    elif gif_secconds == "6":
        gif_secconds = "6"
    elif gif_secconds == "7":
        gif_secconds = "7"
    elif gif_secconds == "8":
        gif_secconds = "8"
    elif gif_secconds == "9":
        gif_secconds = "9"
    elif gif_secconds == "10":
        gif_secconds = "10"
    else:
        gif_secconds = "2"

    if gif_secconds == "Cancel":
        await m.message.reply(
            "⚠️ Process Time Out, resend and try again",
            reply_to_message_id=reply_msg.id,
        )
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

        if duration > 1800:
            await c.send_message(
                chat_id=m.message.chat.id,
                text=f"⚠️ Send Video which duration is less than 30 Minutes",
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
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\n**✶ Send me Start Time of GIF**",
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

    if (await db.get_auto_rename(m.from_user.id)) is True:
        texts = f"**Now Send Name of Output GIF**"
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
    '''
    if duration < 1800:
        await clear_server(user_id, input)
        await CH.edit_msg(
            msg,
            "⚠️ For creating a gif video length should be less than 30 minutes ",
        )
        return
    '''
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
                    text=f"⏰ **Total Video duration: ** `{datetime.timedelta(seconds=duration)}`\n\n**✶ Send me Start Time of GIF**",
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
            await CH.edit_msg(msg, f"⚠️ Process Time Out")
            return
 
        if start_time.text == "Cancel":
            await clear_server(user_id, input)
            await CH.edit_msg(msg, f"Process Cancelled  ✅")
            return
        else:
            start_time = f"{start_time.text}"

        logger.info(
            f"Video start time is 👉 {start_time} For user {m.from_user.id} @{m.from_user.username}"
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

    if (await db.get_auto_rename(m.from_user.id)) is True:
        try:
            files_name = f"{cfile_name}"
        except:
            files_name = "Default_Name"

    new_file_name = f"{files_name}"

    sticker = await CH.simple_sticker_send(c, m)

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.gif"
    commands = [
        "ffmpeg",
        "-i",
        input,
        "-ss",
        f"{start_time}",
        "-vf",
        "scale=500:-1",
        "-t",
        f"{gif_secconds}",
        "-r",
        "10",
        output_directory,
    ]
    texts = f"**Please wait. Creating a GIF....**"
    bool, output, msg = await CH.command_execute(c, m, msg, commands, output_directory, duration, texts)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(output)
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

    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(sticker, msg)
        await clear_server(m.from_user.id, input, output)
        await m.message.reply(
            f"**⚠️ GIF Size is greater than 2 GB\n\nTelegram doesn't support to upload more than 2 GB files",
            reply_to_message_id=reply_msg.id,
        )
        return

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(output)
        return

    description_ = (
        "File Name : "
        + f"{new_file_name}.gif"
        + f"\n\nGIF Duration **{gif_secconds}** Seconds"
    )

    try:
        progress_bar = Progress(m.from_user.id, c, msg)
        c_time = time.time()
        diksha = await c.send_animation(
            chat_id=m.message.chat.id,
            animation=output,
            caption=description_,
            reply_to_message_id=reply_msg.id,
            progress=progress_bar.ProgressBar,
            progress_args=("Uploading....", c_time),
        )

        if (
            CANCEL_PROCESS[m.message.chat.id]
            and msg.id in CANCEL_PROCESS[m.message.chat.id]
        ):
            await clear_server(user_id, input, output)
            return

        await delete_msg(msg)

        if Config.LOG_CHANNEL:
            try:
                cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{m.from_user.first_name}`\n\n🌷 **User Id :** `{m.from_user.id}`\n\n🌷 **User Name :** `@{m.from_user.username}`\n\nUsed video to gif converter"
                )
            except FloodWait:
                await asyncio.sleep(5)
            except Exception as e:
                print(e)
        logger.info(
            f" Video to gif converted Successfully ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        print(e)
        await CH.edit_msg(msg, f"⚠️ **Error** : {e}")

    await clear_server(user_id, input, output)
    await CH.waiting_time(c, m)
