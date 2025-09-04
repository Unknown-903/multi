import asyncio
import datetime
import json
import logging
import os

from pyrogram import Client, filters

from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import COUNT, Sarita, clear_server, delete_msg
from plugins.others.playlist_uploader import playlist_uploader

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def flash_downloader(links, output_directory, new_file_name):
    output = output_directory + "/" + new_file_name + ".mkv"
    command = [
        "ffmpeg",
        "-i",
        links,
        "-map",
        "0",
        "-codec",
        "copy",
        output,
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if os.path.lexists(output):
        return output
    else:
        return None


@Client.on_callback_query(filters.regex("^flashdl"))
async def flash_url_up_(bot, update):
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
            text="⚠️ I am Flash Url Uploader ",
            reply_to_message_id=reply_msg.id,
        )
        return

    else:
        saved_file_path = reply_msg.text
        bc = await bot.send_message(
            chat_id=update.message.chat.id,
            text="🙂 Ruko Jara (रुको जरा)....",
            reply_to_message_id=reply_msg.id,
        )

    # ----------------- Codec Name --------------#
    yt_dlp_url = saved_file_path
    yt_dlp_username = None
    yt_dlp_password = None
    DEF_THUMB_NAIL_VID_S = os.environ.get(
        "https://telegra.ph/file/a483d3f10fdf831f94db8.jpg",
        "https://placehold.it/90x90",
    )
    int(os.environ.get("CHUNK_SIZE", 128))
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
        error_message = e_response
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

    else:
        await clear_server(user_id)
        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"🤦‍♂️ Video Formats not found!!",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            Print(e)
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
        pass
    format_list = []
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

            formats.get("format")

            audio_bit_rate = ""
            if "abr" in formats:
                audio_bit_rate = round(formats["abr"])
                audio_bit_rate = f"{audio_bit_rate}"

            yt_resolution = ""
            yt_resolution = formats.get("resolution")

            yt_acodec = "none"
            yt_acodec = formats.get("acodec")

            yt_vcodec = "none"
            yt_vcodec = formats.get("vcodec")

            if "filesize" in formats:
                humanbytes(formats["filesize"])

            # format_id, format_ext

            if yt_vcodec != "none":
                if (yt_acodec == "mp4a.40.2") or (yt_acodec != "none"):
                    format_list.append(format_id)

            if yt_resolution == "audio only":
                if (
                    (yt_acodec == "mp4a.40.2")
                    or (yt_acodec != "none")
                    and (format_ext != "mp4")
                ):
                    if format_ext == "webm":
                        format_ext = "opus"
                    format_list.append(format_id)
    else:
        format_id = response_json["format_id"]
        format_ext = response_json["ext"]
        format_list.append(format_id)

    description = ""
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]

    if duration is not None:
        video_duration = datetime.timedelta(seconds=duration)
        video_duration = f"{video_duration}"
    else:
        video_duration = ""

    if len(format_list) >= 1:
        try:
            selected_format = format_list[-1]
        except Exception as e:
            await clear_server(user_id, save_ytdl_json_path)
            logger.info(f"💡 Error: {e}")
            await update.message.reply(
                f"💡 Error: {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

    else:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ I am Unable to upload this link",
            reply_to_message_id=reply_msg.id,
        )
        return

    file_url = None
    if "formats" in response_json:
        for formats in response_json["formats"]:
            format_id = formats.get("format_id")
            if format_id == selected_format:
                file_url = formats.get("url")

    if url is None:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ UF Error: I am Unable to upload this link",
            reply_to_message_id=reply_msg.id,
        )
        return
    else:
        pass

    await delete_msg(bc)
    try:
        cd = await update.message.reply(
            "😉 Sabar Kro (सबर करो).....",
            reply_to_message_id=reply_msg.id,
        )
        stickerc = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAJvFWF7YaMKXvQe_dUiFKKhMQacz39rAALEAgACBG2gVsF1Ng9n9CrHHgQ",
        )
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            f"⚠️ Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return

    cfile_name = description[:60]
    try:
        video_file = await flash_downloader(
            file_url, Config.DOWNLOAD_LOCATION, cfile_name
        )
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            f"⚠️ Output Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        await delete_msg(cd, stickerc)
        return

    if video_file is None:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        await update.message.reply(
            "⚠️ Unknown Error Occurred",
            reply_to_message_id=reply_msg.id,
        )
        await delete_msg(cd, stickerc)
        return

    try:
        os.path.getsize(video_file)
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        await update.message.reply(
            f"⚠️ Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        await delete_msg(cd, stickerc)
        return

    await delete_msg(cd, stickerc)
    selected_format = "Others"
    premium_upload = "Yes"
    captions = None
    try:
        await playlist_uploader(
            bot, update, video_file, selected_format, captions, premium_upload
        )
        logger.info(
            f"Used Flash URL Uploader ✅. User {update.from_user.id} @{update.from_user.username}"
        )
    except:
        pass

    await clear_server(user_id, save_ytdl_json_path, video_file)
