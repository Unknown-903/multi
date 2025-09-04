import logging
import math
import os
import time
from datetime import datetime

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import TimeFormatter, humanbytes
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg

db = Database()

logger = logging.getLogger(__name__)


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


CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
PROCESS_MAX_TIMEOUT = 3600
TG_MAX_FILE_SIZE = 2097152000


async def download_link(bot, update):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    tmp_directory_for_each_user = None
    download_directory = None
    tmp_directory_for_each_user = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    )
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)

    url = reply_msg.text
    custom_file_name = os.path.basename(url)
    if not url.startswith("http"):
        try:
            await update.message.edit("⚠️ It's not a valid url")
        except:
            try:
                await update.message.reply(
                    "⚠️ It's not a valid url", reply_to_message_id=reply_msg.id
                )
            except Exception as e:
                print(e)
        await clear_server(user_id, tmp_directory_for_each_user)
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=600) as response:
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

    download_directory = tmp_directory_for_each_user + "/" + custom_file_name

    datetime.now()
    try:
        ab = await bot.edit_message_text(
            text=f"**Downloading...**",
            chat_id=update.message.chat.id,
            message_id=update.message.id,
        )
    except:
        try:
            ab = await bot.send_message(
                text="**Downloading...**",
                chat_id=update.message.chat.id,
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            print(e)
            await clear_server(user_id, tmp_directory_for_each_user, download_directory)
            return
    COUNT.append(user_id)
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            await download_coroutine(
                bot,
                session,
                url,
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
                    user_id, tmp_directory_for_each_user, download_directory
                )
                return
        except Exception as err:
            print(err)
            await clear_server(user_id, tmp_directory_for_each_user, download_directory)
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
                    user_id, tmp_directory_for_each_user, download_directory
                )
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ **Error :** {e}",
                    message_id=ab.id,
                )
                return
        if file_size > TG_MAX_FILE_SIZE:
            await delete_msg(ab)
            return download_directory
        else:
            await delete_msg(ab)
            return download_directory

    else:
        await clear_server(user_id, tmp_directory_for_each_user, download_directory)
        await bot.edit_message_text(
            text="⚠️ **Error :** I can't open this url ",
            chat_id=update.message.chat.id,
            message_id=ab.id,
            disable_web_page_preview=True,
        )
        return None


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
                if round(diff % 10.00) == 0 or downloaded == total_length:
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
