import asyncio
import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    delete_msg,
    msg_edit,
    pl_server_clear,
)

db = Database()

logger = logging.getLogger(__name__)

from plugins.archive.files_list_maker import FILES_LIST
from plugins.others.playlist_uploader import playlist_uploader


def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


@Client.on_callback_query(filters.regex("^mkarchive"))
async def _make_archive(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    logger.info(
        f"☘️ Making Archive file. User {update.from_user.id} @{update.from_user.username}"
    )
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".video.mkv"
    )

    main_directory = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/"
    # ----------------- Archive Type --------------#
    ARCHIVE_TYPE = ReplyKeyboardMarkup(
        [["Zip File 🗃"], ["7z File 🗃", "Rar File 🗃"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    try:
        archive_type = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Select The Archive Type**",
                reply_markup=ARCHIVE_TYPE,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            1200,
        )
        #   await archive_type.delete()
        await archive_type.request.delete()
        archive_type = archive_type.text
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=ReplyKeyboardRemove())
            await ccc.delete()
        except:
            pass
        archive_type = "Zip File 🗃"

    if archive_type == "Zip File 🗃":
        archive_typed = "zipfile"
    elif archive_type == "7z File 🗃":
        archive_typed = "sevenzfile"
    elif archive_type == "Rar File 🗃":
        archive_typed = "rarfile"
    elif archive_type == "Cancel":
        archive_typed = "Cancel"
    else:
        archive_typed = "Cancel"

    if archive_typed == "Cancel":
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        await update.message.reply(
            "Process Cancelled  ✅",
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    # ------------- Ask For Password --------------#
    ASK_ENCRIPTION = ReplyKeyboardMarkup(
        [["Skip", "Password 🔓"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    try:
        encryption_ask = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Do you want to Set Password (Encryption) on Archive**",
                reply_markup=ASK_ENCRIPTION,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        #   await encryption_ask.delete()
        await encryption_ask.request.delete()
        encryption_ask = encryption_ask.text
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=ReplyKeyboardRemove())
            await ccc.delete()
        except:
            pass
        encryption_ask = "Cancel"

    if encryption_ask == "Skip":
        encryption_asked = "Skip"
    elif encryption_ask == "Password 🔓":
        encryption_asked = "password"
    elif encryption_ask == "Cancel":
        encryption_asked = "Cancel"
    else:
        encryption_asked = "Cancel"

    if encryption_asked == "Cancel":
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        await update.message.reply(
            "Process Cancelled  ✅",
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if encryption_asked == "password":
        PASSWORD_BUTTON = ReplyKeyboardMarkup(
            [["Skip"], ["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        try:
            password_ask = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"If you don't want Password in Archive, Then Skip\n\n**Now Send The Password To Encrypt**",
                    reply_markup=PASSWORD_BUTTON,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                1200,
            )
            #   await password_ask.delete()
            await password_ask.request.delete()
            password_ask = password_ask.text
        except asyncio.TimeoutError:
            try:
                ccc = await update.message.reply(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await ccc.delete()
            except:
                pass
            password_ask = "Cancel"

        if password_ask == "Skip":
            encryption_asked = "Skip"
        elif password_ask == "Cancel":
            password_asked = "Cancel"
        else:
            password_asked = f"{password_ask}"

        if Config.LOG_CHANNEL:
            try:
                await bot.send_message(
                    Config.LOG_CHANNEL,
                    f"Archive Password - `{password_asked}`\n\nFor @{update.from_user.username} `{str(update.from_user.id)}`",
                )
            except:
                pass
    # ---------------- Ask For Name --------------#
    new_file_name = f"{user_id}"
    if (await db.get_auto_rename(update.from_user.id)) is True:
        BUTTON_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            ask_ = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"**Send The Name of Output Archive File**",
                    reply_markup=BUTTON_CANCEL,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                1200,
            )
            #   await ask_.delete()
            await ask_.request.delete()
            cfile_name = ask_.text
        except asyncio.TimeoutError:
            try:
                ccc = await update.message.reply(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await ccc.delete()
            except:
                pass
            cfile_name = "Default_Name"

        if cfile_name == "Cancel":
            await clear_server(user_id, saved_file_path)
            FILES_LIST.update({update.from_user.id: []})
            await update.message.reply(
                "Process Cancelled  ✅",
                reply_to_message_id=reply_msg.id,
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
        cfile_name = cfile_name[
            :60
        ]  # truncated_text = new_name[0:60] # File name reduced

        IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
        if len(cfile_name) > 60:
            long_msg = await update.message.reply(
                IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name)),
                reply_to_message_id=reply_msg.id,
            )
            await clear_server(user_id, saved_file_path)
            FILES_LIST.update({update.from_user.id: []})
            return

        new_file_name = f"{cfile_name}"

    try:
        ab = await update.message.reply(
            f"**Processing....**", reply_to_message_id=reply_msg.id
        )
    except Exception as e:
        await pl_server_clear(user_id, output_folder)
        FILES_LIST.update({update.from_user.id: []})
        print(e)
        return

    list_message_ids = FILES_LIST.get(update.from_user.id, None)
    list_message_ids.sort()
    f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/input.txt"
    if list_message_ids is None:
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        await msg_edit(ab, "⚠️ File List is Empty")
        return

    if not os.path.exists(f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/"):
        os.makedirs(f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/")

    COUNT.append(user_id)

    for i in await bot.get_messages(
        chat_id=update.from_user.id, message_ids=list_message_ids
    ):
        media = i.video or i.document or i.audio or i.photo
        try:
            ab = await ab.edit(f"**Downloading :** `{media.file_name}` ...")
        except MessageNotModified:
            FILES_LIST.get(update.from_user.id).remove(i.id)
            await msg_edit(ab, "⚠️ File Skipped!")
            await asyncio.sleep(3)
            continue
        file_dl_path = None
        try:
            progress_bar = Progress(update.from_user.id, bot, ab)
            c_time = time.time()
            file_dl_path = await bot.download_media(
                message=i,
                file_name=f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/{i.id}/",
                # file_name=f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/{media.file_name}",
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("Downloading....", c_time),
            )
            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ab.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path)
                FILES_LIST.update({update.from_user.id: []})
                return
        except Exception as e:
            print(f"⚠️ Error: {e}")
            FILES_LIST.get(update.from_user.id).remove(i.id)
            await msg_edit(ab, "⚠️ File Skipped!!!")
            await asyncio.sleep(3)
            continue

    if archive_typed == "zipfile":
        archive_path = f"{Config.DOWNLOAD_LOCATION}/{new_file_name}.zip"
        if encryption_asked == "password":
            _, err = await pzip_maker(archive_path, main_directory, password_asked)
        else:
            _, err = await zip_maker(archive_path, main_directory)

    elif archive_typed == "rarfile":
        archive_path = f"{Config.DOWNLOAD_LOCATION}/{new_file_name}.rar"
        if encryption_asked == "password":
            _, err = await prar_maker(archive_path, main_directory, password_asked)
        else:
            _, err = await rar_maker(archive_path, main_directory)

    elif archive_typed == "sevenzfile":
        archive_path = f"{Config.DOWNLOAD_LOCATION}/{new_file_name}.7z"
        if encryption_asked == "password":
            _, err = await psevenz_maker(archive_path, main_directory, password_asked)
        else:
            _, err = await sevenz_maker(archive_path, main_directory)

    else:
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        await delete_msg(ab)
        logger.info(
            f"⚠️ else UnExpected Happened {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if err:
        if "Wrong password" in err:
            await clear_server(user_id, saved_file_path)
            FILES_LIST.update({update.from_user.id: []})
            await msg_edit(
                ab,
                f"⚠️ Your Archive is Password Protected\n\n👉 Try Again With Password",
            )
            logger.info(
                f"⚠️ Archive has Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        else:
            try:
                errs = f"{err}"
                list_err = errs.split("/")
                err_text, apps, downloado, userids, reasons = (
                    list_err[0],
                    list_err[1],
                    list_err[2],
                    list_err[3],
                    list_err[4],
                )
            except:
                reasons = err
            print(err)
            await clear_server(user_id, saved_file_path)
            FILES_LIST.update({update.from_user.id: []})
            await msg_edit(ab, f"⚠️ {reasons}")
            return

    try:
        ofiles = len(os.listdir(main_directory))
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        print(e)
        await msg_edit(ab, f"⚠️ **Failed** To Make Archive")
        return

    if ofiles < 1:
        await clear_server(user_id, saved_file_path)
        FILES_LIST.update({update.from_user.id: []})
        await msg_edit(ab, f"⚠️**Error :** Something went wrong")
        logger.info(
            f"⚠️ Failed to Make Archive For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    await delete_msg(ab)
    try:
        selected_format = f"Others"
        await playlist_uploader(bot, update, archive_path, selected_format)
    except Exception as e:
        print(e)
        try:
            await update.message.reply(
                f"⚠️ **Error :** {e}", reply_to_message_id=reply_msg.id
            )
        except:
            pass
    await clear_server(user_id, saved_file_path)
    FILES_LIST.update({update.from_user.id: []})


# ---------------- Zip Maker -----------------#
async def zip_maker(archive_path, main_directory):
    file_genertor_command = [
        "7z",
        "a",
        "-tzip",
        "-mx=0",
        f"{archive_path}",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


async def pzip_maker(archive_path, main_directory, password=None):
    file_genertor_command = [
        "7z",
        "a",
        "-tzip",
        "-mx=0",
        f"{archive_path}",
        f"-p{password}",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


# ---------------- Rar Maker -----------------#
async def rar_maker(archive_path, main_directory):
    file_genertor_command = [
        "rar",
        "a",
        "-r",
        f"{archive_path}",
        "-m0",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


async def prar_maker(archive_path, main_directory, password=None):
    file_genertor_command = [
        "rar",
        "a",
        "-r",
        f"{archive_path}",
        "-m0",
        f"-p{password}",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


# ----------------- 7z Maker -----------------#
async def sevenz_maker(archive_path, main_directory):
    file_genertor_command = [
        "7za",
        "a",
        "-r",
        "-mx=0",
        f"{archive_path}",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


async def psevenz_maker(archive_path, main_directory, password=None):
    file_genertor_command = [
        "7za",
        "a",
        "-r",
        "-mx=0",
        f"{archive_path}",
        f"-p{password}",
        f"{main_directory}",
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    outpt_files = stdout.decode().strip()
    output_error = stderr.decode().strip()
    return outpt_files, output_error


"""

    for i, id_msg in enumerate(await bot.get_messages(
        chat_id=update.from_user.id, message_ids=list_message_ids
    )):
        try:
            numbers = f"{i+1}"
            ab = await ab.edit(f"**Downloading :** `{numbers}` ...")
        except MessageNotModified:
            FILES_LIST.get(update.from_user.id).remove(id_msg.message_id)
            await msg_edit(ab , "⚠️ File Skipped!")
            await asyncio.sleep(3)
            continue
        file_dl_path = None
        try:
            progress_bar = Progress(update.from_user.id, bot, ab)
            c_time = time.time()
            file_dl_path = await bot.download_media(
                message=id_msg,
                file_name=f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/{id_msg.message_id}/",
                #file_name=f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/{media.file_name}",
                progress=progress_bar.progress_for_pyrogram,
                progress_args=(f"**Downloading** `{numbers}`....", c_time),
            )
            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ab.message_id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path)
                FILES_LIST.update({update.from_user.id: []})
                return
        except Exception as e:
            print(f"⚠️ Error: {e}")
            FILES_LIST.get(update.from_user.id).remove(id_msg.message_id)
            await msg_edit(ab, "⚠️ File Skipped!!!")
            await asyncio.sleep(3)
            continue


"""
