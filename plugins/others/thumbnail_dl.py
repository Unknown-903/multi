import asyncio
import json
import logging
import os
import time

import requests
from PIL import Image
from pyrogram import Client, enums, filters

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


@Client.on_callback_query(filters.regex("^thumbdl"))
async def thumbdl_(bot, update):
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
        await bc.edit(
            text=f"⚠️ I can't upload file from this url",
        )
        logger.info(
            f" ⚠️ I can't upload file from this url. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
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
            pass

        thumbnail_image = DEF_THUMB_NAIL_VID_S
        if "thumbnail" in response_json:
            if response_json["thumbnail"] is not None:
                response_json["thumbnail"]
                thumbnail_image = response_json["thumbnail"]

        thumb_image_path = None
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
            new_file_name = Config.DOWNLOAD_LOCATION + "/" + "yt_thumb.jpeg"
            os.rename(thumb_image_path, new_file_name)
        except Exception as e:
            print(e)

        try:
            cd = await bc.edit(f"**Uploading....**")
        except:
            await delete_msg(bc)
            try:
                cd = await update.message.reply(
                    "**Uploading....**", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, save_ytdl_json_path, thumb_image_path)
                logger.info(
                    f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

        try:
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            except:
                pass
            diksha = await bot.send_document(
                chat_id=update.message.chat.id,
                document=new_file_name,
                reply_to_message_id=reply_msg.id,
            )
        except Exception:
            pass
        #  print(e)

        try:
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
            except:
                pass
            await bot.send_photo(
                chat_id=update.message.chat.id,
                photo=new_file_name,
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            print(e)

        await delete_msg(cd)
        await clear_server(user_id, save_ytdl_json_path)

    else:
        await clear_server(user_id, save_ytdl_json_path)
        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"🤦‍♂️ Something went Wrong !!",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            print(e)
        return
