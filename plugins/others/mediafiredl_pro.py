import logging
import math
import os

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import CANCEL_PROCESS, COUNT, delete_msg, msg_edit, pl_server_clear

db = Database()
from plugins.others.playlist_uploader import playlist_uploader

logger = logging.getLogger(__name__)

from asyncio import get_running_loop
from functools import partial

from mediafiredl import MediafireDL

loop = get_running_loop()

mf_file_sizes = 0


def mediafire_downloads(url, output_folder):
    try:
        output_file = MediafireDL.Download(url, output=output_folder)
        errors = None
    except Exception as e:
        output_file = None
        errors = f"{e}"

    return output_file, errors


def calulate_size(url):
    try:
        file_size = MediafireDL.GetFileSize(url)
        errors = None
    except Exception as e:
        file_size = None
        errors = f"{e}"

    return file_size, errors


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("newmfdl"))
)
async def mediafiredwn(bot, update):
    await delete_msg(update.message)
    global mf_file_sizes
    logger.info(
        f"☘️ Sent Mediafire link new Function. User {update.from_user.id} @{update.from_user.username}"
    )
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    bc = None

    url = reply_msg.text
    if "?dkey=" in url:
        text_url = url.split("?dkey=")
        url = text_url[0]

    output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    if not os.path.exists(output_folder):  # os.path.isdir
        os.makedirs(output_folder)

    progress_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Progress", callback_data=(f"nnnmrog"))]]
    )
    bc = await bot.send_message(
        text="**Downloading....**",
        chat_id=update.message.chat.id,
        reply_markup=progress_markup,
        reply_to_message_id=reply_msg.id,
    )
    try:
        file_names = url.split("/")[-2]
    except Exception as e:
        print(e)
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **File Name Error :** {e}")
        return

    try:
        file_size, errors = await loop.run_in_executor(
            None, partial(calulate_size, url)
        )
    except Exception as e:
        print(e)
        mf_file_sizes = f"0"
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Size Error :** {e}")
        return

    if file_size is None:
        if errors is None:
            e = "🤔 Something went Wrong!!!"
        else:
            e = f"{errors}"
        mf_file_sizes = f"0"
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Output Size Error :** {e}")
        return

    mf_file_sizes = file_size
    output_file = output_folder + f"{file_names}"

    COUNT.append(user_id)
    try:
        output_file, errors = await loop.run_in_executor(
            None, partial(mediafire_downloads, url, output_folder)
        )
    except Exception as e:
        print(e)
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Error :** {e}")
        return

    if output_file is None:
        await pl_server_clear(user_id, output_folder)
        if errors is None:
            e = "🤔 Something went Wrong!!!"
        else:
            e = f"{errors}"
        await msg_edit(bc, f"⚠️ **Output Error :** {e}")
        return

    if getFolderSize(output_folder) < 10:
        await pl_server_clear(user_id, output_folder, output_file)
        await msg_edit(
            bc, f"⚠️ **Failed** to Download URL\n\nFile size is less than 10 bites"
        )
        logger.info(
            f"⚠️ Failed to Download URL {url} For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    try:
        os.path.getsize(output_file)
    except Exception as e:
        print(e)
        await pl_server_clear(user_id, output_folder, output_file)
        await msg_edit(bc, f"⚠️ **Output Error :** {e}")
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
        cd = await bc.edit(f"**Files Are Uploading....**", reply_markup=cance_markup)
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                f"**Files Are Uploading....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder, output_file)
            print(e)
            return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        await msg_edit(cd, f"Process Cancelled ✅")
        print("Process Cancelled ✅")
        await pl_server_clear(user_id, output_folder, output_file)
        return

    try:
        selected_format = f"Others"
        premium_upload = "Yes"
        captions = None
        await playlist_uploader(
            bot, update, output_file, selected_format, captions, premium_upload
        )
        logger.info(
            f"Mediafire Link Uploaded ✅. User {update.from_user.id} @{update.from_user.username}"
        )
    except Exception as e:
        try:
            await update.message.reply(
                f"⚠️ **U Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            print(e)
        except:
            pass

    await delete_msg(cd)
    await pl_server_clear(user_id, output_folder, output_file)


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


# ---------------- Progress ------------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("nnnmrog"))
)
async def mfpjjjjt(bot, update):
    global mf_file_sizes
    try:
        output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
        dl_size = getFolderSize(output_folder)
        # download_size = humanbytes(dl_size)
    except Exception as e:
        dl_size = f"0"
        print(e)

    download_size = round(dl_size / 1024 / 1024, 2)

    try:
        requested_ss = int(mf_file_sizes)
        requested = round(requested_ss / 1024 / 1024, 2)
        downloaded = download_size

        total_perc = int(downloaded) * int(100) / requested

        human_dl_size = humanbytes(dl_size)
        human_req_size = humanbytes(requested_ss)

        percentage = round(total_perc, 2)
        progressbar = "[{0}{1}]".format(
            "".join(["■" for i in range(math.floor(total_perc / 10))]),
            "".join(["□" for i in range(10 - math.floor(total_perc / 10))]),
        )
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text=f"Done: {human_dl_size} of {human_req_size}\n\n{progressbar} {percentage}%",
            show_alert=True,
            cache_time=0,
        )
    except:
        try:
            await bot.answer_callback_query(
                callback_query_id=update.id,
                text=f"Processing....",
                show_alert=True,
                cache_time=0,
            )
        except:
            pass


# https://github.com/Gann4Life/mediafiredl
