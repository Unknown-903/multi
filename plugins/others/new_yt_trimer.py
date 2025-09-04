import asyncio
import datetime
import json
import logging
import os

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import COUNT, Sarita, clear_server, delete_msg
from plugins.audio_helper import Ranjan
from plugins.others.playlist_uploader import playlist_uploader
from plugins.processors import Chitranjan as CH

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

async def video_process(
    video_file, output_directory, start_time, end_time, new_file_name
):
    output = output_directory + "/" + new_file_name + f"video.mkv"
    subtitle_option = await Ranjan.fix_subtitle_codec(video_file)
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-ss",
        f"{start_time}",
        "-to",
        f"{end_time}",
        "-map",
        "0",
        "-c",
        "copy",
        output,
    ]
    for option in subtitle_option:
        command.insert(-1, option)
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.lexists(output):
        return output
    else:
        return None

async def audio_process(
    video_file,
    output_directory,
    start_time,
    end_time,
    new_file_name,
    extension,
):
    out_put_file_name = output_directory + "/" + new_file_name + f"audio.{extension}"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-ss",
        f"{start_time}",
        "-to",
        f"{end_time}",
        "-acodec",
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
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def va_merge(video_file, audio_file, output_directory, new_file_name):
    out_put_file_name = output_directory + "/" + new_file_name + ".mkv"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-i",
        audio_file,
        "-map",
        "0:0",
        "-map",
        "1:0",
        "-map",
        "0:1?",
        "-map",
        "0:2?",
        "-map",
        "0:3?",
        "-map",
        "0:4?",
        "-disposition:a:0",
        "default",
        "-disposition:a:1",
        "none",
        "-shortest",
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
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

@Client.on_callback_query(filters.regex("^ooyttrim"))
async def trimmd_only(bot, update):
    await delete_msg(update.message)
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id

    save_ytdl_json_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".json"
    )
    await clear_server(user_id, save_ytdl_json_path)

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
    logger.info(
        f"✏️ {yt_dlp_url} 👉 User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    yt_dlp_username = None
    yt_dlp_password = None
    DEF_THUMB_NAIL_VID_S = os.environ.get(
        "https://telegra.ph/file/a483d3f10fdf831f94db8.jpg",
        "https://placehold.it/90x90",
    )
    int(os.environ.get("CHUNK_SIZE", 128))
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

    else:
        await clear_server(user_id)
        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"🤦‍♂️ Formats not found!!",
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
        butonname = response_json["fulltitle"][0:10]
    else:
        butonname = "Unknown"

    audio_lists = []
    video_lists = []
    duration = None
    if "duration" in response_json:
        duration = response_json["duration"]
    if "formats" in response_json:
        for formats in response_json["formats"]:
            format_id = formats.get("format_id")
            formats.get("format_note")

            format_ext = "Unknown"
            format_ext = formats.get("ext")

            yt_acodec = "none"
            yt_acodec = formats.get("acodec")

            format_string = formats.get("format_note")
            if format_string is None:
                format_string = formats.get("format")

            audio_bit_rate = ""
            if "abr" in formats:
                audio_bit_rate = round(formats["abr"])
                audio_bit_rate = f"{audio_bit_rate}"

            yt_resolution = ""
            yt_resolution = formats.get("resolution")

            approx_file_size = ""
            if "filesize" in formats:
                approx_file_size = humanbytes(formats["filesize"])

            if yt_resolution == "audio only":
                if (yt_acodec != "none") and (format_ext != "mp4"):
                    if format_ext == "webm":
                        format_ext = "opus"
                    akeyboard = [f"🎵 {format_id} {format_ext} {audio_bit_rate}k {approx_file_size}"]                                                    
                    audio_lists.append(akeyboard)

            if format_string is not None and not "audio only" in format_string:
                yfilter = await db.get_yfilter(update.from_user.id)
                if format_ext == f"{yfilter}":
                    if (format_ext == "Unknown") or (format_ext is None):
                        format_ext = "mkv"
                    vkeyboard = [f"🎬 {format_id} {format_ext} {format_string} {approx_file_size}"]                                                    
                    video_lists.append(vkeyboard)
                    
                if yfilter == "all":
                    if (format_ext == "Unknown") or (format_ext is None):
                        format_ext = "mkv"
                    vkeyboard = [f"🎬 {format_id} {format_ext} {format_string} {approx_file_size}"]                                                    
                    video_lists.append(vkeyboard)

            else:
                if (format_ext == "Unknown") or (format_ext is None):
                    format_ext = "mkv"
                vkeyboard = [f"🎬 {format_id} {format_ext} {butonname} {approx_file_size}"]                                                    
                video_lists.append(vkeyboard)

    else:
        await clear_server(user_id, save_ytdl_json_path)
        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ Formats not found!!",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            Print(e)
        return

    if audio_lists is not None:
        audio_markup = ReplyKeyboardMarkup(audio_lists, resize_keyboard=True, one_time_keyboard=True,)
    else:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ Audio is not found in this link",
            reply_to_message_id=reply_msg.id,
        )
        return

    if video_lists is not None:
        video_markup = ReplyKeyboardMarkup(video_lists, resize_keyboard=True, one_time_keyboard=True,)
    else:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ Video is not found in this link",
            reply_to_message_id=reply_msg.id,
        )
        return

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
        video_data = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**File Name :** {description}\n\n⏰ **Total Duration -** {video_duration}",
                reply_markup=video_markup,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        # await video_data.delete()
        await video_data.request.delete()
        video_data = video_data.text
    except asyncio.TimeoutError:
        await clear_server(user_id, save_ytdl_json_path)
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Process Time Out",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=reply_msg.id,
        )
        return
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path)
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"{e}\n\n🤦‍♂️ Something Went Wrong!! ",
            reply_to_message_id=reply_msg.id,
        )

    try:
        audio_data = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**File Name :** {description}\n\n⏰ **Total Duration -** {video_duration}",
                reply_markup=audio_markup,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        # await audio_data.delete()
        await audio_data.request.delete()
        audio_data = audio_data.text
    except asyncio.TimeoutError:
        await clear_server(user_id, save_ytdl_json_path)
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Process Time Out",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=reply_msg.id,
        )
        return
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path)
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"{e}\n\n🤦‍♂️ Something Went Wrong!! ",
            reply_to_message_id=reply_msg.id,
        )

    vsplited_data = video_data.split(" ")
    vformat_id, vformat_ext = (vsplited_data[1], vsplited_data[2],)
    #logger.info(f"Video Format id: {vformat_id}\n\nFormat ext: {vformat_ext}")

    asplited_data = audio_data.split(" ")
    aformat_id, aformat_ext = (asplited_data[1], asplited_data[2],)
    #logger.info(f"Audio Format id: {aformat_id}\n\nFormat ext: {aformat_ext}")

    if user_id not in COUNT:
        COUNT.append(user_id)

    video_url = None
    if "formats" in response_json:
        for formats in response_json["formats"]:
            vvformat_id = formats.get("format_id")
            if vvformat_id == vformat_id:
                video_url = formats.get("url")

    if video_url is None:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ VU Error: I am Unable to Trim this link",
            reply_to_message_id=reply_msg.id,
        )
        return
    else:
        pass

    audio_url = None
    if "formats" in response_json:
        for formats in response_json["formats"]:
            aaformat_id = formats.get("format_id")
            if aaformat_id == aformat_id:
                audio_url = formats.get("url")

    if audio_url is None:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ AU Error: I am Unable to Trim this link",
            reply_to_message_id=reply_msg.id,
        )
        return
    else:
        pass

    STARTING_TIME = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    try:
        start_time = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**File Name :** {description} \n\n⏰ **Total Video duration: ** `{video_duration}`\n\n**✶ Send me Start Time of video**",
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
            ccc = await update.message.reply(".", reply_markup=ReplyKeyboardRemove())
            await ccc.delete()
        except:
            pass
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ Process Time Out",
            reply_to_message_id=reply_msg.id,
        )
        return

    if start_time.text == "Cancel":
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "Process Cancelled ✅",
            reply_to_message_id=reply_msg.id,
        )
        return
    else:
        start_time = f"{start_time.text}"

    ENDING_TIME = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    try:
        end_time = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**File Name :** {description}\n\n⏰ **Total Video duration: ** `{video_duration}`\n\nStart Time:  `{start_time}`\nEnd Time: ..........\n\n**✶ Send me End Time of video**",
                reply_markup=ENDING_TIME,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await end_time.delete()
            await end_time.request.delete()
        except:
            pass
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=ReplyKeyboardRemove())
            await ccc.delete()
        except:
            pass
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "⚠️ Process Time Out",
            reply_to_message_id=reply_msg.id,
        )
        return

    if end_time.text == "Cancel":
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            "Process Cancelled ✅",
            reply_to_message_id=reply_msg.id,
        )
        return
    else:
        end_time = f"{end_time.text}"

    cfile_name = description[:60]

#----------------- Video ----------------#
    msg = await update.message.reply(
        f"**Downloading Video....**",
        reply_to_message_id=reply_msg.id,
    )
    '''
    try:
        video_file = await video_process(
            video_url, Config.DOWNLOAD_LOCATION, start_time, end_time, cfile_name
        )
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path)
        await update.message.reply(
            f"⚠️ V Output Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return
    '''

    output_directory = f"{Config.DOWNLOAD_PATH}/{user_id}/{cfile_name}video.mkv"
    commands = [
        "ffmpeg",
        "-i",
        video_url,
        "-ss",
        f"{start_time}",
        "-to",
        f"{end_time}",
        "-map",
        "0",
        "-c",
        "copy",
        output_directory,
    ]
    texts = "Downloading YT Video file...."
    bool, video_file, msg = await CH.command_execute(bot, update, msg, commands, output_directory, duration, texts)
    if bool:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        return

    if video_file is None:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        await update.message.reply(
            "⚠️ V Unknown Error Occurred",
            reply_to_message_id=reply_msg.id,
        )
        return

    try:
        os.path.getsize(video_file)
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        await update.message.reply(
            f"⚠️ V Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return

    await msg.delete()
#----------------- Audio ----------------#
    msg = await update.message.reply(
        f"**Downloading Audio....**",
        reply_to_message_id=reply_msg.id,
    )
    '''
    try:
        audio_file = await audio_process(
            audio_url, Config.DOWNLOAD_LOCATION, start_time, end_time, cfile_name, aformat_ext
        )
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        await update.message.reply(
            f"⚠️ A Output Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return
    '''
    oa_directory = f"{Config.DOWNLOAD_PATH}/{user_id}/{cfile_name}audio.{aformat_ext}"
    commands = [
        "ffmpeg",
        "-i",
        audio_url,
        "-ss",
        f"{start_time}",
        "-to",
        f"{end_time}",
        "-acodec",
        "copy",
        oa_directory,
    ]
    texts = "Downloading YT Audio file...."
    bool, audio_file, msg = await CH.command_execute(bot, update, msg, commands, output_directory, duration, texts)
    if bool:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        return
    if audio_file is None:
        await clear_server(user_id, save_ytdl_json_path, video_file, audio_file)
        await update.message.reply(
            "⚠️ A Unknown Error Occurred",
            reply_to_message_id=reply_msg.id,
        )
        return

    try:
        os.path.getsize(audio_file)
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file, audio_file)
        await update.message.reply(
            f"⚠️ A Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return

    await msg.delete()
#----------------- Audio ----------------#
    msg = await update.message.reply(
        f"**Merging Now....**",
        reply_to_message_id=reply_msg.id,
    )    
    '''
    try:
        va_file = await va_merge(video_file, audio_file, Config.DOWNLOAD_LOCATION, cfile_name)
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file, audio_file)
        await update.message.reply(
            f"⚠️ VA Output Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return
    '''

    directory = f"{Config.DOWNLOAD_PATH}/{cfile_name}.mkv"
    commands = [
        "ffmpeg",
        "-i",
        video_file,
        "-i",
        audio_file,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c",
        "copy",
        "-shortest",
        directory,
    ]
    texts = "Now Merging...."
    bool, va_file, msg = await CH.command_execute(bot, update, msg, commands, directory, duration, texts)
    if bool:
        await clear_server(user_id, save_ytdl_json_path, video_file)
        return

    if va_file is None:
        await clear_server(user_id, save_ytdl_json_path, video_file, audio_file, va_file)
        await update.message.reply(
            "⚠️ VA Unknown Error Occurred",
            reply_to_message_id=reply_msg.id,
        )
        return

    try:
        os.path.getsize(va_file)
    except Exception as e:
        await clear_server(user_id, save_ytdl_json_path, video_file, audio_file, va_file)
        await update.message.reply(
            f"⚠️ VA Error: {e}",
            reply_to_message_id=reply_msg.id,
        )
        return

    await msg.delete()
    selected_format = "Others"
    premium_upload = "Yes"
    captions = None
    try:
        await playlist_uploader(
            bot, update, va_file, selected_format, captions, premium_upload
        )
        logger.info(
            f"Used YT Trimmer ✅. User {update.from_user.id} @{update.from_user.username}"
        )
    except:
        pass

    await clear_server(user_id, save_ytdl_json_path, video_file, audio_file, va_file)
