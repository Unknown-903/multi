import datetime
import logging
import os
import random
import time

from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup
from plugins.progress import Progress
from database.database import Database
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
from plugins.audio_helper import Ranjan, take_screen_shot
from plugins.others.playlist_uploader import playlist_uploader
from config import Config
from plugins.processors import media_uploader, Chitranjan as CH
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^renamerf"))
async def renamerf_(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    msg = None
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

    if (await db.get_asvideos(m.from_user.id)) is True:
        as_video = True
    else:
        as_video = False

    CMN = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    cfile_name = "Default_Name"
    ask_ = await c.ask(
        chat_id=m.message.chat.id,
        text=f"✶ Send me the Name of File with Extension (Ex: .mp4, .mp3, etc)",
        filters=filters.text,
        reply_markup=CMN,
        reply_to_message_id=reply_msg.id,
    )
    try:
        await ask_.delete()
        await ask_.request.delete()
    except:
        pass
    cfile_name = ask_.text

    if cfile_name.lower() == "cancel":
        await m.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        return

    if "." in cfile_name:
        try:
            splitit = cfile_name.split(".")
            extension = splitit[-1]
        except:
            extension = None
    else:
        extension = None

    cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
    cfile_name = cfile_name[:60] # File name reduced

    IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
    if len(cfile_name) > 60:
        long_msg = await m.message.reply(
            IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name)),
            reply_to_message_id=reply_msg.id,
        )
        return

    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
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

    texts = f"Media Downloaded Successfully ✅"
    bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
    if bool:
        return

    try:
        duration = 0
        duration = await Ranjan.get_duration(input)
    except:
        as_video = False

    try:
        time_format = datetime.timedelta(seconds=duration)
    except:
        as_video = False

    try:
        file_audio = m.message.reply_to_message
        media = file_audio.audio or file_audio.document or file_audio.video
        description_ = media.file_name
        if "." in description_:
            try:
                splitit = description_.split(".")
                extensions = splitit[-1]
            except:
                extensions = "mkv"
        else:
            extensions = "mkv"
        description_ = os.path.splitext(description_)[0]  # +'.mp4'

    except:
        description_ = "Default_Name"
        extensions = "mkv"

    if extension is None:
        extension = extensions

    new_file_names = f"{cfile_name}.{extension}"

    try:
        msg = await msg.edit(f"**Renaming....**")
    except:
        await delete_msg(msg)
        try:
            msg = await m.message.reply(
                "**Renaming....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, input)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
            return

    try:
        new_file_name = Config.DOWNLOAD_LOCATION + "/" + new_file_names
        os.rename(real_video, new_file_name)
    except Exception as e:
        await clear_server(user_id, input, new_file_name)
        print(e)
        await msg_edit(msg, f"⚠️ **Error** : {e}")
        return

    try:
        output_size = os.path.getsize(new_file_name)
    except Exception as e:
        await clear_server(user_id, input, new_file_name)
        await msg_edit(msg, f"⚠️ Error occured: {e}")
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    captions = os.path.basename(new_file_name)
    ft = "Video Renamed ✅ "
    premium_upload = CH.U4GB_Renamer
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(msg)
        try:
            await media_uploader(c, m, new_file_name, captions, ft, premium_upload)
        except:
            pass
        await clear_server(m.from_user.id, input, new_file_name)
        return

    thumb = None
    thumbs = None

    try:
        thumbs = await take_screen_shot(
            new_file_name,
            os.path.dirname(new_file_name),
            random.randint(0, duration - 1),
        )
    except:
        as_video = False

    try:
        widths, heights = await Ranjan.get_dimentions(new_file_name)
    except:
        as_video = False

    if as_video:
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
                    await clear_server(user_id, thumb, new_file_name)
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
                    thumb = thumbs
                    width = widths
                    height = heights
                except:
                    as_video = False

    else:
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
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
                try:
                    Image.open(thumb).convert("RGB").save(thumb)
                    img = Image.open(thumb)
                    img.resize((90, 90))
                    img.save(thumb, "JPEG")
                except:
                    pass
            else:
                try:
                    thumb = thumbs
                    width = widths
                    height = heights
                except:
                    thumb = None

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(thumb, new_file_name)
        return

    if as_video:
        try:
            progress_bar = Progress(m.from_user.id, c, msg)
            c_time = time.time()
            try:
                await m.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
            except:
                pass
            diksha = await c.send_video(
                chat_id=m.message.chat.id,
                video=new_file_name,
                caption=captions,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.ProgressBar,
                progress_args=("Uploading....", c_time),
            )

            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server(user_id, input, new_file_name)
                return

            await delete_msg(msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{m.from_user.first_name}`\n\n🌷 **User Id :** `{m.from_user.id}`\n\n🌷 **User Name :** `@{m.from_user.username}`\n\nUsed Video Renamer ✅"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Video Renamed Successfully ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(msg, f"⚠️ **Error** : {e}")

    else:
        try:
            progress_bar = Progress(m.from_user.id, c, msg)
            c_time = time.time()
            try:
                await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            except:
                pass
            diksha = await c.send_document(
                chat_id=m.message.chat.id,
                document=new_file_name,
                caption=captions,
                force_document=True,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.ProgressBar,
                progress_args=("Uploading....", c_time),
            )

            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server(user_id, thumb, new_file_name)
                return

            await delete_msg(msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{m.from_user.first_name}`\n\n🌷 **User Id :** `{m.from_user.id}`\n\n🌷 **User Name :** `@{m.from_user.username}`\n\nUsed Video Renamer ✅"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Video renamed Successfully ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(msg, f"⚠️ **Error** : {e}")

    await clear_server(user_id, thumb, new_file_name)
