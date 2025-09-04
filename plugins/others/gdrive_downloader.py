import logging
import os

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import CANCEL_PROCESS, COUNT, delete_msg, msg_edit, pl_server_clear

db = Database()
from plugins.others.playlist_uploader import cli_call, playlist_uploader

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


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("folderdldr"))
)
async def folderdldr_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    bc = None

    url = reply_msg.text

    if update.from_user.id not in Config.AUTH_USERS:
        if Config.GDRIVE_FOLDER_UPLOAD.upper() == "NO":
            if "drive/folders" in url:
                await update.message.reply(
                    "⚠️ Currently Disabled To upload Google Drive Folder in This Bot\n\n👉 For Help, Go to @Helps_Group",
                    reply_to_message_id=reply_msg.id,
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
    if "drive/folders" in url:
        final_cmd = f"gdown {url} --fuzzy -O {output_folder} --folder"
    else:
        final_cmd = f"gdown {url} --fuzzy -O {output_folder}"

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

    err_a = "Cannot retrieve the public link of the file. \n"
    err_b = "You may need to change the permission to "
    err_c = "**Anyone with the link** or have had many accesses."

    if ofiles < 1:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Failed** to download url\n\n{err_a}{err_b}{err_c}")
        logger.info(
            f"⚠️ Failed to download url {url} For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if getFolderSize(output_folder) < 25:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Failed** to Download URL\n\n{err_a}{err_b}{err_c}")
        logger.info(
            f"⚠️ Failed to Download URL {url} For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    try:
        files_folder = sorted(list_files(output_folder, []))
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
        cd = await bc.edit(f"**Files Are Uploading....**", reply_markup=cance_markup)
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                f"**Files Are Uploading....**", reply_to_message_id=reply_msg.id
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

    numbers = 0
    for i, single_file in enumerate(files_folder):
        if os.path.exists(single_file):
            try:
                numbers = f"{i+1}"
                selected_format = f"GoogleDrive/{numbers}"
                premium_upload = "Yes"
                captions = None
                await playlist_uploader(
                    bot, update, single_file, selected_format, captions, premium_upload
                )
            except Exception as e:
                try:
                    await update.message.reply(
                        f"⚠️ **Error :** {single_file}\n\nFor File : __{single_file}__",
                        reply_to_message_id=reply_msg.id,
                    )
                    print(e)
                except:
                    pass
                continue

    await delete_msg(cd)
    await pl_server_clear(user_id, output_folder)
    if int(numbers) != 0:
        if int(numbers) == 1:
            texts = f"1 File is Uploaded ✅"
        else:
            texts = f"All Files Are Uploaded ✅"  
        await bot.send_message(
            update.message.chat.id,
            f"{texts}",
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f"{texts}  By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    else:
        await bot.send_message(
            update.message.chat.id,
            "⚠️ Maybe, Today's Google Drive Download Limit Exceeded!\n\nOr, You are trying for more than 50 files\n\nDue to **Drive Download limit** (without Authorisation of Google Account) You can Download about 50 files in 1 Bot\n\nWe have more than 7 Bots, So you can download 7*50 = 350 files per day \n\nSo, Try our other bots 👉 https://t.me/TheNiceBots/202",
            disable_web_page_preview=True,
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f"⚠️ May be reached Gdrive limit For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
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


# ---------------- Progress ------------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("drivprogre"))
)
async def driveppr_(bot, update):

    try:
        output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
        dl_size = getFolderSize(output_folder)
        download_size = humanbytes(dl_size)
    except Exception as e:
        print(e)

    try:
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text=f"Total Downloaded: {download_size}",
            show_alert=True,
            cache_time=0,
        )
    except:
        pass
