import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from database.database import Database
from helpers.display_progress import Progress, humanbytes
from plugins.audio import CANCEL_PROCESS, delete_msg

# from plugins.others.yt_audio_only import ytaudio_only
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import requests
import yt_dlp
from pyrogram import enums
from youtube_search import YoutubeSearch


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


class Chitranjans(object):
    S_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍 Search YouTube Song", callback_data="songsx"),
            ],
            [
                InlineKeyboardButton("Close", callback_data="close"),
            ],
        ]
    )


@Client.on_message(filters.private & filters.command("search"))
async def hbbon_(bot, update):
    b = await bot.send_message(
        chat_id=update.chat.id,
        text="For Searching songs Click below Button 👇",
        reply_markup=Chitranjans.S_BUTTONS,
        reply_to_message_id=update.id,
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("^songsx"))
async def songsv(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    BUTTON_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    CHOOSE = ReplyKeyboardMarkup(
        [["Skip", "Format Selection"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    song = await bot.ask(
        chat_id=update.message.chat.id,
        text=f"**✶ Please Enter The Name of Song**",
        reply_markup=BUTTON_CANCEL,
        filters=filters.text,
        reply_to_message_id=reply_msg.id,
    )
    # await song.delete()
    await song.request.delete()
    if song.text == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    queries = song.text
    if not "song" in queries:
        query = f"{queries} song"
    else:
        query = queries

    ab = await update.message.reply(
        "🔎 **Searching....**", reply_to_message_id=reply_msg.id
    )

    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count > 0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            results[0]["views"]

            if time_to_seconds(duration) >= 900:  # duration limit
                await delete_msg(ab)
                ab = await update.message.reply(
                    "⚠️ Song not found!!!\n\n👉 Define the name of the song a bit And Add in last (**Hindi Song** or __English Song__)",
                    reply_to_message_id=reply_msg.id,
                )
                return
            # performer = f"[Thenicebots]"
            thumb_name = f"thumb{user_id}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)

        except Exception as e:
            print(e)
            await delete_msg(ab)
            ab = await update.message.reply(
                "⚠️ Song Not Found!!!! Please check spellings",
                reply_to_message_id=reply_msg.id,
            )
            return
    except Exception as e:
        await delete_msg(ab)
        ab = await update.message.reply(
            "⚠️ Please enter correct song name ",
            reply_to_message_id=reply_msg.id,
        )
        print(str(e))
        return
    """
    await delete_msg(ab)
    selection = await bot.ask(
        chat_id=update.message.chat.id,
        text=f"**✶ Choose 👇**",
        reply_markup=CHOOSE,
        filters=filters.text,
        reply_to_message_id=reply_msg.id,
    )
    await selection.request.delete()
    if selection.text == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )            
        logger.info(f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
        return

    elif selection.text == "Format Selection":
        await ytaudio_only(bot, update, link)
        return

    elif selection.text == "Skip":
        pass

    else:
        await delete_msg(ab)
        ab = await update.message.reply(
            "⚠️ You didn't use keyboard !!!", reply_to_message_id=reply_msg.id
        )
        return
    """
    await delete_msg(ab)
    ab = await update.message.reply(
        "**Downloading.....**", reply_to_message_id=reply_msg.id
    )
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        file_size_output = ""
        output_size = ""
        try:
            file_size_output = os.path.getsize(audio_file)  # Working
            output_size = humanbytes(file_size_output)
        except:
            pass
        rep = f'<a href="{link}">{title}</a>\n\n<b>File Size:</b> {output_size}'
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60

        await delete_msg(ab)
        ab = await update.message.reply(
            "**Uploading.....**", reply_to_message_id=reply_msg.id
        )
        try:
            progress_bar = Progress(update.from_user.id, bot, ab)
            c_time = time.time()
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
            except:
                pass
            diksha = await bot.send_audio(
                chat_id=update.message.chat.id,
                audio=audio_file,
                # file_name=new_file_name,
                # performer=performer,
                title=title,
                caption=rep,
                duration=dur,
                thumb=thumb_name,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ab.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                try:
                    os.remove(audio_file)
                    os.remove(thumb_name)
                except Exception as e:
                    print(e)
                return

            # await delete_msg(ab)
            # if Config.LOG_CHANNEL:
            #    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
            #    await cmf2v.reply_text(
            #        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed song searcher"
            #    )
            logger.info(
                f" song searcher ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await delete_msg(ab)
            ab = await update.message.reply(
                f"⚠️ Error: {e}", reply_to_message_id=reply_msg.id
            )
    except Exception as e:
        print(e)
        await delete_msg(ab)
        ab = await update.message.reply(
            f"⚠️ Error: {e}", reply_to_message_id=reply_msg.id
        )
    await delete_msg(ab)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
