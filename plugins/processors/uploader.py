import asyncio
import logging
import os
import random
import shlex
import shutil
import time
import threading 
from typing import List, Tuple, Union

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram import enums
from pyrogram.errors import FloodWait

from config import Config
from plugins.progress import Progress, UpProgress
from main import USERBOT
from plugins.audio import clear_server, clear_server_two, delete_msg, msg_edit, humanbytes
from plugins.audio import CANCEL_PROCESS, TimeFormatter 
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from plugins.audio_helper import Ranjan
from database.database import Database
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

class Uploaders:
    @staticmethod
    async def UpProgress_msg(c, m, msg, texts):
        bool = True
        reply_msg = m.message.reply_to_message
        reply_markup = InlineKeyboardMarkup(
            [
                [                        
                    InlineKeyboardButton(
                        "Progress ⚡",
                        callback_data=f"siupload/{msg.chat.id}/{msg.id}"                                                                   
                    ),
                    InlineKeyboardButton(
                        "Cancel ❌",
                        callback_data=(
                            f"progcancel/{msg.chat.id}/{msg.id}/{m.from_user.id}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        try:
            bc = await msg.edit(f"{texts}", reply_markup=reply_markup)
            bool = False
        except Exception:
            await delete_msg(msg)
            try:
                bc = await m.message.reply(
                    f"{texts}", reply_markup=reply_markup, reply_to_message_id=reply_msg.id
                )
                bool = False
            except Exception:
                bc = None
                bool = True
                logger.info(
                    f" ⚠️⚠️ {texts} can't send message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
        return bool, bc

#---------------- Main Uploader --------#
async def media_uploader(
    bot, update, single_file, captions=None, ft=None, premium_upload=None
):
    reply_msg = update.message.reply_to_message
    try:
        single_file_size = os.path.getsize(single_file)
    except Exception as e:
        await clear_server_two(single_file)
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            f"⚠️ Error occured: {e}", reply_to_message_id=reply_msg.id
        )
        return

    MAX_FILE_SIZE = 1999 * 1024 * 1024  # 1999 MB
    check_premium = False
    if premium_upload.upper() == "YES":
        if single_file_size > MAX_FILE_SIZE:
            if Config.SESSION_STRING:
                try:
                    check_premium = (await USERBOT.get_me()).is_premium
                except Exception as e:
                    check_premium = False
                    logger.info(f"🌟⚠️ Checking Premium Error: {e}")
                if check_premium:
                    MAX_FILE_SIZE = 3999 * 1024 * 1024  # 3999 MB
                    logger.info(f"🌟 Premium User")
                else:
                    MAX_FILE_SIZE = 3999 * 1024 * 1024

    UPLOAD_SIZES = "2 GB"
    tgup_size = await db.get_tgpremium(update.from_user.id)
    if "4GB" == f"{tgup_size}":
        if check_premium:
            UPLOAD_SIZES = "4 GB"
            SPLIT_FILE_SIZE = 3999 * 1024 * 1024  # About 3.6 GB
            ARCHIVE_SPLIT_SIZE = 3999  # About 3.4 GB
        else:
            await db.set_tgpremium(update.from_user.id, tgupload="2GB")
            UPLOAD_SIZES = "2 GB"
            SPLIT_FILE_SIZE = 1900 * 1024 * 1024  # About 1.85 GB
            ARCHIVE_SPLIT_SIZE = 1900  # About 1.6 GB
    else:
        UPLOAD_SIZES = "2 GB"
        SPLIT_FILE_SIZE = 1800 * 1024 * 1024  # About 1.85 GB
        ARCHIVE_SPLIT_SIZE = 1800  # About 1.6 GB

    if single_file_size > MAX_FILE_SIZE:
        if single_file.upper().endswith(("FLAC", "WAV")):
            return await update.message.reply(
                f"Telegram doesn't Support to upload more than {UPLOAD_SIZES} files",
                reply_to_message_id=reply_msg.id,
            )
        split_msg = await update.message.reply(
            f"Telegram doesn't support to upload more than {UPLOAD_SIZES} files\n\nSo, Now Spliting....",
            reply_to_message_id=reply_msg.id,
        )
        if single_file.upper().endswith(
            ("MP4", "MKV", "AVI", "MOV", "WEBM", "M4V", "3GP", "WMV", "MPG")
        ):
            splited_dir = await split_large_files(single_file, SPLIT_FILE_SIZE)
            list_splited = os.listdir(splited_dir)
            list_splited.sort()
            number_of_files = len(list_splited)
            logger.info(list_splited)
            basefilename = os.path.basename(single_file)

            split_msg = await split_msg.edit(
                f"__{basefilename}__ \n\n**Splited Into  {number_of_files} Files**"
            )
            for splited_single_file in list_splited:
                splitedt = "Yes"
                if check_premium:
                    await tp_video_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        captions,
                        ft,
                        splitedt,
                    )
                else:
                    await pvideo_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        captions,
                        ft,
                        splitedt,
                    )

            await delete_msg(split_msg)
            try:
                shutil.rmtree(splited_dir)
            except:
                pass

        else:
            # single_file.endswith((".zip", ".rar", ".tar", ".7z")):
            splited_dir = await split_in_zip(single_file, ARCHIVE_SPLIT_SIZE)
            list_splited = os.listdir(splited_dir)
            list_splited.sort()
            number_of_files = len(list_splited)
            logger.info(list_splited)
            basefilename = os.path.basename(single_file)
            captions = f"{captions}\n\n{basefilename}"
            split_msg = await split_msg.edit(
                f"__{basefilename}__ \n\n**Splited Into  {number_of_files} Files**"
            )
            for splited_single_file in list_splited:
                splitedt = "Yes"
                if check_premium:
                    await tp_document_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        captions,
                        ft,
                        splitedt,
                    )
                else:
                    await pdocument_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        captions,
                        ft,
                        splitedt,
                    )

            await delete_msg(split_msg)
            try:
                shutil.rmtree(splited_dir)
            except:
                pass

    else:
        if check_premium:
            if single_file.upper().endswith(
                ("MP4", "MKV", "AVI", "MOV", "WEBM", "M4V", "3GP", "WMV", "MPG")
            ):
                await tp_video_uploader(
                    bot, update, single_file, captions, ft
                )

            elif single_file.upper().endswith(
                ("WAV", "MP3", "FLAC", "M4A", "AIFF", "OPUS", "OGG", "AAC", "AC3")
            ):
                await tp_audio_uploader(
                    bot, update, single_file, captions, ft
                )

            else:
                await tp_document_uploader(
                    bot, update, single_file, captions, ft
                )
        else:
            if single_file.upper().endswith(
                ("MP4", "MKV", "AVI", "MOV", "WEBM", "M4V", "3GP", "WMV", "MPG")
            ):
                await pvideo_uploader(
                    bot, update, single_file, captions, ft
                )

            elif single_file.upper().endswith(
                ("WAV", "MP3", "FLAC", "M4A", "AIFF", "OPUS", "OGG", "AAC", "AC3")
            ):
                await paudio_uploader(
                    bot, update, single_file, captions, ft
                )

            else:
                await pdocument_uploader(
                    bot, update, single_file, captions, ft
                )

async def improvement(c, m, files, ft):
    if Config.LOG_CHANNEL:
        try:
            cmf2v = await files.copy(chat_id=Config.LOG_CHANNEL)
            await cmf2v.reply_text(
                f"**User Information** :\n\n🌷 **First Name :** `{m.from_user.first_name}`\n\n🌷 **User Id :** `{m.from_user.id}`\n\n🌷 **User Name :** `@{m.from_user.username}`\n\n**Used :** {ft}"
            )
        except FloodWait:
            await asyncio.sleep(5)
        except Exception as e:
            print(e)

# ---------------- Video Uploader -------------#
async def pvideo_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    if (await db.get_asvideos(m.from_user.id)) is True:
        as_video = True
    else:
        as_video = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    duration = 0
    width = 0
    height = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_video = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                await clear_server(
                    m.from_user.id, single_file, thumb
                )
                logger.info(
                    f" ⚠️ Thumbnail Ss Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(msg, f"⚠️ **Thumbnail Ss Error** : {e}")
                return 

        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail Ss2 Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                thumb = None
                as_video = False

    try:
        width, height = await Ranjan.get_dimentions(single_file)
    except Exception as e:
        as_video = False
        thumb = None
        await m.message.reply(
            f"⚠️ **Video Hight Width Error** : {e}", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" ⚠️ V HW Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
        )

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    if as_video:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
        except:
            pass
        try:
            files = await c.send_video(
                chat_id=m.message.chat.id,
                video=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

    else:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            files = await c.send_document(
                chat_id=m.message.chat.id,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##
# ---------------- New Audio Uploader -------------#
async def paudio_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None 
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    if (await db.get_upload_as(update.from_user.id)) is True:
        as_audio = True
    else:
        as_audio = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    duration = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_audio = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None
                as_audio = False
        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None
                as_audio = False

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    if as_audio:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
        except:
            pass
        try:
            files = await c.send_audio(
                chat_id=m.message.chat.id,
                audio=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

    else:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            files = await c.send_document(
                chat_id=m.message.chat.id,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

# ---------------- New Doc Uploader -------------#
async def pdocument_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None 
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    duration = 0
    width = 0
    height = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_video = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None

        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail Ss2 Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                thumb = None

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    try:
        await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    except:
        pass
    try:
        files = await c.send_document(
            chat_id=m.message.chat.id,
            document=single_file,
            caption=caption,
            thumb=thumb,
            force_document=True,
            reply_to_message_id=reply_msg.id,
            progress=progress_bar.uploading_progress,
            progress_args=("Uploading....", c_time),
        )
        if (
            CANCEL_PROCESS[m.message.chat.id]
            and msg.id in CANCEL_PROCESS[m.message.chat.id]
        ):
            await clear_server_two(single_file, thumb)
            return
        await delete_msg(msg)
        await improvement(c, m, files, ft)
        await clear_server_two(single_file, thumb)
        logger.info(
            f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        await clear_server_two(single_file, thumb)
        logger.info(e)
        await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
        ##

# -------------------- CLI -------------------#
async def cli_call(cmd: Union[str, List[str]]) -> Tuple[str, str]:
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    elif isinstance(cmd, (list, tuple)):
        pass
    else:
        return None, None
    process = await asyncio.create_subprocess_exec(
        *cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    with open("test.txt", "w", encoding="UTF-8") as f:
        f.write(stdout)
    return stdout, stderr


async def archive_cli(cmd: Union[str, List[str]]) -> Tuple[str, str]:
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    elif isinstance(cmd, (list, tuple)):
        pass
    else:
        return None, None

    process = await asyncio.create_subprocess_exec(
        *cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, process.returncode


# ---------------- Split Video ---------------#


async def split_large_files(input_file, SPLIT_FILE_SIZE):
    working_directory = os.path.dirname(os.path.abspath(input_file))
    new_working_directory = os.path.join(working_directory, str(time.time()))
    if not os.path.isdir(new_working_directory):
        os.makedirs(new_working_directory)
    if input_file.upper().endswith(
        (
            "MKV",
            "MP4",
            "WEBM",
            "AVI",
            "MOV",
            "OGG",
            "WMV",
            "M4V",
            "TS",
            "MPG",
            "MTS",
            "M2TS",
            "3GP",
        )
    ):
        metadata = extractMetadata(createParser(input_file))
        total_duration = 0
        if metadata.has("duration"):
            total_duration = metadata.get("duration").seconds
        total_file_size = os.path.getsize(input_file)
        minimum_duration = (total_duration / total_file_size) * int(SPLIT_FILE_SIZE)
        minimum_duration = int(minimum_duration)

        start_time = 0
        end_time = minimum_duration
        base_name = os.path.basename(input_file)
        input_extension = base_name.split(".")[-1]

        i = 0
        flag = False

        while end_time <= total_duration:
            parted_file_name = "{}_PART_{}.{}".format(
                str(base_name), str(i).zfill(5), str(input_extension)
            )

            output_file = os.path.join(new_working_directory, parted_file_name)
            logger.info(output_file)
            await cult_small_video(
                input_file, output_file, str(start_time), str(end_time)
            )
            logger.info(f"Start time {start_time}, End time {end_time}, Itr {i}")
            start_time = end_time - 3
            end_time = end_time + minimum_duration
            i = i + 1

            if (end_time > total_duration) and not flag:
                end_time = total_duration
                flag = True
            elif flag:
                break

    try:
        os.remove(input_file)
    except Exception as r:
        logger.error(r)
    return new_working_directory


# ------------------ Spit in Zip --------------#
async def split_in_zip(input_file, ARCHIVE_SPLIT_SIZE):
    if os.path.isfile(input_file):
        working_directory = os.path.dirname(os.path.abspath(input_file))
        new_working_directory = os.path.join(
            working_directory, str(time.time()).replace(".", "")
        )
        if not os.path.isdir(new_working_directory):
            os.makedirs(new_working_directory)
        fname = os.path.basename(input_file)
        size = int(ARCHIVE_SPLIT_SIZE)
        cmd = f'7z a -tzip -mx=0 "{new_working_directory}/{fname}.zip" "{input_file}" -v{size}m '

        _, err, rcode = await archive_cli(cmd)

        if err:
            logger.info(f"Error in zip split {err}")
            return None
        else:
            return new_working_directory

    else:
        return None


async def cult_small_video(video_file, out_put_file_name, start_time, end_time):
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        "-c",
        "copy",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(t_response)
    return out_put_file_name


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


# ----------------------------------------#
# ---------- Premium Video Uploader -------------#
async def tp_video_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None 
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    if (await db.get_asvideos(m.from_user.id)) is True:
        as_video = True
    else:
        as_video = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    duration = 0
    width = 0
    height = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_video = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                await clear_server(
                    m.from_user.id, single_file, thumb
                )
                logger.info(
                    f" ⚠️ Thumbnail Ss Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(msg, f"⚠️ **Thumbnail Ss Error** : {e}")
                return 

        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail Ss2 Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                thumb = None
                as_video = False

    try:
        width, height = await Ranjan.get_dimentions(single_file)
    except Exception as e:
        as_video = False
        thumb = None
        await m.message.reply(
            f"⚠️ **Video Hight Width Error** : {e}", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" ⚠️ V HW Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
        )

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    if as_video:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
        except:
            pass
        try:
            files = await USERBOT.send_video(
                chat_id=Config.PREMIUM_STORE,
                video=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await c.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=files.chat.id,
                    message_id=files.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

    else:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            files = await USERBOT.send_document(
                chat_id=Config.PREMIUM_STORE,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await c.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=files.chat.id,
                    message_id=files.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##
# ---------------- New Audio Uploader -------------#
async def tp_audio_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None 
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    if (await db.get_upload_as(update.from_user.id)) is True:
        as_audio = True
    else:
        as_audio = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    duration = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_audio = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None
                as_audio = False
        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None
                as_audio = False

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    if as_audio:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
        except:
            pass
        try:
            files = await USERBOT.send_audio(
                chat_id=Config.PREMIUM_STORE,
                audio=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await c.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=files.chat.id,
                    message_id=files.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

    else:
        try:
            await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            files = await USERBOT.send_document(
                chat_id=Config.PREMIUM_STORE,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.uploading_progress,
                progress_args=("Uploading....", c_time),
            )
            if (
                CANCEL_PROCESS[m.message.chat.id]
                and msg.id in CANCEL_PROCESS[m.message.chat.id]
            ):
                await clear_server_two(single_file, thumb)
                return
            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await c.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=files.chat.id,
                    message_id=files.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await delete_msg(msg)
            await improvement(c, m, files, ft)
            await clear_server_two(single_file, thumb)
            logger.info(
                f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            logger.info(e)
            await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
            ##

# ---------------- New Doc Uploader -------------#
async def tp_document_uploader(
    c, m, single_file, captions=None, ft=None, splitedt=None
):
    reply_msg = m.message.reply_to_message
    real_name = os.path.basename(single_file)
    try:
        msg = await m.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        logger.error(e)
        return 

    texts = f"**Uploading :** `{real_name}`"
    bool, msg = await Uploaders.UpProgress_msg(c, m, msg, texts)
    if bool:
        await clear_server(update.from_user.id, single_file)
        return

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is not None:
        caption = f"{captions}"
    else:
        caption = ""

    if splitedt is not None:
        caption = f"{caption}\n\n{real_name}"
    else:
        caption = f"{caption}"

    if ft is not None:
        ft = f"{ft}"
    else:
        ft = "."

    duration = 0
    width = 0
    height = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_video = False
        thumb = None
        duration = 0

    thumbnail = None
    if (await db.get_othumb(m.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(m.from_user.id)
        except Exception as e:
            thumbnail = None
            logger.info(
                f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
            )
        if thumbnail is not None:
            try:
                thumb = await c.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await db.set_thumbnail(m.from_user.id, thumbnail=None)

        else:
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                thumb = None

        t_height = 0
        try:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("height"):
                t_height = metadata.get("height")
            else:
                t_height = 0
            Image.open(thumb).convert("RGB").save(thumb)
            img = Image.open(thumb)
            img.resize((320, t_height))
            img.save(thumb, "JPEG")
        except Exception as e:
            logger.info(f"⚠️ Thumbnail H Error: {e}")
            if thumbnail is not None:
                await db.set_thumbnail(m.from_user.id, thumbnail=None)
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumb = await take_screen_shot(
                    single_file,
                    os.path.dirname(thumb),
                    random.randint(0, duration - 1),
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ Thumbnail Ss2 Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                thumb = None

    c_time = time.time()
    progress_bar = UpProgress(c, m, msg)
    try:
        await m.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    except:
        pass
    try:
        files = await USERBOT.send_document(
            chat_id=Config.PREMIUM_STORE,
            document=single_file,
            caption=caption,
            thumb=thumb,
            force_document=True,
            reply_to_message_id=reply_msg.id,
            progress=progress_bar.uploading_progress,
            progress_args=("Uploading....", c_time),
        )
        if (
            CANCEL_PROCESS[m.message.chat.id]
            and msg.id in CANCEL_PROCESS[m.message.chat.id]
        ):
            await clear_server_two(single_file, thumb)
            return
        logger.info(f"🌟 Bot is sending in Private ")
        try:
            await c.copy_message(
                chat_id=m.from_user.id,
                from_chat_id=files.chat.id,
                message_id=files.id,
            )
        except Exception as e:
            logger.info(f"⚠️ Error to send pm: {e}")

        await delete_msg(msg)
        await improvement(c, m, files, ft)
        await clear_server_two(single_file, thumb)
        logger.info(
            f"{ft} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        await clear_server_two(single_file, thumb)
        logger.info(e)
        await msg_edit(msg, f"{caption}\n\n⚠️ {e}")
        ##

