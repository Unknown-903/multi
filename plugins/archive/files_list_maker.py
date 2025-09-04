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
from plugins.audio import COUNT, clear_server, delete_msg

db = Database()

FILES_LIST = {}
MESSAGES_ID = {}

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(
    filters.regex("^archiverpro")
)  # & filters.user(Config.AUTH_USERS)
async def make_archive(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None

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

    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".video.mkv"
    )
    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    media = reply_msg.video or reply_msg.document or reply_msg.audio or reply_msg.photo
    try:
        media.file_name
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        await update.message.reply_text(
            f"⚠️ **Error :** {e}", reply_to_message_id=reply_msg.id
        )
        return
    if media.file_name is None:
        await clear_server(user_id, saved_file_path)
        await update.message.reply_text(
            "⚠️ File Name Not Found !!!", reply_to_message_id=reply_msg.id
        )
        return
    input_ = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/input.txt"
    if os.path.exists(input_):
        await clear_server(user_id, saved_file_path)
        await update.message.reply_text(
            "⚠️ Your Already One in Progress\nDon't Spam.",
            reply_to_message_id=reply_msg.id,
        )
        return
    if FILES_LIST.get(update.from_user.id, None) is None:
        FILES_LIST.update({update.from_user.id: []})
    if (len(FILES_LIST.get(update.from_user.id)) >= 0) and (
        len(FILES_LIST.get(update.from_user.id)) <= Config.MAX_VIDEOS
    ):
        FILES_LIST.get(update.from_user.id).append(reply_msg.id)

    CANCEL_BUTTONSP = ReplyKeyboardMarkup(
        [["Done ✅"], ["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    next_video = await bot.ask(
        update.from_user.id,
        "After sending all files, Click on **Done ✅**\n\nOr, Now Send Me The Next File",
        reply_markup=CANCEL_BUTTONSP,
        reply_to_message_id=reply_msg.id,
    )
    # -------------- First File Appended ----------#
    MAKEA_BUTTONS = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Make Archive", callback_data="mkarchive")],
            [InlineKeyboardButton("Cancel", callback_data="mkcancel")],
        ]
    )
    if next_video.text:
        if next_video.text == "Cancel":
            await clear_server(user_id, saved_file_path)
            FILES_LIST.update({update.from_user.id: []})
            await delete_msg(next_video, next_video.request)
            await update.message.reply_text(
                "Process Cancelled ✅",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
            return

        elif next_video.text == "Done ✅":
            await delete_msg(next_video, next_video.request)
            await update.message.reply_text(
                "If you want Custom file name in Output Archive File, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Click on **Make Archive** 👇",
                reply_markup=MAKEA_BUTTONS,
                reply_to_message_id=reply_msg.id,
            )
            return

        else:
            await delete_msg(next_video, next_video.request)
            next_video = await bot.ask(
                update.from_user.id,
                "⚠️ Don't send Test words\n\n👉 Now Send The Next File To Make Archive",
                reply_markup=CANCEL_BUTTONSP,
                reply_to_message_id=reply_msg.id,
            )
        # ---------------------------------------------#
    while True:
        MERGE_BUTTONO = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Make Archive", callback_data="mkarchive")],
                [InlineKeyboardButton("Cancel", callback_data="mkcancel")],
            ]
        )

        MERGER_BUTTONS = ReplyKeyboardMarkup(
            [["Done ✅"], ["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )

        if next_video.text:
            if next_video.text == "Cancel":
                await clear_server(user_id, saved_file_path)
                FILES_LIST.update({update.from_user.id: []})
                if MESSAGES_ID.get(update.from_user.id, None) is not None:
                    await bot.delete_messages(
                        chat_id=update.message.chat.id,
                        message_ids=MESSAGES_ID.get(update.from_user.id),
                    )
                try:
                    await editable.edit(
                        "Process Cancelled ✅", reply_markup=ReplyKeyboardRemove()
                    )
                except:
                    await update.message.reply_text(
                        "Process Cancelled ✅",
                        reply_markup=ReplyKeyboardRemove(),
                        reply_to_message_id=reply_msg.id,
                    )
                break
            elif next_video.text == "Done ✅":
                if MESSAGES_ID.get(update.from_user.id, None) is not None:
                    await bot.delete_messages(
                        chat_id=update.message.chat.id,
                        message_ids=MESSAGES_ID.get(update.from_user.id),
                    )
                try:
                    await editable.edit(
                        "If you want Custom file name in Output Archive File, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Click on **Make Archive** 👇",
                        reply_markup=MERGE_BUTTONO,
                    )
                except:
                    await update.message.reply_text(
                        "If you want Custom file name in Output Archive File, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Click on **Make Archive** 👇",
                        reply_markup=MERGE_BUTTONO,
                        reply_to_message_id=next_video.id,
                    )

                cancd = await update.message.reply_text(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await delete_msg(cancd)
                break

            else:
                next_video = await bot.ask(
                    update.from_user.id,
                    "⚠️ You are Doing Wrong.\n\n👉 Send me the next file to make Archive, Or\n\n👉 Click on the Below Button 👇",
                    reply_markup=MERGER_BUTTONS,
                    reply_to_message_id=next_video.id,
                )
                continue
        # ------------------ Apend Files --------------#
        if (
            next_video.video
            or next_video.document
            or next_video.audio
            or next_video.photo
        ):
            filetype = (
                next_video.document
                or next_video.video
                or next_video.audio
                or next_video.photo
            )
            try:
                file_name_recogniser = filetype.file_name
            except Exception as e:
                next_video = await bot.ask(
                    update.from_user.id,
                    f"⚠️ **Error** : {e}\n\n👉 Getting Error in this File. So, Send me Another File To Make Archive",
                    reply_to_message_id=next_video.id,
                )
                continue
            if file_name_recogniser is None:
                next_video = await bot.ask(
                    update.from_user.id,
                    "⚠️ File Name Not Found !!!\n\n👉 So, Send me Another File or Rename it",
                    reply_to_message_id=next_video.id,
                )
                continue

            input_ = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/input.txt"
            if os.path.exists(input_):
                FILES_LIST.update({update.from_user.id: []})
                await clear_server(user_id, saved_file_path)
                await update.message.reply_text(
                    "⚠️ Already One in Progress\n\n👉 Don't Spam."
                )
                break

            editable = await update.message.reply_text(
                "**Please wait....**", reply_to_message_id=next_video.id
            )
            if len(FILES_LIST.get(update.from_user.id)) > Config.MAX_VIDEOS:
                if MESSAGES_ID.get(update.from_user.id, None) is not None:
                    await bot.delete_messages(
                        chat_id=update.message.chat.id,
                        message_ids=MESSAGES_ID.get(update.from_user.id),
                    )
                await editable.edit(
                    text="⚠️ Reached Limit !!!\n👉 Max **{} Files** Allowed to Make Archive File".format(
                        len(FILES_LIST.get(update.from_user.id))
                    )
                )
                next_video = await bot.ask(
                    update.from_user.id,
                    "Now Press on Keyboard Button 👇",
                    reply_markup=MERGE_BUTTONO,
                    reply_to_message_id=next_video.id,
                )
                MESSAGES_ID.update({update.from_user.id: next_video.request.id})
            if FILES_LIST.get(update.from_user.id, None) is None:
                FILES_LIST.update({update.from_user.id: []})
            if (len(FILES_LIST.get(update.from_user.id)) >= 0) and (
                len(FILES_LIST.get(update.from_user.id)) <= Config.MAX_VIDEOS
            ):
                FILES_LIST.get(update.from_user.id).append(next_video.id)

                if MESSAGES_ID.get(update.from_user.id, None) is not None:
                    await bot.delete_messages(
                        chat_id=update.message.chat.id,
                        message_ids=MESSAGES_ID.get(update.from_user.id),
                    )
                await editable.edit(
                    text="Total Files : **{}**".format(
                        len(FILES_LIST.get(update.from_user.id))
                    )
                )
                next_video = await bot.ask(
                    update.from_user.id,
                    f"Now Send Me The Next File",
                    reply_markup=MERGER_BUTTONS,
                    reply_to_message_id=next_video.id,
                )
                MESSAGES_ID.update({update.from_user.id: next_video.request.id})

        else:
            next_video = await bot.ask(
                update.from_user.id,
                "⚠️ Send Me files Or Click on Below Keyboard",
                reply_markup=MERGER_BUTTONS,
                reply_to_message_id=next_video.id,
            )
            MESSAGES_ID.update({update.from_user.id: next_video.request.id})


@Client.on_callback_query(filters.regex("^mkcancel"))
async def mkcancel_(bot, update):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".video.mkv"
    )
    try:
        FILES_LIST.update({update.from_user.id: []})
    except:
        pass
    await clear_server(user_id, saved_file_path)
    await delete_msg(update.message)
    try:
        await update.message.reply(
            "Process Cancelled ✅", reply_to_message_id=reply_msg.id
        )
    except:
        pass
