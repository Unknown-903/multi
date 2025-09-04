import asyncio
import logging
import os
import random
import shlex
import shutil
import time
from typing import List, Tuple, Union

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram import enums
from pyrogram.errors import FloodWait

from config import Config
from database.database import Database
from helpers.display_progress import Progress, humanbytes
from main import USERBOT
from plugins.audio import clear_server_two, delete_msg
from plugins.audio import CANCEL_PROCESS, TimeFormatter 

from plugins.audio_helper import Ranjan

db = Database()

logger = logging.getLogger(__name__)


async def playlist_uploader(
    bot, update, single_file, selected_format=None, captions=None, premium_upload=None
):
    reply_msg = update.message.reply_to_message
    try:
        single_file_size = os.path.getsize(single_file)
    except Exception as e:
        await clear_server_two(single_file)
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        bad = await update.message.reply(
            f"⚠️ Error occured: {e}", reply_to_message_id=reply_msg.id
        )
        return bad

    MAX_FILE_SIZE = 1999 * 1024 * 1024  # 1999 MB
    check_premium = False
    if premium_upload == "Yes":
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
                    MAX_FILE_SIZE = 1999 * 1024 * 1024

    UPLOAD_SIZES = "2 GB"
    tgup_size = await db.get_tgpremium(update.from_user.id)
    if "4GB" == f"{tgup_size}":
        if check_premium:
            UPLOAD_SIZES = "4 GB"
            SPLIT_FILE_SIZE = 3600 * 1024 * 1024  # About 3.6 GB
            ARCHIVE_SPLIT_SIZE = 3400  # About 3.4 GB
        else:
            await db.set_tgpremium(update.from_user.id, tgupload="2GB")
            UPLOAD_SIZES = "2 GB"
            SPLIT_FILE_SIZE = 1700 * 1024 * 1024  # About 1.85 GB
            ARCHIVE_SPLIT_SIZE = 1600  # About 1.6 GB
    else:
        UPLOAD_SIZES = "2 GB"
        SPLIT_FILE_SIZE = 1700 * 1024 * 1024  # About 1.85 GB
        ARCHIVE_SPLIT_SIZE = 1600  # About 1.6 GB

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
                if check_premium:
                    await tp_video_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        selected_format,
                        captions,
                    )
                else:
                    await pvideo_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        selected_format,
                        captions,
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

            split_msg = await split_msg.edit(
                f"__{basefilename}__ \n\n**Splited Into  {number_of_files} Files**"
            )
            for splited_single_file in list_splited:
                if check_premium:
                    await tp_document_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        selected_format,
                        captions,
                    )
                else:
                    await pdocument_uploader(
                        bot,
                        update,
                        os.path.join(splited_dir, splited_single_file),
                        selected_format,
                        captions,
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
                    bot, update, single_file, selected_format, captions
                )

            elif single_file.upper().endswith(
                ("WAV", "MP3", "FLAC", "M4A", "AIFF", "OPUS", "OGG", "AAC", "AC3")
            ):
                await tp_audio_uploader(
                    bot, update, single_file, selected_format, captions
                )

            else:
                await tp_document_uploader(
                    bot, update, single_file, selected_format, captions
                )
        else:
            if single_file.upper().endswith(
                ("MP4", "MKV", "AVI", "MOV", "WEBM", "M4V", "3GP", "WMV", "MPG")
            ):
                await pvideo_uploader(
                    bot, update, single_file, selected_format, captions
                )

            elif single_file.upper().endswith(
                ("WAV", "MP3", "FLAC", "M4A", "AIFF", "OPUS", "OGG", "AAC", "AC3")
            ):
                await paudio_uploader(
                    bot, update, single_file, selected_format, captions
                )

            else:
                await pdocument_uploader(
                    bot, update, single_file, selected_format, captions
                )


# ---------------- Video Uploader -------------#
async def pvideo_uploader(
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)
    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    if (await db.get_asvideos(update.from_user.id)) is True:
        as_video = True
    else:
        as_video = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"

    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**File Name :** `{real_name}`\n\n**File Size :** {output_size}"

    elif selected_format == "Others":
        caption = f"`{real_name}`"

    else:
        caption = f"`{real_name}`\n\nVideo Quality : {selected_format}"

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

    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None
                as_video = False

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, 320))
                img.save(thumb, "JPEG")
            except:
                thumb = None
                as_video = False
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None
                as_video = False

        try:
            width, height = await Ranjan.get_dimentions(thumb)
        except:
            as_video = False
            thumb = None

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)

    if as_video:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
        except:
            pass
        try:
            await bot.send_video(
                chat_id=update.message.chat.id,
                video=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass

    else:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            await bot.send_document(
                chat_id=update.message.chat.id,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass


# --------------- Audio Uploader -------------#
async def paudio_uploader(
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)

    if (await db.get_upload_as(update.from_user.id)) is True:
        as_audio = True
    else:
        as_audio = False

    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""
        as_audio = False

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"
    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`\n\n**Audio Size :** {output_size}"

    elif selected_format == "Others":
        caption = f"`{real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**Audio Name :** `{real_name}`\n\n{captions}**Audio Size :** {output_size}"

    else:
        caption = f"`{real_name}`\n\n**Audio Size :** {output_size}\n**Audio Quality :** {selected_format}"

    duration = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_audio = False
        thumb = None
        duration = 0

    thumb = None
    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None
                as_audio = False

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((90, 90))
                img.save(thumb, "JPEG")
            except:
                thumb = None
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None
                as_audio = False

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)
    if as_audio:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
        except:
            pass
        try:
            await bot.send_audio(
                chat_id=update.message.chat.id,
                audio=single_file,
                caption=caption,
                duration=duration,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass

    else:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            await bot.send_document(
                chat_id=update.message.chat.id,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass


# ------------- Document Uploader -------------#
async def pdocument_uploader(
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)
    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"
    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**File Name :** `{real_name}`\n\n{captions}"

    else:
        caption = f"`{real_name}`"

    duration = 0
    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        thumb = None
        duration = 0
    thumb = None
    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, 320))
                img.save(thumb, "JPEG")
            except:
                thumb = None
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None

        try:
            width, height = await Ranjan.get_dimentions(thumb)
        except:
            thumb = None

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)
    try:
        await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    except:
        pass
    try:
        await bot.send_document(
            chat_id=update.message.chat.id,
            document=single_file,
            caption=caption,
            thumb=thumb,
            force_document=True,
            reply_to_message_id=reply_msg.id,
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Uploading....**", c_time),
        )

        await clear_server_two(single_file, thumb)
        await delete_msg(ef)
    except FloodWait as f:
        asyncio.sleep(f.x)
        return await playlist_uploader(bot, update, single_file, selected_format)
    except FileNotFoundError:
        await update.message.answer("⚠️ Sorry, I can't find that file", show_alert=True)
    except Exception as e:
        await clear_server_two(single_file, thumb)
        print(e)
        try:
            await ef.edit(f"{caption}\n\n⚠️ {e}")
        except:
            pass


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
        minimum_duration = (total_duration / total_file_size) * (SPLIT_FILE_SIZE)
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
        size = ARCHIVE_SPLIT_SIZE
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
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)
    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    if (await db.get_asvideos(update.from_user.id)) is True:
        as_video = True
    else:
        as_video = False

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"

    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**File Name :** `{real_name}`\n\n**File Size :** {output_size}"

    elif selected_format == "Others":
        caption = f"`{real_name}`"

    else:
        caption = f"`{real_name}`\n\nVideo Quality : {selected_format}"

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

    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None
                as_video = False

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, 320))
                img.save(thumb, "JPEG")
            except:
                thumb = None
                as_video = False
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None
                as_video = False

        try:
            width, height = await Ranjan.get_dimentions(thumb)
        except:
            as_video = False
            thumb = None

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)
    if as_video:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
        except:
            pass
        try:
            uploaded_file = await USERBOT.send_video(
                chat_id=Config.PREMIUM_STORE,
                video=single_file,
                caption=caption,
                supports_streaming=True,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await bot.copy_message(
                    chat_id=update.from_user.id,
                    from_chat_id=uploaded_file.chat.id,
                    message_id=uploaded_file.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass

    else:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            uploaded_file = await USERBOT.send_document(
                chat_id=Config.PREMIUM_STORE,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await bot.copy_message(
                    chat_id=update.from_user.id,
                    from_chat_id=uploaded_file.chat.id,
                    message_id=uploaded_file.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass


# ------------ Premium Audio Uploader -------------#
async def tp_audio_uploader(
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)

    if (await db.get_upload_as(update.from_user.id)) is True:
        as_audio = True
    else:
        as_audio = False

    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    try:
        file_size_output = os.path.getsize(single_file)  # Working
        output_size = humanbytes(file_size_output)
    except:
        output_size = ""
        as_audio = False

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"
    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`\n\n**Audio Size :** {output_size}"

    elif selected_format == "Others":
        caption = f"`{real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**Audio Name :** `{real_name}`\n\n{captions}**Audio Size :** {output_size}"

    else:
        caption = f"`{real_name}`\n\n**Audio Size :** {output_size}\n**Audio Quality :** {selected_format}"

    duration = 0
    thumb = None

    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        as_audio = False
        thumb = None
        duration = 0

    thumb = None
    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None
                as_audio = False

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((90, 90))
                img.save(thumb, "JPEG")
            except:
                thumb = None
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None
                as_audio = False

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)
    if as_audio:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
        except:
            pass
        try:
            uploaded_file = await USERBOT.send_audio(
                chat_id=Config.PREMIUM_STORE,
                audio=single_file,
                caption=caption,
                duration=duration,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await bot.copy_message(
                    chat_id=update.from_user.id,
                    from_chat_id=uploaded_file.chat.id,
                    message_id=uploaded_file.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass

    else:
        try:
            await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        except:
            pass
        try:
            uploaded_file = await USERBOT.send_document(
                chat_id=Config.PREMIUM_STORE,
                document=single_file,
                caption=caption,
                thumb=thumb,
                force_document=True,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            logger.info(f"🌟 Bot is sending in Private ")
            try:
                await bot.copy_message(
                    chat_id=update.from_user.id,
                    from_chat_id=uploaded_file.chat.id,
                    message_id=uploaded_file.id,
                )
            except Exception as e:
                logger.info(f"⚠️ Error to send pm: {e}")

            await clear_server_two(single_file, thumb)
            await delete_msg(ef)
        except FloodWait as f:
            asyncio.sleep(f.x)
            return await playlist_uploader(bot, update, single_file, selected_format)
        except FileNotFoundError:
            await update.message.answer(
                "⚠️ Sorry, I can't find that file", show_alert=True
            )
        except Exception as e:
            await clear_server_two(single_file, thumb)
            print(e)
            try:
                await ef.edit(f"{caption}\n\n⚠️ {e}")
            except:
                pass


# --------- Premium Document Uploader -------------#
async def tp_document_uploader(
    bot, update, single_file, selected_format=None, captions=None
):
    reply_msg = update.message.reply_to_message
    update.from_user.id
    real_name = os.path.basename(single_file)
    ef = await update.message.reply(
        f"**Uploading :** `{real_name}`", reply_to_message_id=reply_msg.id
    )

    if captions is None:
        captions = ""
    else:
        captions = f"{captions}\n"
    if selected_format.startswith("GoogleDrive"):
        rnumber = " "
        try:
            wnumber = selected_format.split("/")
            rnumber = wnumber[1]
        except:
            pass
        caption = f"`{rnumber} - {real_name}`"

    elif selected_format == "NameAndSize":
        caption = f"**File Name :** `{real_name}`\n\n{captions}"

    else:
        caption = f"`{real_name}`"

    duration = 0
    try:
        duration = await Ranjan.get_duration(single_file)
    except:
        thumb = None
        duration = 0
    thumb = None
    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                print(e)
                await update.message.reply(
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                    reply_to_message_id=reply_msg.id,
                )
                thumb = None

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, 320))
                img.save(thumb, "JPEG")
            except:
                thumb = None
        else:
            try:
                thumb = await take_screen_shot(
                    single_file, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except:
                thumb = None

        try:
            width, height = await Ranjan.get_dimentions(thumb)
        except:
            thumb = None

    c_time = time.time()
    progress_bar = Progress(update.from_user.id, bot, ef)
    try:
        await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    except:
        pass
    try:
        uploaded_file = await USERBOT.send_document(
            chat_id=Config.PREMIUM_STORE,
            document=single_file,
            caption=caption,
            thumb=thumb,
            force_document=True,
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Uploading....**", c_time),
        )

        logger.info(f"🌟 Bot is sending in Private ")
        try:
            await bot.copy_message(
                chat_id=update.from_user.id,
                from_chat_id=uploaded_file.chat.id,
                message_id=uploaded_file.id,
            )
        except Exception as e:
            logger.info(f"⚠️ Error to send pm: {e}")

        await clear_server_two(single_file, thumb)
        await delete_msg(ef)
    except FloodWait as f:
        asyncio.sleep(f.x)
        return await playlist_uploader(bot, update, single_file, selected_format)
    except FileNotFoundError:
        await update.message.answer("⚠️ Sorry, I can't find that file", show_alert=True)
    except Exception as e:
        await clear_server_two(single_file, thumb)
        print(e)
        try:
            await ef.edit(f"{caption}\n\n⚠️ {e}")
        except:
            pass
