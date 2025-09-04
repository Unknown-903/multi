import datetime
import logging
import os
import random
import time

from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait

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
)
from plugins.audio_helper import Ranjan, take_screen_shot
from plugins.others.playlist_uploader import playlist_uploader
from plugins.processors import media_uploader, Chitranjan as CH

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^viddoc"))
async def viddocs(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    ab = None
    cd = None
    ef = None
    width = 0
    height = 0
    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

    try:
        file_video = m.message.reply_to_message
        media = file_video.video or file_video.audio or file_video.document
        if media.file_name is not None:
            description_ = media.file_name
        else:
            description_ = f"{m.from_user.id}.mkv"
    #    description_ = os.path.splitext(description_)[0] #+'.mp3'
    except:
        description_ = "Default_Name.mkv"

    input = f"{Config.DOWNLOAD_PATH}/{description_}"
    if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
        os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

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

    texts = f"**Converting....**"
    bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
    if bool:
        return

    try:
        duration = await Ranjan.get_duration(input)
    except Exception as e:
        await clear_server(user_id, input)
        print(e)
        await msg_edit(msg, f"⚠️ **Error** : {e}")
        return

    try:
        time_format = datetime.timedelta(seconds=duration)
    except Exception as e:
        await clear_server(user_id, input)
        print(e)
        await msg_edit(msg, f"⚠️ **Error** : Duration not found")
        return

    if duration < 1:
        await clear_server(user_id, input)
        await msg_edit(msg, f"⚠️ **Error** : Duration is Less than 1 Sec")
        return

    if real_video is None:
        await clear_server(user_id, input)
        await msg_edit(msg, f"**Error** : in File_Size")
        return

    try:
        duration = None
        duration = await Ranjan.get_duration(input)
    except Exception as e:
        await clear_server(user_id, input)
        print(e)
        await msg_edit(msg, f"**Error** : {e}")
        return

    if duration is None:
        await clear_server(user_id, input)
        await msg_edit(msg, f"⚠️ **Error** : Duration is None")
        return

    try:
        output_size = os.path.getsize(input)
    except Exception as e:
        await clear_server(user_id, input)
        await msg_edit(msg, f"⚠️ Error occured: {e}")
        logger.info(
            f"⚠️ Error occured: {e}. User {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
        return

    captions = os.path.basename(input)
    ft = "Converted Video to Doc ✅ "
    premium_upload = CH.U4GB_VConverter
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(msg)
        try:
            await media_uploader(c, m, input, captions, ft, premium_upload)
        except:
            pass
        await clear_server(m.from_user.id, input)
        return

    thumb = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                await clear_server(user_id, input, thumb)
                print(e)
                await msg_edit(
                    msg,
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                )
                return

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((90, 90))
                img.save(thumb, "JPEG")
            except:
                pass
        else:
            try:
                thumb = await take_screen_shot(
                    input, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except Exception as e:
                thumb = None

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(thumb)
        return

    try:
        progress_bar = Progress(m.from_user.id, m, msg)
        c_time = time.time()
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        diksha = await c.send_document(
            chat_id=m.message.chat.id,
            document=input,
            caption=captions,
            thumb=thumb,
            force_document=True,
            reply_to_message_id=reply_msg.id,
            progress=progress_bar.ProgressBar,
            progress_args=("Uploading....", c_time),
        )

        if (
            CANCEL_PROCESS[m.message.chat.id]
            and msg.id in CANCEL_PROCESS[m.message.chat.id]
        ):
            await clear_server(user_id, input, thumb)
            return

        await delete_msg(msg)

        if Config.LOG_CHANNEL:
            try:
                cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{m.from_user.first_name}`\n\n🌷 **User Id :** `{m.from_user.id}`\n\n🌷 **User Name :** `@{m.from_user.username}`\n\nVideo Converter Doc to Video"
                )
            except FloodWait:
                await asyncio.sleep(5)
            except Exception as e:
                print(e)
        logger.info(
            f" Video Converted file to video ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        print(e)
        await msg_edit(msg, f"⚠️ **Error** : {e}")

    await clear_server(user_id, input, thumb)
