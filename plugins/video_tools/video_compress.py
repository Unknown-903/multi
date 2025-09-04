import asyncio
import datetime
import logging
import math
import os
import random
import re
import time

from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from config import Config
from database.database import Database
from helpers.display_progress import Progress, TimeFormatter, humanbytes
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    delete_msg,
    dmsg_edit,
    msg_edit,
)
from plugins.audio_helper import Ranjan, take_screen_shot
from plugins.others.playlist_uploader import playlist_uploader

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def probe_file(filepath):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=height",
        "-of",
        "csv=s=x:p=0",
        filepath,
    ]
    logger.info(cmd)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    logger.debug("[stdout] " + stdout.decode())
    logger.debug("[stderr] " + stderr.decode())

    file_info = stdout.decode()
    return file_info


def is_cancelled(update, chat_id, message_id):
    cancelled = False
    if CANCEL_PROCESS[chat_id] and message_id in CANCEL_PROCESS[chat_id]:
        cancelled = True
    return cancelled


async def compress_video(
    video_file,
    output_directory,
    total_time,
    bot,
    message,
    status,
    new_file_name,
    hightv,
    widthv,
    bitratev,
    extension,
    update,
):
    out_put_file_name = output_directory + "/" + new_file_name + f".{extension}"
    progress = status
    with open(progress, "w") as f:
        pass
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "quiet",
        "-progress",
        progress,
        "-i",
        video_file,
        "-b:v",
        f"{bitratev}k",
        "-c:a",
        "copy",
        "-vf",
        f"scale={widthv}:{hightv}",
        "-compression_level",
        f"{0}",
        out_put_file_name,
    ]

    COMPRESSION_START_TIME = time.time()
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    logger.info("ffmpeg_process: " + str(process.pid))
    while process.returncode != 0:
        await asyncio.sleep(3)
        with open(status, "r+") as file:
            text = file.read()
            frame = re.findall("frame=(\d+)", text)
            time_in_us = re.findall("out_time_ms=(\d+)", text)
            progress = re.findall("progress=(\w+)", text)
            speed = re.findall("speed=(\d+\.?\d*)", text)
            if len(frame):
                frame = int(frame[-1])
            else:
                frame = 1
            if len(speed):
                speed = speed[-1]
            else:
                speed = 1
            if len(time_in_us):
                time_in_us = time_in_us[-1]
            else:
                time_in_us = 1
            if len(progress):
                if progress[-1] == "end":
                    logger.info(progress[-1])
                    break

            if is_cancelled(update, update.message.chat.id, message.id):
                logger.info("Process Cancelled ❌❌ ")
                try:
                    nicebots = await bot.edit_message_text(
                        f"**Process Cancelled ✅**",
                        update.message.chat.id,
                        message.id,
                    )
                    await nicebots.delete()
                except:
                    pass
                await bot.stop_transmission()
                break

            TimeFormatter((time.time() - COMPRESSION_START_TIME) * 1000)
            elapsed_time = int(time_in_us) / 1000000
            difference = math.floor((total_time - elapsed_time) / float(speed))
            if difference > 0:
                TimeFormatter(difference * 1000)
            percentage = math.floor(elapsed_time * 100 / total_time)
            progress_str = "<b>Percentage :</b> {0}%\n\n[{1}{2}]".format(
                round(percentage, 2),
                "".join(["●" for i in range(math.floor(percentage / 5))]),
                "".join(["○" for i in range(20 - math.floor(percentage / 5))]),
            )
            # stats = f'<b>Compressing....</b>\n\n' \
            #         f'<b>ETA :</b> {ETA}\n\n' \
            #         f'{progress_str}\n'

            percentages = "{}%".format(round(percentage, 2))
            stats = f"<b>Compressing....</b> {percentages}"

            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Cancel",
                            callback_data=(
                                f"progcancel/{update.message.chat.id}/{message.id}/{update.from_user.id}"
                            ).encode("UTF-8"),
                        )
                    ]
                ]
            )

            try:
                await message.edit_text(text=stats, reply_markup=reply_markup)
            except:
                pass

    #   try:
    #     await log_msg.edit_text(
    #       text=stats
    #     )
    #   except:
    #       pass
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(e_response)
    logger.info(t_response)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


@Client.on_callback_query(filters.regex("^commm"))
async def compress_video_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
    width = 0
    height = 0

    if reply_msg.media:
        logger.info(
            f"☘️ Sent Video for Compressing. User {update.from_user.id} @{update.from_user.username}"
        )
        if user_id not in Config.AUTH_USERS:
            media_file = reply_msg.video or reply_msg.document or reply_msg.audio
            FILE_SIZE = media_file.file_size
            if FILE_SIZE >= Config.MAX_COM_SIZE:  # MB
                MAX_VIDEO_SIZE = humanbytes(Config.MAX_COM_SIZE)
                await update.message.reply(
                    f"🧐 Encoding is a slow process, And it needs more RAM for proper functioning.\n\n👉 So, Only Admin can use Compressor\n\n👉 Free users can Test only for file_size less than {MAX_VIDEO_SIZE}\n\n👉 Or, You can use These\n\n(1). @videocompressor_cbot\n(2). @VideoCompress_cBot\n(3). @Compressorbot_cbot",
                    reply_to_message_id=reply_msg.id,
                )
                try:
                    del Config.TIME_GAP_STORE[update.from_user.id]
                except Exception as e:
                    logger.info(
                        f"⚠️ Error Compress TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                return

    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if os.path.isdir(download_path):
        await update.message.reply(
            "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__",
            reply_to_message_id=reply_msg.id,
        )
        return

    if reply_msg.video:
        try:
            files_audio = update.message.reply_to_message
            medias = files_audio.video
            duratio = medias.duration
        except Exception as e:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"**⚠️ Error** : {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if user_id not in Config.AUTH_USERS:
            if duratio > Config.MAX_COM_DURATION:  # max duration of video
                try:
                    MAX_DURATION = datetime.timedelta(seconds=Config.MAX_COM_DURATION)
                except:
                    MAX_DURATION = ""
                ab = await bot.send_message(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ Send Video which duration is less than {MAX_DURATION}",
                    reply_to_message_id=reply_msg.id,
                )
                return

    if len(COUNT) > Config.NUMBER:
        logbutton = [
            [InlineKeyboardButton("Logs Channel", url=f"https://t.me/ViiiideoCom1Logs")]
        ]
        InlineKeyboardMarkup(logbutton)
        ab = await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"**⚠️ Already {Config.NUMBERS} Process Running**\n\n👉 Try Another Compressor Bots\n\n(1). @Compressorbot_cbot\n(2). @VideoCompress_cBot\n(3). @videocompressor_cbot",
            #      reply_markup=logmarkup,
            reply_to_message_id=reply_msg.id,
        )
        return

    if user_id in COUNT:
        ab = await bot.send_message(
            chat_id=update.message.chat.id,
            text="Already Your 1 Request Processing",
            reply_to_message_id=reply_msg.id,
        )
        return

    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )
    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    BUTTON_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if reply_msg.media:
        SELECT_QUALITY = ReplyKeyboardMarkup(
            [
                ["480p", "360p"],
                ["240p", "144p"],
                ["Cancel"],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        new_file_name = "Default_Name"
        video_quality = await bot.ask(
            chat_id=update.message.chat.id,
            text="I don't compress below than 360p.\n\nSo, Send me video of higher quality to compress. Now select video Quality on Button.\n\n__✶ **Click the Button of your choice**__",
            reply_markup=SELECT_QUALITY,
            filters=filters.text,
        )
        await video_quality.delete()
        await video_quality.request.delete()
        if video_quality.text == "Cancel":
            await clear_server(user_id, saved_file_path)
            return await update.message.reply(
                "**Process Cancelled** ✅", reply_to_message_id=reply_msg.id
            )
        elif video_quality.text == "480p":
            widthv = "854"
            hightv = "480"
            bitratev = "500"
        elif video_quality.text == "360p":
            widthv = "640"
            hightv = "360"
            bitratev = "400"
        elif video_quality.text == "240p":
            widthv = "426"
            hightv = "240"
            bitratev = "150"
        elif video_quality.text == "144p":
            widthv = "256"
            hightv = "144"
            bitratev = "61"
        else:
            widthv = "640"
            hightv = "360"
            bitratev = "400"

        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of Output Video**",
                reply_markup=BUTTON_CANCEL,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            )
            await ask_.delete()
            await ask_.request.delete()
            cfile_name = ask_.text

            if cfile_name == "Cancel":
                await update.message.reply(
                    "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                )
                logger.info(
                    f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                await clear_server(user_id, saved_file_path)
                return

            if "." in cfile_name:
                try:
                    splitit = cfile_name.split(".")
                    extension = splitit[-1]
                except:
                    extension = "mkv"
            else:
                extension = "mkv"

            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[
                :60
            ]  # truncated_text = new_name[0:60] # File name reduced

            IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
            if len(cfile_name) > 60:
                long_msg = await update.message.reply(
                    IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name))
                )
                await clear_server(user_id, saved_file_path)
                return

        try:
            ab = await update.message.reply(
                "**Downloading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        if Config.LOG_CHANNEL:
            try:
                comf2v = await reply_msg.copy(chat_id=Config.LOG_CHANNEL)
                await comf2v.reply_text(
                    f"**Currently Using 👇** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`"
                )
            except FloodWait as fw:
                await asyncio.sleep(fw.x)
            except Exception as e:
                print(e)
        COUNT.append(user_id)
        c_time = time.time()
        status = f"progress-{c_time}.txt"
        prog = Progress(update.from_user.id, bot, ab)
        real_audio = await bot.download_media(
            message=reply_msg,
            file_name=saved_file_path,
            progress=prog.progress_for_pyrogram,
            progress_args=("**Downloading....**", c_time),
        )

        if (
            CANCEL_PROCESS[update.message.chat.id]
            and ab.id in CANCEL_PROCESS[update.message.chat.id]
        ):
            await clear_server(user_id, saved_file_path)
            return

        try:
            bc = await ab.edit(f"Video Downloaded Successfully ✅")
        except:
            await delete_msg(ab)
            try:
                bc = await update.message.reply(
                    "Video Downloaded Successfully ✅",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return
    # ----------------- Direct Links -------------#
    else:
        logger.info(
            f"☘️ Sent URL for Compressing. User {update.from_user.id} @{update.from_user.username}"
        )
        SELECT_QUALITY = ReplyKeyboardMarkup(
            [
                ["480p", "360p"],
                ["240p", "144p"],
                ["Cancel"],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        new_file_name = "Default_Name"
        video_quality = await bot.ask(
            chat_id=update.message.chat.id,
            text="I don't compress below than 360p.\n\nSo, Send me video of higher quality to compress. Now select video Quality on Button.\n\n__✶ **Click the Button of your choice**__",
            reply_markup=SELECT_QUALITY,
            filters=filters.text,
        )
        await video_quality.delete()
        await video_quality.request.delete()
        if video_quality.text == "Cancel":
            await clear_server(user_id, saved_file_path)
            return await update.message.reply(
                "**Process Cancelled** ✅", reply_to_message_id=reply_msg.id
            )
        elif video_quality.text == "480p":
            widthv = "854"
            hightv = "480"
            bitratev = "500"
        elif video_quality.text == "360p":
            widthv = "640"
            hightv = "360"
            bitratev = "400"
        elif video_quality.text == "240p":
            widthv = "426"
            hightv = "240"
            bitratev = "150"
        elif video_quality.text == "144p":
            widthv = "256"
            hightv = "144"
            bitratev = "61"
        else:
            widthv = "640"
            hightv = "360"
            bitratev = "400"

        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of Output Video**",
                reply_markup=BUTTON_CANCEL,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            )
            await ask_.delete()
            await ask_.request.delete()
            cfile_name = ask_.text

            if cfile_name == "Cancel":
                await update.message.reply(
                    "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                )
                logger.info(
                    f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                await clear_server(user_id, saved_file_path)
                return

            if "." in cfile_name:
                try:
                    splitit = cfile_name.split(".")
                    extension = splitit[-1]
                except:
                    extension = "mkv"
            else:
                extension = "mkv"

            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[
                :60
            ]  # truncated_text = new_name[0:60] # File name reduced

            IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
            if len(cfile_name) > 60:
                long_msg = await update.message.reply(
                    IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name))
                )
                await clear_server(user_id)
                return

        saved_file_path = reply_msg.text
        if Config.LOG_CHANNEL:
            try:
                comf2v = await reply_msg.copy(chat_id=Config.LOG_CHANNEL)
                await comf2v.reply_text(
                    f"**Currently Using 👇** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`"
                )
            except FloodWait as fw:
                await asyncio.sleep(fw.x)
            except Exception as e:
                print(e)
        c_time = time.time()
        status = f"progress-{c_time}.txt"

        try:
            bc = await bot.send_message(
                chat_id=update.message.chat.id,
                text="🔗 URL Received",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await clear_server(user_id, saved_file_path)
            print(e)
            return
        COUNT.append(user_id)
    # ---------------------------------------------#
    try:
        duration = 0
        duration = await Ranjan.get_duration(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : {e}")
        return

    try:
        time_format = datetime.timedelta(seconds=duration)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(
            bc,
            f"⚠️ **Error** : Duration not found!!!",
        )
        return

    if duration < 1:
        await clear_server(user_id, saved_file_path)
        await msg_edit(bc, f"⚠️ **Error** : Duration is Less than 1 Sec")
        return

    if user_id not in Config.AUTH_USERS:
        if duration > Config.MAX_COM_DURATION:
            try:
                MAX_DURATION = datetime.timedelta(seconds=Config.MAX_COM_DURATION)
            except:
                MAX_DURATION = ""
            await clear_server(user_id, saved_file_path)
            await msg_edit(
                bc, f"⚠️ Send Video which duration is less than {MAX_DURATION}"
            )
            return

    try:
        media_rsulation = await probe_file(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : {e}")
        return

    if user_id not in Config.AUTH_USERS:
        if int(media_rsulation) < 481:
            await clear_server(user_id, saved_file_path)
            await msg_edit(bc, f"⚠️ I don't compress below than 480p")
            return

    if user_id not in Config.AUTH_USERS:
        if int(media_rsulation) > 1501:
            await clear_server(user_id, saved_file_path)
            await msg_edit(
                bc, f"⚠️ Send video 1080p or Below\n\n👉 Server can't handle to Encode"
            )
            return

    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.document or file_video.audio
            description_ = media.file_name
            if "." in description_:
                try:
                    splitit = description_.split(".")
                    extension = splitit[-1]
                except:
                    extension = "mkv"
            else:
                extension = "mkv"
            description_ = os.path.splitext(description_)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
            extension = "mkv"
    else:
        try:
            #  file_name = saved_file_path.split("/")[-1]
            file_name = os.path.basename(saved_file_path)
            extension = "mkv"
            description_ = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
            extension = "mkv"

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            description_ = f"{cfile_name}"
        except:
            description_ = "Default_Name"

    try:
        new_file_name = f"{cfile_name}"
    except:
        new_file_name = description_

    stickeraudio = None
    try:
        stickeraudio = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAESX81jQ4atc_bS1YcfJ3IfCuTfSfoKkwACegYAAgu2GVYTpn876J0baCoE",
        )
    except:
        pass

    try:
        cd = await bc.edit(f"**Compressing....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**Compressing....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await delete_msg(stickeraudio)
            return

    log_msg = None
    logreply_msg = None
    try:
        chat_ids = Config.LOG_CHANNEL
        log_msg = await bot.send_message(
            chat_ids,
            f"**Compressing....**",
        )
        logreply_msg = await log_msg.reply_text(
            f"**Currently Using 👇** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`"
        )
    except:
        pass

    au_start = time.time()
    try:
        compressed = None
        compressed = await asyncio.wait_for(
            compress_video(
                saved_file_path,
                Config.DOWNLOAD_LOCATION,
                duration,
                bot,
                cd,
                status,
                new_file_name,
                hightv,
                widthv,
                bitratev,
                extension,
                update,
            ),
            7200,
        )
    except asyncio.TimeoutError:
        await clear_server(user_id, saved_file_path, compressed)
        await delete_msg(log_msg, logreply_msg, stickeraudio)
        await msg_edit(
            cd,
            f"⚠️ Compressing Timed Out\n\n👉 Reason : Your video is taking too much time",
        )
        logger.info(
            f"⚠️⚠️ Compressing Timed Out of  {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    except Exception as e:
        await clear_server(user_id, saved_file_path, compressed)
        print(e)
        await msg_edit(cd, f"Process Cancelled  ✅ \n\n**Due to** : {e}")
        await delete_msg(log_msg, logreply_msg, stickeraudio)
        logger.info(
            f"Process Cancelled  ✅  Error 👉 {e} User 👉 {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and cd.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        await clear_server(user_id, saved_file_path, compressed)
        await delete_msg(log_msg, logreply_msg, stickeraudio)
        logger.info(
            f"Process Cancelled ❌❌ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        try:
            await update.message.reply(
                text=f"Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            print(e)
        return

    if compressed is None:
        await clear_server(user_id, saved_file_path, compressed)
        await msg_edit(cd, f"⚠️ **Error** : in Compressing")
        await delete_msg(log_msg, logreply_msg, stickeraudio)
        return

    compressed_time = TimeFormatter((time.time() - au_start) * 1000)
    await delete_msg(log_msg, logreply_msg, stickeraudio)

    try:
        output_size = os.path.getsize(compressed)
    except Exception as e:
        await clear_server(user_id, saved_file_path, compressed)
        await msg_edit(cd, f"⚠️ Error occured: {e}")
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    selected_format = "Others"
    if output_size > (1999 * 1024 * 1024):  # 1999mb
        await delete_msg(cd)
        try:
            await playlist_uploader(bot, update, trimn, selected_format)
        except:
            pass
        await clear_server(user_id, saved_file_path, compressed)
        logger.info(
            f"Video Compressed ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    thumb = None
    if (await db.get_othumb(update.from_user.id)) is False:
        thumb = None
    else:
        thumb = f"{Config.DOWNLOAD_LOCATION}/thenicebots{update.from_user.id}.jpg"
        try:
            thumbnail = await db.get_thumbnail(update.from_user.id)
        except Exception as e:
            logger.info(
                f"⚠️ Error: {e} ✅ By {str(update.from_user.id)} @{update.from_user.username}"
            )
            thumbnail = None
        if thumbnail is not None:
            try:
                thumb = await bot.download_media(message=thumbnail, file_name=thumb)
            except Exception as e:
                await clear_server(user_id, saved_file_path, compressed, thumb)
                print(e)
                await msg_edit(
                    cd,
                    f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                )
                return

            try:
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, 320))
                img.save(thumb, "JPEG")
            except:
                pass
        else:
            try:
                thumb = await take_screen_shot(
                    compressed, os.path.dirname(thumb), random.randint(0, duration - 1)
                )
            except Exception as e:
                await clear_server(user_id, saved_file_path, compressed, thumb)
                print(e)
                await msg_edit(cd, f"⚠️ **Error** : {e}")
                return

        try:
            width, height = await Ranjan.get_dimentions(thumb)
        except Exception as e:
            await clear_server(user_id, saved_file_path, compressed, thumb)
            print(e)
            await msg_edit(
                cd,
                f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
            )
            return

    try:
        ef = await cd.edit(f"**Uploading....**")
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                "**Uploading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path, compressed, thumb)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    if reply_msg.media:
        try:
            file_size_input = os.path.getsize(saved_file_path)
            input_size = humanbytes(file_size_input)

            file_size_output = os.path.getsize(compressed)
            output_size = humanbytes(file_size_output)
            description_ = (
                "File Name : "
                + description_
                + f".{extension}"
                + f"\n\nVideo Quality : {hightv}p\nCompressed in : {compressed_time}\n\nNow Video Size : {output_size}\nBefore Video Size : {input_size}"
            )
        except:
            description_ = description_ + f".{extension}"
    else:
        try:
            file_size_output = os.path.getsize(compressed)
            output_size = humanbytes(file_size_output)
            description_ = (
                "File Name : "
                + description_
                + f".{extension}"
                + f"\n\nVideo Quality : {hightv}p\nCompressed in : {compressed_time}\n\nNow Video Size : {output_size}"
            )
        except:
            description_ = description_ + f".{extension}"

    if (await db.get_asvideos(update.from_user.id)) is True:
        try:
            c_time = time.time()
            prog = Progress(update.from_user.id, bot, ef)
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
            except:
                pass
            diksha = await bot.send_video(
                chat_id=update.message.chat.id,
                video=compressed,
                caption=description_,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                thumb=thumb,
                reply_to_message_id=reply_msg.id,
                progress=prog.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, compressed, thumb)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n👉 Video Compressed ✅"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Video Compressed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    else:
        try:
            prog = Progress(update.from_user.id, bot, ef)
            c_time = time.time()
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            except:
                pass
            diksha = await bot.send_document(
                chat_id=update.message.chat.id,
                document=compressed,
                caption=description_,
                thumb=thumb,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=prog.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, compressed, thumb)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n👉 Video Compressed ✅"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Video Compressed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    await clear_server(user_id, saved_file_path, compressed, thumb)


"""
2160p: 3840x2160
1440p: 2560x1440
1080p: 1920x1080
720p: 1280x720
480p: 854x480
360p: 640x360
240p: 426x240

        mt = mimetypes.guess_type(saved_file_path)
        if mt:
            print("Mime Type:", mt[0])
        else:
            print("Cannot determine Mime Type")

        filetype = mt[0]
        if filetype is None:
            await bc.edit("⚠️ Your file type is application in url\n\n👉 First rename your file and add Extension.\n\n👉 And make direct link in @FileToLinkGen_cBot")
            await clear_server(user_id, saved_file_path)
            return
        if filetype.startswith("application/"):
            await bc.edit("⚠️ Your file type is application, in URL\n\n👉 Make direct link in @FileToLinkGen_cBot")
            await clear_server(user_id, saved_file_path)
            return
        if not filetype.startswith("video/"):
            await bc.edit("⚠️ Video not found in url")
            await clear_server(user_id, saved_file_path)
            return

"""
