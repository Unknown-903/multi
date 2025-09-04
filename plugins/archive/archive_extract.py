import asyncio
import logging
import os
import time

from pykeyboard import InlineKeyboard
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.archive.download_link import download_link
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    delete_msg,
    msg_edit,
    pl_server_clear,
)
from plugins.others.playlist_uploader import playlist_uploader
from plugins.archive.drive_dl import gdrive_dlr
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def remove_unwanted(string):
    return (
        string.replace('"', "-")
        .replace(":", "-")
        .replace(";", "-")
        .replace("?", "-")
        .replace("&", "-")
        .replace(",", "-")
        .replace("*", "-")
        .replace("_", "-")
    )


def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


async def asking_password(bot, update, texts_pass):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    output_folder = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/extracted"

    PASSWORD_ASKS = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_password = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=texts_pass,
                reply_markup=PASSWORD_ASKS,
                reply_to_message_id=reply_msg.id,
            ),
            1800,
        )
        await ask_password.request.delete()
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out\n\n👉 Resend your file And try Again",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await pl_server_clear(user_id, output_folder)
        ask_password = False

    if ask_password.text == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await pl_server_clear(user_id, output_folder)

    return ask_password


BOT_CMDS = [
    "/start",
    "/help",
    "/settings",
    "/usettings",
    "/del_thumb",
    "/show_thumb",
    "/admin",
    "/force_use",
    "/process",
    "/info",
    "/id",
]


@Client.on_callback_query(filters.regex("^aextract"))
async def extract_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    bco = None
    e = "e !!!!?"
    ask_choice = "NiceBots"
    asked_password = "TheNiceBots"
    type_choice = "NiceBots"
    typed_choice = "TheNiceBots"

    if reply_msg.media:
        if not reply_msg.document:
            await update.message.reply(
                "⚠️ Send only Archived file (ex. zip, rar etc)",
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
    # ----------------- Ask Type -----------------#
    TYPE_BUTTONS = ReplyKeyboardMarkup(
        [["Extractor 1", "Extractor 2"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        type_choice = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Extractor 1** : will Extract files from archive (without using directory names)\n\n**Extractor 2** : will Extract files with full paths\n\n**Note :** Both are different in Command Line. When your all files are not listing. Then try **Extractor 2** \n\n✶ If Your Archive is Simple, Then Ignore these Texts. Select any 👇",
                reply_markup=TYPE_BUTTONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        await type_choice.request.delete()
        type_choice = type_choice.text
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out, ReSend your file",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if type_choice == "Extractor 1":
        typed_choice = "one_extractor"
    elif type_choice == "Extractor 2":
        typed_choice = "extractor_two"
    elif type_choice == "Cancel":
        typed_choice = "Cancel"
    else:
        typed_choice = "Cancel"

    if typed_choice == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return
    # ---------------- Choice Button -------------#
    CHOICE_BUTTONS = ReplyKeyboardMarkup(
        [["Unzip 🗃", "Password 🔓"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_choice = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"🗃 = Normal files\n\n🔓 = Password protected files\n\nCancel = To cancel the process\n\n__**You Selected {type_choice}**__",
                reply_markup=CHOICE_BUTTONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        #  await ask_choice.delete()
        await ask_choice.request.delete()
        ask_choice = ask_choice.text
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out, ReSend your file",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if ask_choice == "Unzip 🗃":
        asked_choice = "unzips"
    elif ask_choice == "Password 🔓":
        asked_choice = "passwords"
    elif ask_choice == "Cancel":
        asked_choice = "Cancel"
    else:
        asked_choice = "Cancel"

    if asked_choice == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if asked_choice == "passwords":
        PASSWORD_BUTTON = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            ask_password = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"Now Send me the password of Archive",
                    reply_markup=PASSWORD_BUTTON,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                600,
            )
            #  await ask_password.delete()
            await ask_password.request.delete()
            ask_password = ask_password.text
        except asyncio.TimeoutError:
            try:
                await update.message.reply(
                    "⚠️ Process Time Out, ReSend your file",
                    reply_markup=ReplyKeyboardRemove(),
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass
            logger.info(
                f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return
        if ask_password == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        else:
            asked_password = f"{ask_password}"

            if Config.LOG_CHANNEL:
                try:
                    await bot.send_message(
                        Config.LOG_CHANNEL,
                        f"Archive Password - `{asked_password}`\n\nFor @{update.from_user.username} `{str(update.from_user.id)}`",
                    )
                except:
                    pass

    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    output_folder = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/extracted"
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"

    if reply_msg.media:
        logger.info(
            f"☘️ Sent file for Extracting Archive. User {update.from_user.id} @{update.from_user.username}"
        )
        try:
            received_file = reply_msg.document
            documents_name = received_file.file_name
            documents_name = remove_unwanted(documents_name)
        except:
            documents_name = "ArchiveFile"

        try:
            ab = await update.message.reply(
                "**Downloading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        COUNT.append(user_id)

        progress_bar = Progress(update.from_user.id, bot, ab)
        c_time = time.time()
        archive = await bot.download_media(
            message=reply_msg,
            file_name=f"{download_path}/{documents_name}",
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Downloading....**", c_time),
        )

        if (
            CANCEL_PROCESS[update.message.chat.id]
            and ab.id in CANCEL_PROCESS[update.message.chat.id]
        ):
            await pl_server_clear(user_id, output_folder)
            return

        try:
            bco = await ab.edit(f"File Downloaded Successfully ✅")
        except:
            await delete_msg(ab)
            try:
                bco = await update.message.reply(
                    "File Downloaded Successfully ✅",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await pl_server_clear(user_id, output_folder)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

    else:
        logger.info(
            f"☘️ Sent url for Extracting Archive. User {update.from_user.id} @{update.from_user.username}"
        )
        if "drive.google.com" in reply_msg.text:
            archive = await gdrive_dlr(bot, update)
            try:
                file_size = os.path.getsize(archive)
            except Exception as e:
                logger.info(f"Error D: {e}")
                await pl_server_clear(user_id, output_folder)
                await update.message.reply(
                    f"⚠️ Initial **Error:** {e}", reply_to_message_id=reply_msg.id
                )
                return 

        else:
            archive = await download_link(bot, update)

            try:
                getFolderSize(download_path) < 5
            except Exception as e:
                await pl_server_clear(user_id, output_folder)
                logger.info(
                    f" ⚠️ {e} {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

            if getFolderSize(download_path) < 10:
                await pl_server_clear(user_id, output_folder)
                logger.info(
                    f" ⚠️⚠️ Folder size is less than 10kb {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

        if archive is None:
            await pl_server_clear(user_id, output_folder)
            logger.info(
                f" ⚠️⚠️ Archive is None in url {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        bco = await bot.send_message(
            chat_id=update.message.chat.id,
            text="Processing....",
            reply_to_message_id=reply_msg.id,
        )

    try:
        bc = await bco.edit(f"**Extracting....**")
    except:
        await delete_msg(bco)
        try:
            bc = await update.message.reply(
                f"**Extracting....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    if typed_choice == "one_extractor":
        if asked_choice == "passwords":
            logger.info(
                f"👉 Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            if Config.LOG_CHANNEL:
                try:
                    await bot.send_message(
                        Config.LOG_CHANNEL,
                        f"e Archive Password : `{asked_password}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                    )
                except Exception as a:
                    logger.info(a)
            out, err = await archive_password(archive, output_folder, asked_password)

        else:
            logger.info(
                f"👉 7z Extractor using by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            out, err = await archive_extracter(archive, output_folder)

    else:
        if asked_choice == "passwords":
            logger.info(
                f"👉 x Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            if Config.LOG_CHANNEL:
                try:
                    await bot.send_message(
                        Config.LOG_CHANNEL,
                        f"x Archive Password : `{asked_password}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                    )
                except:
                    pass
            out, err = await x_extract_pass(archive, output_folder, asked_password)

        else:
            logger.info(
                f"👉 7z x Extractor using by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            out, err = await x_extractor(archive, output_folder)

    try:
        COUNT.remove(user_id)
    except:
        pass

    if err:
        if "Wrong password" in err:
            if asked_choice == "passwords":
                await msg_edit(bc, f"⚠️ Your Given Password is Wrong")
                logger.info(
                    f"⚠️ Given Password is Wrong {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

                texts_pass = f"Now Send me the Correct Password of Archive file"
                ask_password = await asking_password(bot, update, texts_pass)
                while True:
                    if ask_password.media:
                        texts_pass = f"⚠️ Currently, Don't send me files\n\n👉 Send me The Correct Password of Archive File"
                        ask_password = await asking_password(bot, update, texts_pass)

                    if ask_password.text:
                        if ask_password.text in BOT_CMDS:
                            texts_pass = f"⚠️ Currently, Don't use Commands\n\n👉 Send me The Correct Password of Archive File"
                            ask_password = await asking_password(
                                bot, update, texts_pass
                            )
                        if ask_password.text == "Cancel":
                            await delete_msg(bc)
                            break
                            return

                        extractor_msg = await update.message.reply(
                            "**Extracting....**", reply_to_message_id=reply_msg.id
                        )
                        if typed_choice == "one_extractor":
                            logger.info(
                                f"👉 Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                            )

                            if Config.LOG_CHANNEL:
                                try:
                                    await bot.send_message(
                                        Config.LOG_CHANNEL,
                                        f"e Archive Password : `{ask_password.text}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                                    )
                                except:
                                    pass
                            out, errs = await archive_password(
                                archive, output_folder, ask_password.text
                            )

                        else:
                            logger.info(
                                f"👉 x Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                            )
                            if Config.LOG_CHANNEL:
                                try:
                                    await bot.send_message(
                                        Config.LOG_CHANNEL,
                                        f"x Archive Password : `{ask_password.text}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                                    )
                                except:
                                    pass
                            out, errs = await x_extract_pass(
                                archive, output_folder, ask_password.text
                            )
                        await delete_msg(extractor_msg)
                        if errs:
                            if "Wrong password" in errs:
                                texts_pass = f"🙄 Again you entered wrong Password\n\n👉 Now Try to Send me the Correct Password of Archive file"
                                ask_password = await asking_password(
                                    bot, update, texts_pass
                                )
                            else:
                                try:
                                    errs = f"{errs}"
                                    list_err = errs.split("/")
                                    err_text, apps, downloado, userids, reasons = (
                                        list_err[0],
                                        list_err[1],
                                        list_err[2],
                                        list_err[3],
                                        list_err[4],
                                    )
                                except:
                                    reasons = errs
                                reasons = reasons[:4000]
                                await pl_server_clear(user_id, output_folder)
                                await update.message.reply(
                                    f"⚠️ {reasons}", reply_to_message_id=reply_msg.id
                                )
                                break

                        else:
                            break

                    else:
                        texts_pass = f"🤐 You are doing wrong !!!\n\n👉 Now Try to Send me the Correct Password of Archive file"
                        ask_password = await asking_password(bot, update, texts_pass)

            else:
                await msg_edit(bc, f"⚠️ Your Archive is Password Protected")
                logger.info(
                    f"⚠️ Archive has Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

                texts_pass = f"Now Send me the Correct Password of Archive file"
                ask_password = await asking_password(bot, update, texts_pass)
                while True:
                    if ask_password.media:
                        texts_pass = f"⚠️ Currently, Don't send me files\n\n👉 Send me The Correct Password of Archive File"
                        ask_password = await asking_password(bot, update, texts_pass)

                    if ask_password.text:
                        if ask_password.text in BOT_CMDS:
                            texts_pass = f"⚠️ Currently, Don't use Commands\n\n👉 Send me The Correct Password of This Archive File"
                            ask_password = await asking_password(
                                bot, update, texts_pass
                            )
                        if ask_password.text == "Cancel":
                            await delete_msg(bc)
                            break
                            return

                        extractor_msg = await update.message.reply(
                            "**Extracting....**", reply_to_message_id=reply_msg.id
                        )
                        if typed_choice == "one_extractor":
                            logger.info(
                                f"👉 Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                            )
                            if Config.LOG_CHANNEL:
                                try:
                                    await bot.send_message(
                                        Config.LOG_CHANNEL,
                                        f"e Archive Password : `{ask_password.text}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                                    )
                                except:
                                    pass

                            out, errs = await archive_password(
                                archive, output_folder, ask_password.text
                            )

                        else:
                            logger.info(
                                f"👉 x Extracting using Password {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                            )
                            if Config.LOG_CHANNEL:
                                try:
                                    await bot.send_message(
                                        Config.LOG_CHANNEL,
                                        f"x Archive Password : `{ask_password.text}`\n\n🌷 **User Id :** `{update.from_user.id}`\n🌷 **User Name :** `@{update.from_user.username}`",
                                    )
                                except:
                                    pass
                            out, errs = await x_extract_pass(
                                archive, output_folder, ask_password.text
                            )
                        await delete_msg(extractor_msg)
                        if errs:
                            if "Wrong password" in errs:
                                texts_pass = f"🙄 Again you entered wrong Password\n\n👉 Now Try to Send me the Correct Password of Archive file"
                                ask_password = await asking_password(
                                    bot, update, texts_pass
                                )
                            else:
                                try:
                                    errs = f"{errs}"
                                    list_err = errs.split("/")
                                    err_text, apps, downloado, userids, reasons = (
                                        list_err[0],
                                        list_err[1],
                                        list_err[2],
                                        list_err[3],
                                        list_err[4],
                                    )
                                except:
                                    reasons = errs
                                reasons = reasons[:4000]
                                await pl_server_clear(user_id, output_folder)
                                await update.message.reply(
                                    f"⚠️ {reasons}", reply_to_message_id=reply_msg.id
                                )
                                break

                        else:
                            break

                    else:
                        texts_pass = f"🤐 You are doing wrong !!!\n\n👉 Now Try to Send me the Correct Password of Archive file"
                        ask_password = await asking_password(bot, update, texts_pass)
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
            reasons = reasons[:4000]
            await pl_server_clear(user_id, output_folder)
            await msg_edit(bc, f"⚠️ {reasons}")
            return

    try:
        ofiles = len(os.listdir(output_folder))
    except Exception as e:
        await pl_server_clear(user_id, output_folder)
        print(e)
        await msg_edit(bc, f"⚠️ **Error :** Something went wrong")
        return

    if ofiles < 1:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(bc, f"⚠️ **Failed** To Extract Archive")
        logger.info(
            f"⚠️ Failed to Extract Archive For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    paths = get_files(path=output_folder)
    SELECT_BUTTONS = await make_keyboard(
        paths=paths, user_id=user_id, chat_id=update.message.chat.id
    )

    await delete_msg(bc)
    try:
        await update.message.reply(
            "**Choose the required option....**",
            reply_markup=SELECT_BUTTONS,
            reply_to_message_id=reply_msg.id,
        )
    except Exception:
        logger.info(
            f"⚠️ Error {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        try:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ Error : {e}\n\n👉 So, Your files of Archive are not listed. Now, Click on **Upload All Files** Button 👇",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            logger.info(
                f"⚠️ Error {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        ER_SELECT_BUTTONS = await er_make_keyboard(
            paths=paths, user_id=user_id, chat_id=update.message.chat.id
        )
        try:
            await update.message.reply(
                "**Choose the required option....**",
                reply_markup=ER_SELECT_BUTTONS,
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            logger.info(
                f"⚠️ Error {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            try:
                await bot.send_message(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ Error : {e}",
                    reply_to_message_id=reply_msg.id,
                )
            except Exception as e:
                logger.info(
                    f"⚠️ Error {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            await pl_server_clear(user_id, output_folder)


# -------------- Upload All Files -------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("all_files"))
)
async def upload_all(bot, update):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    tgbc = None
    COUNT.append(user_id)
    output_folder = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/extracted"

    spl_data = update.data.split("|")
    file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
    tgbc = None
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
        tgbc = await update.message.edit(
            "**Files Are Uploading....**", reply_markup=cance_markup
        )
    except:
        await delete_msg(tgbc)
        try:
            tgbc = await update.message.reply(
                f"**Files Are Uploading....**",
                reply_markup=cance_markup,
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        await msg_edit(tgbc, f"Process Cancelled ✅")
        print("Process Cancelled ✅")
        await pl_server_clear(user_id, output_folder)
        return

    paths = get_files(path=file_path)
    if not paths:
        await pl_server_clear(user_id, output_folder)
        try:
            tgbc = await tgbc.edit("🧐 Files not found to Upload")
        except:
            await delete_msg(tgbc)
            try:
                tgbc = await update.message.reply(
                    f"🧐 Files not found to Upload",
                    reply_to_message_id=reply_msg.id,
                )
            except Exception as e:
                print(e)
                return
    for single_file in paths:
        try:
            selected_format = f"Others"
            await playlist_uploader(bot, update, single_file, selected_format)
        except FloodWait:
            asyncio.sleep(4)
        except Exception as e:
            print(e)
            continue
    await delete_msg(tgbc)

    logger.info(
        f"All Files Are Uploaded ✅  By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    await pl_server_clear(user_id, output_folder)
    await bot.send_message(
        update.message.chat.id,
        "All Files Are Uploaded ✅",
        reply_to_message_id=reply_msg.id,
    )


# ------------ Upload Single Files ------------#


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("one_file"))
)
async def onebyone(bot, update):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    tgbc = None
    tbc = None
    spl_data = update.data.split("|")
    output_folder = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/extracted"
    file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
    tgbc = None
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
        tgbc = await update.message.edit(
            "**Files Are Uploading....**", reply_markup=cance_markup
        )
    except:
        await delete_msg(tgbc)
        try:
            tgbc = await update.message.reply(
                f"**Files Are Uploading....**",
                reply_markup=cance_markup,
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        await msg_edit(tgbc, f"Process Cancelled ✅")
        print("Process Cancelled ✅")
        await pl_server_clear(user_id, output_folder)
        return

    paths = get_files(path=file_path)
    if not paths:
        single_file = paths[int(spl_data[3])]
        await clear_server_two(single_file)
        try:
            tgbc = await tgbc.edit("🧐 Files not found to Upload")
        except:
            await delete_msg(tgbc)
            try:
                tgbc = await update.message.reply(
                    f"🧐 Files not found to Upload",
                    reply_to_message_id=reply_msg.id,
                )
            except Exception as e:
                print(e)
                return

    try:
        selected_format = f"Others"
        single_file = paths[int(spl_data[3])]
        await playlist_uploader(bot, update, single_file, selected_format)
    except Exception as e:
        print(e)

    try:
        tbc = await tgbc.edit("**Refreshing....**")
    except:
        await delete_msg(tgbc)
        try:
            tbc = await update.message.reply(
                f"**Refreshing....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    await asyncio.sleep(1)
    rpaths = get_files(path=file_path)
    if not rpaths:
        await pl_server_clear(user_id, output_folder)
        try:
            tgbc = await tbc.edit("All Files Uploaded ✅ ")
        except:
            await delete_msg(tbc)
            try:
                tgbc = await update.message.reply(
                    f"All Files Uploaded ✅", reply_to_message_id=reply_msg.id
                )
            except Exception as e:
                print(e)
                return
    SELECT_BUTTONS = await make_keyboard(
        paths=rpaths, user_id=update.from_user.id, chat_id=update.message.chat.id
    )

    try:
        upmsg = await tbc.edit(
            "**Choose the required option....**", reply_markup=SELECT_BUTTONS
        )
    except:
        await delete_msg(tbc)
        try:
            await update.message.reply(
                f"**Choose the required option....**",
                reply_to_message_id=reply_msg.id,
                reply_markup=SELECT_BUTTONS,
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return


# --------------- e Extractor -----------------#
async def archive_extracter(archive_file, output_directory):
    file_genertor_command = [
        "7z",
        "e",
        "-y",
        archive_file,
        f"-o{output_directory}",
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


async def archive_password(archive_file, output_directory, password):
    file_genertor_command = [
        "7z",
        "e",
        "-y",
        archive_file,
        f"-o{output_directory}",
        f"-p{password}",
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


# --------------- x Extractor -----------------#
async def x_extractor(archive_file, output_directory):
    file_genertor_command = [
        "7z",
        "x",
        "-y",
        archive_file,
        f"-o{output_directory}",
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


async def x_extract_pass(archive_file, output_directory, password):
    file_genertor_command = [
        "7z",
        "x",
        "-y",
        archive_file,
        f"-o{output_directory}",
        f"-p{password}",
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


# -------------- List Of Files ----------------#
def list_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return list_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst


# -------------------- Tools -----------------#

"""
def get_files(path):
    path_list = []
    for r, d, f in os.walk(path):
        for file in f:
            path_list.append(os.path.join(r, file))
    path_list.sort()
    return path_list
"""


def get_files(path):
    path_list = [
        val
        for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(path)]
        for val in sublist
    ]
    return sorted(path_list)


async def make_keyboard(paths, user_id, chat_id):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for file in paths:
        data.append(
            InlineKeyboardButton(
                f"{num} - {os.path.basename(file)}",
                f"one_file|{user_id}|{chat_id}|{num}",
            )
        )
        num += 1
        if num > (97):
            data.append(
                InlineKeyboardButton(
                    f"Upload All Files ", f"all_files|{user_id}|{chat_id}"
                )
            )
            data.append(InlineKeyboardButton("Cancel  ❌", "nytcancl"))
    data.append(
        InlineKeyboardButton(f"Upload All Files", f"all_files|{user_id}|{chat_id}")
    )
    data.append(InlineKeyboardButton("Cancel  ❌", "nytcancl"))
    i_kbd.add(*data)
    return i_kbd


async def er_make_keyboard(paths, user_id, chat_id):
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    data.append(
        InlineKeyboardButton(f"Upload All Files", f"all_files|{user_id}|{chat_id}")
    )
    data.append(InlineKeyboardButton("Cancel  ❌", "nytcancl"))
    i_kbd.add(*data)
    return i_kbd


"""
            files_ext = None
            try:
                files_ext = os.path.splitext(archive)[1]
            except:
                pass
            if files_ext == ".zst":
                logger.info(f"👉 zst x Extractor using by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
                out, err = await zstd_extracter(archive, output_folder)

            elif str(archive).endswith(("tar", "tar.gz", "tar.bz2")):
                logger.info(f"👉 tar x Extractor using by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
                out, err = await tar_extracter(archive, output_folder)

            else:
                logger.info(f"👉 7z x Extractor using by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
                out, err = await x_extractor(archive, output_folder)

"""

# ---------------- Extractors -----------------#
async def zstd_extracter(archive_file, output_directory):
    file_genertor_command = [
        "zstd",
        "-f",
        "--output-dir-flat",
        output_directory,
        "-d",
        archive_file,
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


async def tar_extracter(archive_file, output_directory):
    file_genertor_command = [
        "tar",
        "-xvf",
        archive_file,
        "-C",
        output_directory,
        "--warning=none",
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
