import asyncio
import logging
import os

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import Config
from database.database import Database
from plugins.audio import CANCEL_PROCESS, COUNT, delete_msg, msg_edit, pl_server_clear

db = Database()
from plugins.others.playlist_uploader import cli_call, playlist_uploader

logger = logging.getLogger(__name__)


def remove_space(string):
    return string.replace(" ", "")


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("spotify"))
)
async def spotify(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    bc = None

    """
    await update.message.reply("⚠️ Currently Disabled Spotify songs Downloader", reply_to_message_id=reply_msg.id)
    try:
        del Config.TIME_GAP_STORE[update.from_user.id]
    except Exception as e:
        logger.info(f"⚠️ Error Compress TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
    return
    """

    url = reply_msg.text
    try:
        url = remove_space(url)
    except:
        pass
    logger.info(
        f"☘️ Spotify link {url} sent By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    if not "spotify.com" in url:
        await update.message.reply(
            "⚠️ Send Spotify Song Link", reply_to_message_id=reply_msg.id
        )
        return

    if "playlist" in url:
        if update.from_user.id not in Config.AUTH_USERS:
            if not Config.SPOTIFY_PLAYLIST == "YES":
                await update.message.reply(
                    "⚠️ Spotify Playlist Download Option, Currently Disabled\n\nFor help Ask in @Helps_Group",
                    reply_to_message_id=reply_msg.id,
                )
                try:
                    del Config.TIME_GAP_STORE[update.from_user.id]
                except Exception as e:
                    logger.info(
                        f"⚠️ Error Compress TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                return

    if "episode" in url:
        await update.message.reply(
            "⚠️ Why did you send episode link 🤔\n\nSend me Only Spotify Track/Album/Artist/Playlist Link",
            reply_to_message_id=reply_msg.id,
        )
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error Spotify TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        return
    # ----------------- Format Buttons ------------#
    FORMAT_BUTTONS = ReplyKeyboardMarkup(
        [["MP3", "WAV", "FLAC"], ["M4A", "OPUS", "OGG"], ["Skip", "Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_format = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"The Best Available Audio Quality will be Downloaded\n\nSelect Audio Format in Below keyboard 👇",
                reply_markup=FORMAT_BUTTONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        # await ask_format.delete()
        await ask_format.request.delete()
        ask_format = ask_format.text
    except asyncio.TimeoutError:
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Process Time Out",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=reply_msg.id,
        )
        return

    if ask_format == "MP3":
        asked_format = "mp3"
    elif ask_format == "WAV":
        asked_format = "wav"
    elif ask_format == "FLAC":
        asked_format = "flac"
    elif ask_format == "M4A":
        asked_format = "m4a"
    elif ask_format == "OPUS":
        asked_format = "opus"
    elif ask_format == "OGG":
        asked_format = "ogg"
    elif ask_format == "Skip":
        asked_format = "mp3"
    elif ask_format == "Cancel":
        asked_format = "Cancel"
    else:
        asked_format = "Cancel"

    if asked_format == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    if not os.path.exists(output_folder):  # os.path.isdir
        os.makedirs(output_folder)

    progress_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Progress", callback_data=(f"drivprogre"))]]
    )
    bc = await bot.send_message(
        text="**Downloading....**",
        chat_id=update.message.chat.id,
        reply_markup=progress_markup,
        reply_to_message_id=reply_msg.id,
    )

    COUNT.append(user_id)
    final_cmd = f"spotdl {url} --output-format {asked_format} -o {output_folder}"

    out, err = await cli_call(final_cmd)

    try:
        ofiles = len(os.listdir(output_folder))
    except Exception as e:
        await pl_server_clear(user_id, output_folder)
        print(e)
        await msg_edit(bc, f"⚠️ **Error :** Something went wrong")
        return

    if err and ofiles < 1:
        try:
            reasons = f"{err}"
        except:
            reasons = f"{err}"
            reasons = reasons[:4000]
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ {reasons}")
        return

    if ofiles < 1:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Failed** to download url")
        logger.info(
            f"⚠️ Failed to download url {url} For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if getFolderSize(output_folder) < 25:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Failed** to Download URL")
        logger.info(
            f"⚠️ Failed to Download URL {url} For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    try:
        files_folder = list_files(output_folder, [])
    except Exception as e:
        await pl_server_clear(user_id, output_folder)
        print(e)
        await msg_edit(bc, f"⚠️ **Error :** {e}")
        return

    try:
        cance_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Cancel",
                        callback_data=(
                            f"progcancel/{update.message.chat.id}/{reply_msg.id}/{update.from_user.id}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        cd = await bc.edit(f"**Songs Are Uploading....**", reply_markup=cance_markup)
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                f"**Songs Are Uploading....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        await msg_edit(cd, f"Process Cancelled ✅")
        print("Process Cancelled ✅")
        await pl_server_clear(user_id, output_folder)
        return

    numbers = None
    for i, single_file in enumerate(files_folder):
        if os.path.exists(single_file):
            if single_file.upper().endswith(
                ("MP3", "M4A", "WAV", "FLAC", "OPUS", "OGG")
            ):
                real_name = os.path.basename(single_file)
                try:
                    metadata = extractMetadata(createParser(single_file))
                except:
                    metadata = None
                if metadata and metadata.has("title"):
                    title = metadata.get("title")
                    ext = f"{asked_format}"
                    real_name = f"{title}.{ext}"

                splited_name = real_name
                single_files = output_folder + "/" + f"{splited_name}"

                try:
                    os.rename(single_file, single_files)
                except:
                    single_files = single_file

                try:
                    numbers = f"{i}"
                    selected_format = f"GoogleDrive/{numbers}"
                    await playlist_uploader(bot, update, single_files, selected_format)
                except Exception as e:
                    try:
                        await update.message.reply(
                            f"⚠️ **Error :** {single_files}\n\nFor File : __{single_files}__",
                            reply_to_message_id=reply_msg.id,
                        )
                        print(e)
                    except:
                        pass
                    continue

    await delete_msg(cd)
    await pl_server_clear(user_id, output_folder)
    if numbers is not None:
        await bot.send_message(
            update.message.chat.id,
            "All Songs Are Uploaded ✅",
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f"All Songs Are Uploaded ✅  By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    else:
        await bot.send_message(
            update.message.chat.id,
            "⚠️ Something went wrong \n\nSend me only Track/Album/Artist/Playlist Link",
            disable_web_page_preview=True,
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f"⚠️ Unknown Error For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )


# ----------------- File List -----------------#
def list_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return list_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst


# ---------------- Folder Size ----------------#
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size
