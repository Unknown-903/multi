import asyncio
import datetime
import json
import logging
import os
import time

import requests
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import COUNT, Sarita, clear_server, delete_msg

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def remove_space(string):
    return string.replace(" ", "")


# another
def space_remove(string):
    return "".join(string.split())


def DetectFileSize(url):
    r = requests.get(url, allow_redirects=True, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    return total_size


def DownLoadFile(url, file_name, chunk_size, client, ud_type, message_id, chat_id):
    if os.path.exists(file_name):
        os.remove(file_name)
    if not url:
        return file_name
    r = requests.get(url, allow_redirects=True, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    downloaded_size = 0
    with open(file_name, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
                downloaded_size += chunk_size
            if client is not None:
                if ((total_size // downloaded_size) % 5) == 0:
                    time.sleep(0.3)
                    try:
                        client.edit_message_text(
                            chat_id,
                            message_id,
                            text="{}: {} of {}".format(
                                ud_type,
                                humanbytes(downloaded_size),
                                humanbytes(total_size),
                            ),
                        )
                    except:
                        pass
    return file_name


@Client.on_callback_query(filters.regex("^yonlyyt"))
async def only_youtube(bot, update):
    await delete_msg(update.message)
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id

    text_url = reply_msg.text.split(None, 1)[0]
    if "playlist?list=" in text_url:
        await update.message.reply(
            "⚠️ I don't support Playlist\n\n👉 For YouTube Playlist Downloading Use @YoutubePlaylistDLBot",
            reply_to_message_id=reply_msg.id,
        )
        return

    if reply_msg.text.startswith("magnet:?"):
        await update.message.reply(
            "⚠️ I am not a magnet link downloader\n\n👉 Use @MagnetLinkDLBot",
            reply_to_message_id=reply_msg.id,
        )
        return

    if "mega.nz" in reply_msg.text:
        await update.message.reply(
            "⚠️ Currently mega.nz links not support",
            reply_to_message_id=reply_msg.id,
        )
        return

    if "seeder.cc" in reply_msg.text:
        await update.message.reply(
            "⚠️ Currently seeder.cc links not support\n\n👉 Use public leech groups",
            reply_to_message_id=reply_msg.id,
        )
        return

    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if os.path.isdir(download_path):
        await update.message.reply(
            "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__",
            reply_to_message_id=reply_msg.id,
        )
        return

    if len(COUNT) > Config.NUMBER:
        ab = await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"**⚠️ Already {Config.NUMBERS} Process Running**\n\n👉 Try again after a few minutes",
            reply_to_message_id=reply_msg.id,
        )
        return

    #  if user_id in COUNT:
    #      ab = await bot.send_message(
    #          chat_id=update.message.chat.id,
    #          text="Already Your 1 Request Processing",
    #          reply_to_message_id=reply_msg.id
    #      )
    #      return

    if reply_msg.media:
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="⚠️ I am YouTube Music Downloader ",
            reply_to_message_id=reply_msg.id,
        )
        return

    else:
        saved_file_path = reply_msg.text
        bc = await bot.send_message(
            chat_id=update.message.chat.id,
            text="**Processing....**",
            reply_to_message_id=reply_msg.id,
        )
    #   if not "youtu" in saved_file_path:
    #       await bc.edit("⚠️ Send me Only YouTube Link")
    #       await clear_server(user_id, saved_file_path)
    #       return

    # ----------------- Codec Name --------------#
    yt_dlp_url = saved_file_path
    yt_dlp_username = None
    yt_dlp_password = None
    DEF_THUMB_NAIL_VID_S = os.environ.get(
        "https://telegra.ph/file/a483d3f10fdf831f94db8.jpg",
        "https://placehold.it/90x90",
    )
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    FORMAT_SELECTION = "**File Name :** `{}`"
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

    HTTP_PROXY = ""
    url = yt_dlp_url
    try:
        url = remove_space(url)
        print(url)
    except:
        pass

    if "youtu" in url:
        if url in Sarita.INVALID_LINKS:
            logger.info(
                f"⚠️ Invalid YouTube Link. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await bc.edit("⚠️ Invalid YouTube Link\n\n👉 YouTube video id not found")
            return

    # ------------------ For Json File ------------#

    if HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--proxy",
            HTTP_PROXY,
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
        ]

    if "hotstar" in url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")

    if yt_dlp_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(yt_dlp_username)
    if yt_dlp_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(yt_dlp_password)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if e_response and "nonnumeric port" not in e_response:
        SET_CUSTOM_USERNAME_PASSWORD = ""
        error_message = e_response.replace(
            "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call yt-dlp with the --verbose flag and include its complete output.",
            "",
        )
        if "This video is only available for registered users." in error_message:
            error_message += SET_CUSTOM_USERNAME_PASSWORD

        await clear_server(user_id)
        error_message = error_message[0:4000]
        await bc.edit(
            text=f"⚠️ I can't upload file from this url\n\n👉 {error_message}",
        )
        logger.info(
            f" ⚠️ I can't upload file from this url {error_message}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return False

    if t_response:
        try:
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)
        except Exception as e:
            await clear_server(user_id)
            await bc.edit(text=f"⚠️ **Error :** {e}")
            return

        if not os.path.exists(
            Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
        ):
            os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

        save_ytdl_json_path = (
            Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".json"
        )
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        # ------------------ Format Selection ----------------#

        if "fulltitle" in response_json:
            butonname = response_json["fulltitle"][0:30]
        else:
            butonname = "unknown"

        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = ""
                format_ext = formats.get("ext")
                approx_file_size = ""
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                cb_string_video = "vniceytdl/{}/{}/{}".format(
                    "video", format_id, format_ext
                )
                cb_string_file = "vniceytdl/{}/{}/{}".format(
                    "file", format_id, format_ext
                )
                if format_string is not None and not "audio only" in format_string:
                    yfilter = await db.get_yfilter(update.from_user.id)
                    if format_ext == f"{yfilter}":
                        ikeyboard = [
                            InlineKeyboardButton(
                                ""
                                + "🎬 "
                                + format_string
                                + " - "
                                + approx_file_size
                                + " "
                                + format_ext
                                + " ",
                                callback_data=(cb_string_video).encode("UTF-8"),
                            )
                        ]

                        inline_keyboard.append(ikeyboard)
                    if yfilter == "all":
                        ikeyboard = [
                            InlineKeyboardButton(
                                ""
                                + "🎬 "
                                + format_string
                                + " - "
                                + approx_file_size
                                + " "
                                + format_ext
                                + " ",
                                callback_data=(cb_string_video).encode("UTF-8"),
                            )
                        ]

                        inline_keyboard.append(ikeyboard)

                else:
                    ikeyboard = [
                        InlineKeyboardButton(
                            f"{butonname}" + " " + approx_file_size + " " + format_ext,
                            callback_data=(cb_string_file).encode("UTF-8"),
                        ),
                    ]
                    inline_keyboard.append(ikeyboard)
            if duration is not None:
                "vniceytdl/{}/{}/{}".format("audio", "64k", "mp3")
                "vniceytdl/{}/{}/{}".format("audio", "128k", "mp3")
                "vniceytdl/{}/{}/{}".format("audio", "192k", "mp3")
                "vniceytdl/{}/{}/{}".format("audio", "320k", "mp3")
                # inline_keyboard.append([
                #    InlineKeyboardButton(
                #        "🎵 MP3 " + "64k", callback_data=cb_string_64.encode("UTF-8")),
                #    InlineKeyboardButton(
                #        "🎵 MP3 " + "192k", callback_data=cb_string_192.encode("UTF-8")),
                # ])
                inline_keyboard.append(
                    [
                        InlineKeyboardButton(
                            "🎵 MP3 " + "128k", callback_data="oytsong"
                        ),
                        InlineKeyboardButton(
                            "🎵 MP3 " + "320k", callback_data="oytsong"
                        ),
                    ]
                )

        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "vniceytdl/{}/{}/{}".format("file", format_id, format_ext)
            cb_string_video = "vniceytdl/{}/{}/{}".format(
                "video", format_id, format_ext
            )
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        "Upload via ytdl",
                        callback_data=(cb_string_file).encode("UTF-8"),
                    )
                ]
            )
            cb_string_file = "ndirectv/{}/{}/{}".format("file", format_id, format_ext)
            cb_string_video = "ndirectv/{}/{}/{}".format("video", format_id, format_ext)
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        "Upload via aiohttp",
                        callback_data=(cb_string_file).encode("UTF-8"),
                    )
                ]
            )
        inline_keyboard.append(
            [
                InlineKeyboardButton("Cancel", callback_data="nytcancl"),
            ]
        )
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        thumbnail_image = DEF_THUMB_NAIL_VID_S
        if "thumbnail" in response_json:
            if response_json["thumbnail"] is not None:
                response_json["thumbnail"]
                thumbnail_image = response_json["thumbnail"]
        try:
            thumb_image_path = DownLoadFile(
                thumbnail_image,
                Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".webp",
                CHUNK_SIZE,
                None,  # bot,
                "Downloading...",
                update.message.id,
                update.message.chat.id,
            )
            if os.path.exists(thumb_image_path):
                im = Image.open(thumb_image_path).convert("RGB")
                im.save(thumb_image_path.replace(".webp", ".jpg"), "jpeg")
            else:
                thumb_image_path = None
        except:
            pass

        try:
            await bc.delete()
        except:
            pass

        description = ""
        if "fulltitle" in response_json:
            description = response_json["fulltitle"][0:1021]

        if duration is None:
            duration = 0
        video_duration = datetime.timedelta(seconds=duration)
        video_duration = f"{video_duration}"

        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=FORMAT_SELECTION.format(description)
                + f"\n\n⏰ **Total Duration -** {video_duration}",
                reply_markup=reply_markup,
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, save_ytdl_json_path)
            yfilters = await db.get_yfilter(update.from_user.id)
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"🤦‍♂️ I am not finding **{yfilters}** Files\n\n👉 __So, Now Go to__ /usettings __And Change YTDL Filter, Set YTDL Filter to__ **all**",
                parse_mode="md",
                reply_to_message_id=reply_msg.id,
            )

    else:
        inline_keyboard = []
        cb_string_file = "ndirectv/{}/{}/{}".format("file", "LFO", "NONE")
        cb_string_video = "ndirectv/{}/{}/{}".format("video", "OFL", "ENON")
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    "Upload via aiohttp", callback_data=(cb_string_file).encode("UTF-8")
                ),
            ]
        )
        inline_keyboard.append(
            [
                InlineKeyboardButton("Cancel", callback_data="nytcancl"),
            ]
        )
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=FORMAT_SELECTION.format(""),
            reply_markup=reply_markup,
            parse_mode="html",
            reply_to_message_id=reply_msg.id,
        )
