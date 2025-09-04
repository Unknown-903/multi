import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import Config
from database.database import Database
from helpers.display_progress import Progress, humanbytes
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    delete_msg,
)
from plugins.audio_helper import Ranjan
from plugins.others.playlist_uploader import playlist_uploader

db = Database()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


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


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("vniceytdl"))
)
async def _vniceytdl(bot, update):
    await delete_msg(update.message)
    ab = None
    ef = None
    stickerc = None
    update.data
    updated_data = update.data.split("/")
    tg_send_type, yt_dlp_format, yt_dlp_ext = (
        updated_data[1],
        updated_data[2],
        updated_data[3],
    )
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message

    tmp_directory_for_each_user = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    )

    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)

    thumb_image_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    )
    save_ytdl_json_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".json"
    )
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except (FileNotFoundError):
        await update.message.reply(
            "**Error :** json file not found",
            reply_to_message_id=reply_msg.id,
        )
        await clear_server(
            user_id, tmp_directory_for_each_user, thumb_image_path, save_ytdl_json_path
        )
        return False
    # ---------------------------------------------#
    if (await db.get_auto_rename(update.from_user.id)) is True:
        NUMBER_BUTTONS = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            yt_name = str(response_json.get("title"))
            new_name = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"**Title :** `{yt_name}`\n\n✶ Extension (eg. .mp4 .mp3) is Optional. If you want to add extension then Give Filename with extension (eg. `newfilename.mp4`)\n\n__**Now Send Me The New File Name**__ 👇",
                    reply_markup=NUMBER_BUTTONS,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                900,
            )
            try:
                await new_name.delete()
                await new_name.request.delete()
            except:
                pass
            new_name = new_name.text
        except asyncio.TimeoutError:
            try:
                ccc = await update.message.reply(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await ccc.delete()
            except:
                pass
            new_name = "Time Out"

        if "." in new_name:
            try:
                splitit = new_name.split(".")
                extension = splitit[-1]
            except:
                extension = yt_dlp_ext
        else:
            extension = yt_dlp_ext

        new_name = os.path.splitext(new_name)[0]  # extension Removed
        new_name = new_name[:60]  # truncated_text = new_name[0:60] # File name reduced

        IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File Name And Try again"""
        if len(new_name) > 60:
            long_msg = await update.message.reply(
                IF_LONG_FILE_NAME.format(alimit="60", num=len(checkerss)),
                reply_to_message_id=reply_msg.id,
            )
            await clear_server(
                user_id,
                tmp_directory_for_each_user,
                thumb_image_path,
                save_ytdl_json_path,
            )
            return

        if new_name == "Cancel":
            new_names = "Cancel"
        elif new_name == "Time Out":
            new_names = "TimeUp"
        else:
            new_names = new_name

        if new_names == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            await clear_server(
                user_id,
                tmp_directory_for_each_user,
                thumb_image_path,
                save_ytdl_json_path,
            )
            return

        if new_names == "TimeUp":
            await update.message.reply(
                "⚠️ Process Time Out, Resend Again",
                reply_to_message_id=reply_msg.id,
            )
            await clear_server(
                user_id,
                thumb_image_path,
                tmp_directory_for_each_user,
                save_ytdl_json_path,
            )
            return

    # ---------------------------------------------#
    if yt_dlp_ext == "webm":
        yt_dlp_ext = "mkv"
    yt_dlp_url = update.message.reply_to_message.text
    custom_file_name = (
        str(response_json.get("title")) + "_" + yt_dlp_format + "." + yt_dlp_ext
    )
    yt_dlp_username = None
    yt_dlp_password = None
    if "|" in yt_dlp_url:
        url_parts = yt_dlp_url.split("|")
        if len(url_parts) == 2:
            yt_dlp_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            yt_dlp_url = url_parts[0]
            custom_file_name = url_parts[1]
            yt_dlp_username = url_parts[2]
            yt_dlp_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    yt_dlp_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    yt_dlp_url = yt_dlp_url[o : o + l]
        if yt_dlp_url is not None:
            yt_dlp_url = yt_dlp_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        if yt_dlp_username is not None:
            yt_dlp_username = yt_dlp_username.strip()
        if yt_dlp_password is not None:
            yt_dlp_password = yt_dlp_password.strip()
        logger.info(yt_dlp_url)
        logger.info(custom_file_name)
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                yt_dlp_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                yt_dlp_url = yt_dlp_url[o : o + l]

    description = ""
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]

    cance_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Progress", callback_data=f"xrprog")],
            [
                InlineKeyboardButton(
                    "Cancel",
                    callback_data=(
                        f"progcancel/{update.message.chat.id}/{reply_msg.id}/{update.from_user.id}"
                    ).encode("UTF-8"),
                )
            ],
        ]
    )
    ab = await bot.send_message(
        text="**Downloading....**",
        chat_id=update.message.chat.id,
        reply_markup=cance_markup,
        reply_to_message_id=reply_msg.id,
    )
    stickerc = await bot.send_sticker(
        chat_id=update.message.chat.id,
        sticker="CAACAgUAAxkBAAJvFWF7YaMKXvQe_dUiFKKhMQacz39rAALEAgACBG2gVsF1Ng9n9CrHHgQ",
    )

    COUNT.append(user_id)

    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    TG_MAX_FILE_SIZE = 1998 * 1024 * 1024
    HTTP_PROXY = ""

    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize",
            str(TG_MAX_FILE_SIZE),
            "--bidi-workaround",
            "--extract-audio",
            "--audio-format",
            yt_dlp_ext,
            "--audio-quality",
            yt_dlp_format,
            yt_dlp_url,
            "-o",
            download_directory,
        ]
    else:
        minus_f_format = yt_dlp_format
        if "youtu" in yt_dlp_url:
            minus_f_format = yt_dlp_format + "+bestaudio[ext=m4a]/best"
        command_to_exec = [
            "yt-dlp",
            "--continue",
            "--embed-subs",
            "--no-warnings",
            "-f",
            minus_f_format,
            
            "--bidi-workaround",
            "-o",
            download_directory,
            yt_dlp_url,
        ]

    if HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(HTTP_PROXY)
    if yt_dlp_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(yt_dlp_username)
    if yt_dlp_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(yt_dlp_password)
    command_to_exec.append("--no-warnings")
    if "hotstar" in yt_dlp_url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")

    logger.info(command_to_exec)
    datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        try:
            await stickerc.delete()
            await ab.edit("Process Cancelled ✅")
            print("Process Cancelled ✅")
        except:
            pass
        await clear_server(
            user_id,
            tmp_directory_for_each_user,
            download_directory,
            save_ytdl_json_path,
        )
        return

    ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call yt-dlp with the --verbose flag and include its complete output."
    if e_response and ad_string_to_replace in e_response:
        e_response.replace(ad_string_to_replace, "")
        await clear_server(
            user_id, tmp_directory_for_each_user, thumb_image_path, save_ytdl_json_path
        )
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=ab.id,
            text=f"⚠️ **Error :** In yt-dlp\n\n👉 So i can't upload the file",
        )
        return False
    if t_response:
        await clear_server_two(save_ytdl_json_path)
        try:
            file_size = os.path.getsize(download_directory)
        except FileNotFoundError:
            try:
                download_directory = (
                    os.path.splitext(download_directory)[0] + "." + "mkv"
                )
                file_size = os.path.getsize(download_directory)
            except Exception as e:
                await clear_server(
                    user_id,
                    tmp_directory_for_each_user,
                    thumb_image_path,
                    save_ytdl_json_path,
                )
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ OS **Error :** {e}",
                    message_id=ab.id,
                )
                await stickerc.delete()
                return
        if file_size > (1999 * 1024 * 1024):
            await delete_msg(ab, stickerc)
            new_download_directory = None
            if (await db.get_auto_rename(update.from_user.id)) is True:
                new_download_directory = (
                    tmp_directory_for_each_user + "/" + f"{new_names}.{extension}"
                )
                os.rename(download_directory, new_download_directory)
            else:
                new_download_directory = download_directory

            try:
                selected_format = f"Others"
                premium_upload = "Yes"
                captions = None
                await playlist_uploader(
                    bot,
                    update,
                    new_download_directory,
                    selected_format,
                    captions,
                    premium_upload,
                )
            except Exception as e:
                print(e)
            await clear_server(
                user_id, save_ytdl_json_path, new_download_directory, thumb_image_path
            )
            logger.info(
                f"URL Uploaded  ✅ For User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        else:
            try:
                await stickerc.delete()
                ef = await bot.edit_message_text(
                    text="**Uploading....**",
                    chat_id=update.message.chat.id,
                    message_id=ab.id,
                )
            except:
                ef = await bot.send_message(
                    text="**Uploading....**",
                    chat_id=update.message.chat.id,
                    reply_to_message_id=reply_msg.id,
                )
            width = 0
            height = 0
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None:
                    if metadata.has("duration"):
                        duration = metadata.get("duration").seconds

            thumbnail = None
            thumbnail = await db.get_thumbnail(update.from_user.id)
            if thumbnail is not None:
                try:
                    thumb_image_path = await bot.download_media(
                        message=thumbnail, file_name=thumb_image_path
                    )
                except Exception as e:
                    await clear_server(
                        user_id,
                        save_ytdl_json_path,
                        new_download_directory,
                        thumb_image_path,
                    )
                    await bot.edit_message_text(
                        chat_id=update.message.chat.id,
                        text=f"⚠️ **Thumbnail Error** : {e}\n\n👉 Delete old Thumbnail from database, Use Command /del_thumb And Try again",
                        message_id=ef.id,
                    )
                    return

                try:
                    Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    img.resize((320, 320))
                    img.save(thumb_image_path, "JPEG")
                except:
                    pass
            else:
                if os.path.exists(thumb_image_path):
                    width = 0
                    height = 0
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width

                    Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    if tg_send_type == "file":
                        img.resize((320, height))
                    else:
                        img.resize((90, height))
                    img.save(thumb_image_path, "JPEG")

                else:
                    try:
                        thumb_image_path = await take_screen_shot(
                            download_directory,
                            os.path.dirname(download_directory),
                            random.randint(0, duration - 1),
                        )
                    except:
                        thumb_image_path = None

            if (await db.get_othumb(update.from_user.id)) is False:
                thumb_image_path = None

            new_download_directory = None
            if (await db.get_auto_rename(update.from_user.id)) is True:
                new_download_directory = (
                    tmp_directory_for_each_user + "/" + f"{new_names}.{extension}"
                )
                os.rename(download_directory, new_download_directory)
                description = f"**File Name :** `{new_names}.{extension}`"
            else:
                new_download_directory = download_directory

            progress_bar = Progress(update.from_user.id, bot, ef)
            start_time = time.time()
            if tg_send_type == "audio":
                if (await db.get_upload_as(update.from_user.id)) is True:
                    try:
                        file_size_output = os.path.getsize(
                            new_download_directory
                        )  # Working
                        output_size = humanbytes(file_size_output)
                        final_description = (
                            description
                            + f".{yt_dlp_ext}"
                            + f"\n\nFile Size : {output_size}"
                        )
                    except:
                        final_description = description

                    try:
                        durations = await Ranjan.get_duration(download_directory)
                    except:
                        durations = 0

                    try:
                        try:
                            await update.message.reply_chat_action(
                                enums.ChatAction.UPLOAD_AUDIO
                            )
                        except:
                            pass
                        daudio = await bot.send_audio(
                            chat_id=update.message.chat.id,
                            audio=new_download_directory,
                            caption=final_description,
                            duration=durations,
                            thumb=thumb_image_path,
                            reply_to_message_id=update.message.reply_to_message.id,
                            progress=progress_bar.progress_for_pyrogram,
                            progress_args=("**Uploading....**", start_time),
                        )

                        if (
                            CANCEL_PROCESS[update.message.chat.id]
                            and ef.id in CANCEL_PROCESS[update.message.chat.id]
                        ):
                            print("Process Cancelled ✅")
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                save_ytdl_json_path,
                                new_download_directory,
                            )
                            return

                        good3 = await bot.edit_message_text(
                            text=".",
                            chat_id=update.message.chat.id,
                            message_id=ef.id,
                            disable_web_page_preview=True,
                        )
                        await good3.delete()
                        if Config.LOG_CHANNEL:
                            try:
                                urlaudio = await daudio.copy(chat_id=Config.LOG_CHANNEL)
                                await urlaudio.reply_text(
                                    f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader Audio"
                                )
                            except FloodWait:
                                await asyncio.sleep(5)
                            except Exception as e:
                                print(e)
                        logger.info(
                            f"URL To Audio Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )

                    except Exception as e:
                        print(e)
                        await ef.edit(text=f"**Error** : {e}")

                else:
                    try:
                        try:
                            await update.message.reply_chat_action(
                                enums.ChatAction.UPLOAD_DOCUMENT
                            )
                        except:
                            pass
                        daudio = await bot.send_document(
                            chat_id=update.message.chat.id,
                            document=new_download_directory,
                            caption=description,
                            thumb=thumb_image_path,
                            force_document=True,
                            reply_to_message_id=update.message.reply_to_message.id,
                            progress=progress_bar.progress_for_pyrogram,
                            progress_args=("**Uploading....**", start_time),
                        )
                        if (
                            CANCEL_PROCESS[update.message.chat.id]
                            and ef.id in CANCEL_PROCESS[update.message.chat.id]
                        ):
                            print("Process Cancelled ✅")
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                save_ytdl_json_path,
                                new_download_directory,
                            )
                            return
                        good3 = await bot.edit_message_text(
                            text=".",
                            chat_id=update.message.chat.id,
                            message_id=ef.id,
                            disable_web_page_preview=True,
                        )
                        await good3.delete()
                        if Config.LOG_CHANNEL:
                            try:
                                urlaudio = await daudio.copy(chat_id=Config.LOG_CHANNEL)
                                await urlaudio.reply_text(
                                    f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader Audio Doc"
                                )
                            except FloodWait:
                                await asyncio.sleep(5)
                            except Exception as e:
                                print(e)
                        logger.info(
                            f"URL To Audio(Doc) Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )

                    except Exception as e:
                        print(e)
                        await ef.edit(text=f"**Error** : {e}")

            elif tg_send_type == "file":
                try:
                    await update.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_DOCUMENT
                    )
                except:
                    pass
                ddoc = await bot.send_document(
                    chat_id=update.message.chat.id,
                    document=new_download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_bar.progress_for_pyrogram,
                    progress_args=("**Uploading....**", start_time),
                )
                if (
                    CANCEL_PROCESS[update.message.chat.id]
                    and ef.id in CANCEL_PROCESS[update.message.chat.id]
                ):
                    await clear_server(
                        user_id,
                        tmp_directory_for_each_user,
                        thumb_image_path,
                        save_ytdl_json_path,
                        new_download_directory,
                    )
                    return
                if (await db.get_auto_rename(update.from_user.id)) is False:
                    await ddoc.reply_text(
                        f"__If your file is not opening, Then rename and add Extension ( ex. .pdf, .zip, .rar etc )__ "
                    )
                good2 = await bot.edit_message_text(
                    text="Successfully Uploaded",
                    chat_id=update.message.chat.id,
                    message_id=ef.id,
                    disable_web_page_preview=True,
                )
                await good2.delete()
                if Config.LOG_CHANNEL:
                    try:
                        cmdoc = await ddoc.copy(chat_id=Config.LOG_CHANNEL)
                        await cmdoc.reply_text(
                            f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader"
                        )
                    except FloodWait:
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(e)
                logger.info(
                    f"URL To File(video) Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

            elif tg_send_type == "vm":
                try:
                    await update.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_VIDEO_NOTE
                    )
                except:
                    pass
                dnote = await bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=new_download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_bar.progress_for_pyrogram,
                    progress_args=("**Uploading....**", start_time),
                )
                if (
                    CANCEL_PROCESS[update.message.chat.id]
                    and ef.id in CANCEL_PROCESS[update.message.chat.id]
                ):
                    await clear_server(
                        user_id,
                        tmp_directory_for_each_user,
                        thumb_image_path,
                        save_ytdl_json_path,
                        new_download_directory,
                    )
                    return
                good1 = await bot.edit_message_text(
                    text="Successfully Uploaded",
                    chat_id=update.message.chat.id,
                    message_id=ef.id,
                    disable_web_page_preview=True,
                )
                await good1.delete()
                if Config.LOG_CHANNEL:
                    try:
                        cmnote = await dnote.copy(chat_id=Config.LOG_CHANNEL)
                        await cmnote.reply_text(
                            f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader"
                        )
                    except FloodWait:
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(e)
                logger.info(
                    f"URL To Video_Note Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

            elif tg_send_type == "video":
                if (await db.get_asvideos(update.from_user.id)) is True:
                    try:
                        try:
                            await update.message.reply_chat_action(
                                enums.ChatAction.UPLOAD_VIDEO
                            )
                        except:
                            pass
                        dvideo = await bot.send_video(
                            chat_id=update.message.chat.id,
                            video=new_download_directory,
                            caption=description,
                            duration=duration,
                            width=width,
                            height=height,
                            supports_streaming=True,
                            thumb=thumb_image_path,
                            reply_to_message_id=update.message.reply_to_message.id,
                            progress=progress_bar.progress_for_pyrogram,
                            progress_args=("**Uploading....**", start_time),
                        )

                        if (
                            CANCEL_PROCESS[update.message.chat.id]
                            and ef.id in CANCEL_PROCESS[update.message.chat.id]
                        ):
                            print("Process Cancelled ✅")
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                save_ytdl_json_path,
                                new_download_directory,
                            )
                            return

                        good = await bot.edit_message_text(
                            text="Successfully Uploaded",
                            chat_id=update.message.chat.id,
                            message_id=ef.id,
                            disable_web_page_preview=True,
                        )
                        await good.delete()
                        if Config.LOG_CHANNEL:
                            try:
                                cmvideo = await dvideo.copy(chat_id=Config.LOG_CHANNEL)
                                await cmvideo.reply_text(
                                    f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader"
                                )
                            except FloodWait:
                                await asyncio.sleep(5)
                            except Exception as e:
                                print(e)
                        logger.info(
                            f"URL To Video Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                    except Exception as e:
                        print(e)
                        await ef.edit(text=f"**Error** : {e}")

                else:
                    try:
                        try:
                            await update.message.reply_chat_action(
                                enums.ChatAction.UPLOAD_DOCUMENT
                            )
                        except:
                            pass
                        dvideo = await bot.send_document(
                            chat_id=update.message.chat.id,
                            document=new_download_directory,
                            caption=description,
                            thumb=thumb_image_path,
                            force_document=True,
                            reply_to_message_id=update.message.reply_to_message.id,
                            progress=progress_bar.progress_for_pyrogram,
                            progress_args=("**Uploading....**", start_time),
                        )

                        if (
                            CANCEL_PROCESS[update.message.chat.id]
                            and ef.id in CANCEL_PROCESS[update.message.chat.id]
                        ):
                            print("Process Cancelled ✅")
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                save_ytdl_json_path,
                                new_download_directory,
                            )
                            return
                        good = await bot.edit_message_text(
                            text="Successfully Uploaded",
                            chat_id=update.message.chat.id,
                            message_id=ef.id,
                            disable_web_page_preview=True,
                        )
                        await good.delete()
                        if Config.LOG_CHANNEL:
                            try:
                                cmvideo = await dvideo.copy(chat_id=Config.LOG_CHANNEL)
                                await cmvideo.reply_text(
                                    f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used url uploader"
                                )
                            except FloodWait:
                                await asyncio.sleep(5)
                            except Exception as e:
                                print(e)
                        logger.info(
                            f"URL To Video Uploaded  ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                    except Exception as e:
                        print(e)
                        await ef.edit(text=f"**Error** : {e}")

            await clear_server(
                user_id,
                tmp_directory_for_each_user,
                thumb_image_path,
                save_ytdl_json_path,
                new_download_directory,
            )


# ---------------- Folder Size ----------------#
def getFolderSize(folder):
    total_size = 0
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


# ------------------ Progress ----------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("xrprog"))
)
async def pogress_(bot, update):
    try:
        output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
        dl_size = getFolderSize(output_folder)
        dl_size = int(dl_size) / 2
        human_download = humanbytes(dl_size)

        await bot.answer_callback_query(
            callback_query_id=update.id,
            text=f"Downloaded : {human_download}",
            show_alert=True,
            cache_time=0,
        )
    except Exception as e:
        print(e)
