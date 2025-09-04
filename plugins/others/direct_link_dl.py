import asyncio
import logging
import math
import os
import random
import time
from datetime import datetime

import aiohttp
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
from helpers.display_progress import Progress, TimeFormatter, humanbytes
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg

db = Database()

logger = logging.getLogger(__name__)

from plugins.others.playlist_uploader import playlist_uploader


def remove_unwanted(string):
    return (
        string.replace('"', "")
        .replace(":", " ")
        .replace(";", " ")
        .replace("?", " ")
        .replace("&", " ")
        .replace(",", " ")
        .replace("*", " ")
    )


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


CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
PROCESS_MAX_TIMEOUT = 3600
PORT = int(os.environ.get("PORT", 5000))
DEF_THUMB_NAIL_VID_S = os.environ.get(
    "https://telegra.ph/file/a483d3f10fdf831f94db8.jpg", "https://placehold.it/90x90"
)
TG_MAX_FILE_SIZE = 1998 * 1024 * 1024
HTTP_PROXY = ""


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("ndirectv"))
)
async def ndirectv_(bot, update):
    await delete_msg(update.message)
    ab = None
    ef = None
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
    yt_dlp_url = update.message.reply_to_message.text

    try:
        await bot.edit_message_text(
            text="Request Accepted",
            chat_id=update.message.chat.id,
            message_id=update.message.id,
        )
    except:
        pass

    if (await db.get_auto_rename(update.from_user.id)) is True:
        NUMBER_BUTTONS = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            #     yt_name = str(response_json.get("title"))
            new_name = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"✶ __File Name Limit allowed by Telegram is 60 Characters.__\n\n✶ Extension (eg. .mp4 .mp3) is Optional. If you want to add extension then Give Filename with extension (eg. `newfilename.mp4`)\n\n__**Now Send me new File Name**__ 👇",
                    reply_markup=NUMBER_BUTTONS,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                600,
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

        new_name = os.path.splitext(new_name)[0]
        new_name = new_name[:60]  # truncated_text = new_name[0:60]

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
            await clear_server(user_id, tmp_directory_for_each_user, thumb_image_path)
            return

        if new_names == "TimeUp":
            await update.message.reply(
                "⚠️ Process Time Out, Resend Again",
                reply_to_message_id=reply_msg.id,
            )
            await clear_server(user_id, thumb_image_path, tmp_directory_for_each_user)
            return

    custom_file_name = os.path.basename(yt_dlp_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(yt_dlp_url, timeout=600) as response:
            content_type = response.headers["Content-Type"]
            print(content_type)

            try:
                custom_file_name = response.headers.get("Content-Disposition").split(
                    "filename="
                )[1]
                try:
                    custom_file_name = remove_unwanted(custom_file_name)
                except:
                    pass
                print(custom_file_name)
            except:
                custom_file_name = custom_file_name
            await response.release()

    if "|" in yt_dlp_url:
        url_parts = yt_dlp_url.split("|")
        if len(url_parts) == 2:
            yt_dlp_url = url_parts[0]
            custom_file_name = url_parts[1]
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

    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    datetime.now()
    try:
        ab = await bot.edit_message_text(
            text=f"**Processing....**",
            chat_id=update.message.chat.id,
            message_id=update.message.id,
        )
    except:
        ab = await bot.send_message(
            text="**Processing....**",
            chat_id=update.message.chat.id,
            reply_to_message_id=reply_msg.id,
        )
    COUNT.append(user_id)
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            await download_coroutine(
                bot,
                session,
                yt_dlp_url,
                download_directory,
                update.message.chat.id,
                ab.id,
                c_time,
                update,
                reply_msg,
            )
            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ab.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(
                    user_id,
                    tmp_directory_for_each_user,
                    download_directory,
                    thumb_image_path,
                )
                return
        except Exception as err:
            print(err)
            await clear_server(
                user_id,
                tmp_directory_for_each_user,
                download_directory,
                thumb_image_path,
            )
            try:
                await bot.edit_message_text(
                    text=f"Process Cancelled ✅ \n\n⚠️ **Due to :** {err}",
                    chat_id=update.message.chat.id,
                    message_id=ab.id,
                )
            except:
                pass
            return False

    if os.path.exists(download_directory):
        ufile_name = os.path.basename(download_directory)
        description = f"**File Name :** `{ufile_name}`"
        try:
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
        file_size = TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError:
            try:
                download_directory = (
                    os.path.splitext(download_directory)[0] + "." + "mkv"
                )
                file_size = os.stat(download_directory).st_size
            except Exception as e:
                await clear_server(
                    user_id,
                    tmp_directory_for_each_user,
                    download_directory,
                    thumb_image_path,
                )
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ **Error :** {e}",
                    message_id=ef.id,
                )
                return
        if file_size > TG_MAX_FILE_SIZE:
            await delete_msg(ef)
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
                user_id,
                tmp_directory_for_each_user,
                new_download_directory,
                thumb_image_path,
            )
            #    await bot.edit_message_text(
            #        chat_id=update.message.chat.id,
            #        text="⚠️ Can't upload more than 2 GB file",
            #        message_id=ef.id
            #    )

            logger.info(
                f"URL Uploaded  ✅ For User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        else:
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
                        tmp_directory_for_each_user,
                        download_directory,
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
                            duration=duration,
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
                                new_download_directory,
                            )
                            return

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
                        await ef.edit(text=f"⚠️ **Error** : {e}")

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
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                new_download_directory,
                            )
                            return

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
                        await ef.edit(text=f"⚠️ **Error** : {e}")

            elif tg_send_type == "file":
                try:
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

                except Exception as e:
                    print(e)
                    await ef.edit(text=f"⚠️ **Error** : {e}")

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
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                new_download_directory,
                            )
                            return

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
                        await ef.edit(text=f"⚠️ **Error** : {e}")

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
                            await clear_server(
                                user_id,
                                tmp_directory_for_each_user,
                                thumb_image_path,
                                new_download_directory,
                            )
                            return

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
                        await ef.edit(text=f"⚠️ **Error** : {e}")

            else:
                logger.info("Did this happen? :\\")

            await clear_server(
                user_id,
                tmp_directory_for_each_user,
                thumb_image_path,
                new_download_directory,
            )
            if (await db.get_auto_rename(update.from_user.id)) is False:
                # text="__If your file is not opening, Then rename and add Extension ( ex. .mp4, .mp3, .pdf, .zip, etc )__",
                cpc = await bot.edit_message_text(
                    text=".",
                    chat_id=update.message.chat.id,
                    message_id=ef.id,
                    disable_web_page_preview=True,
                )
            else:
                cpc = await bot.edit_message_text(
                    text=".",
                    chat_id=update.message.chat.id,
                    message_id=ef.id,
                    disable_web_page_preview=True,
                )

            await delete_msg(cpc)

    else:
        await bot.edit_message_text(
            text="⚠️ **Error :** I can't upload this url ",
            chat_id=update.message.chat.id,
            message_id=ab.id,
            disable_web_page_preview=True,
        )


# ---------------------------------------------#
def is_cancelled(update, chat_id, message_id):
    cancelled = False
    if CANCEL_PROCESS[chat_id] and message_id in CANCEL_PROCESS[chat_id]:
        cancelled = True
    return cancelled


async def download_coroutine(
    bot, session, url, file_name, chat_id, message_id, start, update, reply_msg
):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=PROCESS_MAX_TIMEOUT) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]

        if "text" in content_type and total_length < 500:
            return await response.release()
        await bot.edit_message_text(
            chat_id,
            message_id,
            text="""**Downloading....**"""
            # **➩ URL :** {}\n
            # **➩ File Size :** {}""".format(url, humanbytes(total_length))
        )
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += CHUNK_SIZE
                now = time.time()
                diff = now - start
                # ---------------------------------------------#
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Cancel",
                                callback_data=(
                                    f"progcancel/{chat_id}/{message_id}/{update.from_user.id}"
                                ).encode("UTF-8"),
                            )
                        ]
                    ]
                )

                if is_cancelled(update, chat_id, message_id):
                    logger.info("Process Cancelled ✅ ")
                    try:
                        nicebots = await bot.edit_message_text(
                            f"**Process Cancelled ✅**", chat_id, message_id
                        )
                        await nicebots.delete()
                    except:
                        pass
                    await bot.stop_transmission()
                # --------------------------------------------#
                if round(diff % 7.00) == 0 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = (
                        round((total_length - downloaded) / speed) * 1000
                    )
                    elapsed_time + time_to_completion
                    time_to_complete = (
                        round(((total_length - downloaded) / speed)) * 1000
                    )
                    try:
                        current_message = """**Downloading....**\n
[{}{}]\n
**➩ Percentage :** {}%\n
➩ {} **Of** {}\n
**➩ Speed :** {}/s\n
**➩ Time Left :** {}""".format(
                            "".join(["●" for i in range(math.floor(percentage / 5))]),
                            "".join(
                                ["○" for i in range(20 - math.floor(percentage / 5))]
                            ),
                            round(percentage, 2),
                            humanbytes(downloaded),
                            humanbytes(total_length),
                            humanbytes(speed),
                            TimeFormatter(time_to_complete),
                        )
                        if current_message != display_message:
                            await bot.edit_message_text(
                                chat_id,
                                message_id,
                                text=current_message,
                                reply_markup=reply_markup,
                            )
                            display_message = current_message
                    except Exception as e:
                        logger.info(str(e))
        return await response.release()
