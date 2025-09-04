import asyncio
import datetime
import json
import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import Config
from database.database import Database
from helpers.display_progress import Progress
from plugins.audio import CANCEL_PROCESS, COUNT, clear_server, delete_msg, msg_edit
from plugins.audio_helper import Ranjan
from plugins.others.playlist_uploader import playlist_uploader

db = Database()
UPLOADS = {}
STREAMS_INDEX = {}
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def execute_cmd(cmds):
    process = await asyncio.create_subprocess_exec(
        *cmds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


##########################################
# ---------------- UPLOADER ---------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("fstreamup"))
)
async def fstreamupload(bot, update):
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    await delete_msg(update.message)
    updated_data = update.data.split("/")
    mapping, chat_msg_id = (updated_data[1], updated_data[2])
    data = UPLOADS[chat_msg_id][int(mapping)]
    outputs = data["location"]

    try:
        os.path.getsize(outputs)
    except Exception as e:
        await clear_server(user_id, new_video_name)
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Error occured: {e}", reply_to_message_id=reply_msg.id
        )
        return

    new_names = "A_Default_Name"
    if (await db.get_auto_rename(update.from_user.id)) is True:
        NUMBER_BUTTONS = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            new_name = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"__**Now Send me The New File Name**__ 👇",
                    reply_markup=NUMBER_BUTTONS,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await new_name.delete()
                await new_name.request.delete()
            except:
                pass
            new_name = new_name.text
        except asyncio.TimeoutError:
            try:
                ccc = await update.message.reply(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await ccc.delete()
            except:
                pass
            new_name = "Time Out"

        new_name = os.path.splitext(new_name)[0]
        new_name = new_name[:60]  # truncated_text = new_name[0:60]

        IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File Name And Try again"""
        if len(new_name) > 60:
            long_msg = await update.message.reply(
                IF_LONG_FILE_NAME.format(alimit="60", num=len(checkerss)),
                reply_to_message_id=reply_msg.id,
            )
            await clear_server(user_id, outputs)
            return

        if new_name == "Cancel":
            new_names = "Cancel"
        elif new_name == "Time Out":
            new_names = "TimeUp"
        else:
            new_names = new_name

        if new_names == "Cancel":
            await clear_server(user_id, outputs)
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        if new_names == "TimeUp":
            new_names = "A_Default_Name"

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            f"{new_names}"
        except:
            pass

        main_directory = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
        new_video_name = f"{main_directory}/{new_names}.mkv"
        try:
            os.rename(outputs, new_video_name)
        except:
            new_video_name = outputs
    else:
        new_video_name = outputs

    try:
        os.path.getsize(new_video_name)
    except Exception as e:
        await clear_server(user_id, new_video_name)
        logger.info(
            f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Error occured: {e}", reply_to_message_id=reply_msg.id
        )
        return
    COUNT.append(user_id)
    selected_format = "Others"
    try:
        await playlist_uploader(bot, update, new_video_name, selected_format)
    except:
        pass
    await clear_server(user_id, new_video_name)
    logger.info(
        f"Stream Removed ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_callback_query(filters.regex("^remstream"))
async def remstreamsl(bot, update):
    ab = None
    bc = None

    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id

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
    #   if user_id in COUNT:
    #        ab = await bot.send_message(
    #           chat_id=update.message.chat.id,
    #          text="Already Your 1 Request Processing",
    #          reply_to_message_id=reply_msg.id
    #      )
    #      return

    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )

    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    BUTTON_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if reply_msg.media:
        logger.info(
            f"☘️ Sent file for Extracting audio or subtitles. User {update.from_user.id} @{update.from_user.username}"
        )
        try:
            ab = await update.message.reply(
                "**Downloading....**", reply_to_message_id=reply_msg.id
            )
        except:
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        COUNT.append(user_id)

        progress_bar = Progress(update.from_user.id, bot, ab)
        c_time = time.time()
        real_audio = await bot.download_media(
            message=reply_msg,
            file_name=saved_file_path,
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Downloading....**", c_time),
        )

        if (
            CANCEL_PROCESS[update.message.chat.id]
            and ab.id in CANCEL_PROCESS[update.message.chat.id]
        ):
            await clear_server(user_id, saved_file_path)
            return

        try:
            bc = await ab.edit(f"Media Downloaded Successfully ✅")
        except:
            await delete_msg(ab)
            try:
                bc = await update.message.reply(
                    "Video Downloaded Successfully ✅",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

    else:
        logger.info(
            f"☘️ Sent url for Extracting audio and subtitles. User {update.from_user.id} @{update.from_user.username}"
        )
        saved_file_path = reply_msg.text
        try:
            bc = await bot.send_message(
                chat_id=update.message.chat.id,
                text="🔗 URL Received",
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await clear_server(user_id, saved_file_path)
            print(e)
            return
        COUNT.append(user_id)

    try:
        trim_vid_dur = await Ranjan.get_duration(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : {e}")
        return

    try:
        time_format = datetime.timedelta(seconds=trim_vid_dur)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : Duration not found 0")
        return

    main_cmds = [
        "ffprobe",
        "-hide_banner",
        "-show_streams",
        "-print_format",
        "json",
        saved_file_path,
    ]
    output = await execute_cmd(main_cmds)
    if not output:
        await clear_server(user_id, saved_file_path)
        await msg_edit(bc, f"⚠️ **Error** : Data not found!!!")
        return

    details = json.loads(output[0])

    try:
        for stream in details["streams"]:
            stream["index"]
            stream["codec_name"]
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        logger.info(f"{e}")
        e = f"{e}"
        e = e[0:3000]
        await msg_edit(bc, f"⚠️ **Error 1:** Streams could not find\n{e}")
        return
    buttons = []

    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("audio", "subtitle", "video"):
            pass
        else:
            continue
        try:
            langs = stream["tags"]["language"]
        except:
            langs = mapping

        streams_cd = "delstream/{}/{}/{}/{}".format(
            stream_type, stream_name, langs, mapping
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{stream_type.capitalize()} - {str(langs).capitalize()} - {str(stream_name).capitalize()}",
                    callback_data=(streams_cd).encode("UTF-8"),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("❌ Cancel", callback_data="nytcancl"),
        ]
    )

    try:
        COUNT.remove(user_id)
    except:
        pass

    aaa = (
        "✶ You can Remove streams (audio, subtitles, video) by clicking below Buttons. "
    )
    bbb = "\n\n✶ Your video size will reduce, By removing unwanted streams. "
    ccc = "\n\n✶ Top first audio is **Default Audio**, Which will play in Telegram. "
    ddd = "\n\n**Select Your Required Option 👇**"

    try:
        cd = await bc.edit(
            f"{aaa}{bbb}{ccc}{ddd}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                f"{aaa}{bbb}{ccc}{ddd}",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return


########----------#--###########-#--#--#-#-#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("delstream"))
)
async def delstreamsi(bot, update):
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    await delete_msg(update.message)
    updated_data = update.data.split("/")
    codec_type, codec_name, language, mapping = (
        updated_data[1],
        updated_data[2],
        updated_data[3],
        updated_data[4],
    )
    if reply_msg.media:
        saved_file_path = (
            f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}.download.mkv"
        )
    else:
        saved_file_path = reply_msg.text

    try:
        cd = await update.message.reply(
            "**Removing....**", reply_to_message_id=reply_msg.id
        )
    except:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    COUNT.append(user_id)
    stickeraudio = None
    try:
        stickeraudio = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAESX81jQ4atc_bS1YcfJ3IfCuTfSfoKkwACegYAAgu2GVYTpn876J0baCoE",
        )
    except:
        pass

    logger.info(
        f"Codec Name: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )

    outputs = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}/Default_Name_1.mkv"
    out = "No Error"
    err = "No Error"
    rcode = "No Error"
    pid = "No Error"

    main_cmds = [
        "ffmpeg",
        "-i",
        f"{saved_file_path}",
        "-map",
        "0",
        "-map",
        f"-0:{mapping}",
        "-c",
        "copy",
        f"{outputs}",
        "-y",
    ]
    out, err, rcode, pid = await execute_cmd(main_cmds)
    if rcode != 0:
        await clear_server(user_id, saved_file_path, outputs)
        try:
            await delete_msg(stickeraudio)
            ef = await cd.edit(f"⚠️ **Error** : in extraction")
        except:
            await delete_msg(cd)
            try:
                ef = await update.message.reply(
                    "⚠️ **Error** : in extraction", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, saved_file_path, outputs)
                logger.info(
                    f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            print(err)
            return

    await delete_msg(stickeraudio)
    try:
        os.remove(saved_file_path)
    except:
        pass
    try:
        COUNT.remove(user_id)
    except:
        pass
    main_cmds = [
        "ffprobe",
        "-hide_banner",
        "-show_streams",
        "-print_format",
        "json",
        outputs,
    ]
    output = await execute_cmd(main_cmds)
    if not output:
        await clear_server(user_id, outputs)
        await msg_edit(cd, f"⚠️ **Error** : Data not found!!!")
        return

    details = json.loads(output[0])

    try:
        e = None
        for stream in details["streams"]:
            stream["index"]
            stream["codec_name"]
    except Exception as e:
        await clear_server(user_id, outputs)
        logger.info(f"{e}")
        e = f"{e}"
        e = e[0:3000]
        await msg_edit(cd, f"⚠️ **Error 2:** Streams could not find\n{e}")
        return
    buttons = []
    STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"] = {}
    UPLOADS[f"{update.message.chat.id}-{cd.id}"] = {}

    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("audio", "subtitle", "video"):
            pass
        else:
            continue
        try:
            langs = stream["tags"]["language"]
        except:
            langs = mapping

        chat_msg_id = f"{update.message.chat.id}-{cd.id}"
        streams_cd = "reprocess/{}/{}/{}/{}".format(
            stream_type, stream_name, mapping, chat_msg_id
        )
        upload_streams = "fstreamup/{}/{}".format(mapping, chat_msg_id)

        UPLOADS[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "location": outputs,
        }
        STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "map": mapping,
            "name": stream_name,
            "type": stream_type,
            "lang": langs,
            "location": outputs,
        }
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{stream_type.capitalize()} - {str(langs).capitalize()} - {str(stream_name).capitalize()}",
                    callback_data=(streams_cd).encode("UTF-8"),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("❌ Cancel", callback_data="nytcancl"),
            InlineKeyboardButton(
                "✅ Upload", callback_data=(upload_streams).encode("UTF-8")
            ),
        ]
    )
    aaa = "✶ Do you want to remove more streams? Then click below button."
    bbb = "\n\n**✅ Upload:** Now, If you want to upload video."
    ccc = "\n\n**❌ Cancel:** To cancel the whole process."
    ddd = "\n\n✶ If you want custom file name in output video, "
    eee = "Then Activate ✏️ **Rename File: Yes** in /settings"
    fff = "\n\n✶ Top first audio is **Default Audio**, Which will play in Telegram. "
    ggg = "\n\n**Select Your Required Option 👇**"

    try:
        ef = await cd.edit(
            f"{aaa}{bbb}{ccc}{ddd}{eee}{fff}{ggg}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                f"{aaa}{bbb}{ccc}{ddd}{eee}{fff}{ggg}",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=reply_msg.id,
            )
        except Exception:
            await clear_server(user_id, outputs)
            logger.info(
                f" ⚠️⚠️ can't send ef message {e} {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return


################ Reprocess 1 #############
########----------#--###########-#--#--#-#-#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("reprocess"))
)
async def reprocess_one(bot, update):
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    await delete_msg(update.message)
    updated_data = update.data.split("/")
    codec_type, codec_name, mapping, chat_msg_id = (
        updated_data[1],
        updated_data[2],
        updated_data[3],
        updated_data[4],
    )
    data = STREAMS_INDEX[chat_msg_id][int(mapping)]
    saved_file_path = data["location"]

    try:
        cd = await update.message.reply(
            "**Removing....**", reply_to_message_id=reply_msg.id
        )
    except:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    COUNT.append(user_id)
    stickeraudio = None
    try:
        stickeraudio = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAESX81jQ4atc_bS1YcfJ3IfCuTfSfoKkwACegYAAgu2GVYTpn876J0baCoE",
        )
    except:
        pass

    logger.info(
        f"Codec Name: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )

    outputs = (
        Config.DOWNLOAD_LOCATION
        + "/"
        + f"{update.from_user.id}_Default_Name_2"
        + f".mkv"
    )
    out = "No Error"
    err = "No Error"
    rcode = "No Error"
    pid = "No Error"

    main_cmds = [
        "ffmpeg",
        "-i",
        saved_file_path,
        "-map",
        "0",
        "-map",
        f"-0:{mapping}",
        "-c",
        "copy",
        outputs,
        "-y",
    ]
    out, err, rcode, pid = await execute_cmd(main_cmds)
    if rcode != 0:
        await clear_server(user_id, saved_file_path, outputs)
        try:
            await delete_msg(stickeraudio)
            ef = await cd.edit(f"⚠️ **Error** : in extraction")
        except:
            await delete_msg(cd)
            try:
                ef = await update.message.reply(
                    "⚠️ **Error** : in extraction", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, saved_file_path, outputs)
                logger.info(
                    f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            print(err)
            return

    await delete_msg(stickeraudio)
    try:
        os.remove(saved_file_path)
    except:
        pass
    try:
        COUNT.remove(user_id)
    except:
        pass

    main_cmds = [
        "ffprobe",
        "-hide_banner",
        "-show_streams",
        "-print_format",
        "json",
        outputs,
    ]
    output = await execute_cmd(main_cmds)
    if not output:
        await clear_server(user_id, outputs)
        await msg_edit(cd, f"⚠️ **Error** : Data not found!!!")
        return

    details = json.loads(output[0])

    try:
        for stream in details["streams"]:
            stream["index"]
            stream["codec_name"]
    except Exception as e:
        await clear_server(user_id, outputs)
        logger.info(f"{e}")
        e = f"{e}"
        e = e[0:3000]
        await msg_edit(cd, f"⚠️ **Error 3:** Streams could not find\n{e}")
        return
    buttons = []
    STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"] = {}
    UPLOADS[f"{update.message.chat.id}-{cd.id}"] = {}

    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("audio", "subtitle", "video"):
            pass
        else:
            continue
        try:
            langs = stream["tags"]["language"]
        except:
            langs = mapping

        chat_msg_id = f"{update.message.chat.id}-{cd.id}"
        streams_cd = "twreprocess/{}/{}/{}/{}".format(
            stream_type, stream_name, mapping, chat_msg_id
        )
        upload_streams = "fstreamup/{}/{}".format(mapping, chat_msg_id)

        UPLOADS[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "location": outputs,
        }
        STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "map": mapping,
            "name": stream_name,
            "type": stream_type,
            "lang": langs,
            "location": outputs,
        }
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{stream_type.capitalize()} - {str(langs).capitalize()} - {str(stream_name).capitalize()}",
                    callback_data=(streams_cd).encode("UTF-8"),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("❌ Cancel", callback_data="nytcancl"),
            InlineKeyboardButton(
                "✅ Upload", callback_data=(upload_streams).encode("UTF-8")
            ),
        ]
    )
    aaa = "✶ Do you want to remove more streams? Then click below button.\n\n**✅ Upload:** Now, If you want to upload video."
    bbb = "\n\n**❌ Cancel:** To cancel the whole process.\n\n✶ If you want custom file name in output video, "
    ccc = "Then Activate ✏️ **Rename File: Yes** in /settings\n\n✶ Top first audio is **Default Audio**, Which will play in Telegram. "
    ddd = "\n\n**Select Your Required Option 👇**"

    try:
        ef = await cd.edit(
            f"{aaa}{bbb}{ccc}{ddd}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                f"{aaa}{bbb}{ccc}{ddd}",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await clear_server(user_id, outputs)
            logger.info(
                f" ⚠️⚠️ can't send ef message {e} {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return


################ Reprocess 2 #############
########----------#--###########-#--#--#-#-#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("twreprocess"))
)
async def reprocess_two(bot, update):
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    await delete_msg(update.message)
    updated_data = update.data.split("/")
    codec_type, codec_name, mapping, chat_msg_id = (
        updated_data[1],
        updated_data[2],
        updated_data[3],
        updated_data[4],
    )
    data = STREAMS_INDEX[chat_msg_id][int(mapping)]
    saved_file_path = data["location"]

    try:
        cd = await update.message.reply(
            "**Removing....**", reply_to_message_id=reply_msg.id
        )
    except:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    COUNT.append(user_id)
    stickeraudio = None
    try:
        stickeraudio = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAESX81jQ4atc_bS1YcfJ3IfCuTfSfoKkwACegYAAgu2GVYTpn876J0baCoE",
        )
    except:
        pass

    logger.info(
        f"Codec Name: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )

    outputs = (
        Config.DOWNLOAD_LOCATION
        + "/"
        + f"{update.from_user.id}/Default_Name_3"
        + f".mkv"
    )
    out = "No Error"
    err = "No Error"
    rcode = "No Error"
    pid = "No Error"

    main_cmds = [
        "ffmpeg",
        "-i",
        saved_file_path,
        "-map",
        "0",
        "-map",
        f"-0:{mapping}",
        "-c",
        "copy",
        outputs,
        "-y",
    ]
    out, err, rcode, pid = await execute_cmd(main_cmds)
    if rcode != 0:
        await clear_server(user_id, saved_file_path, outputs)
        try:
            await delete_msg(stickeraudio)
            ef = await cd.edit(f"⚠️ **Error** : in extraction")
        except:
            await delete_msg(cd)
            try:
                ef = await update.message.reply(
                    "⚠️ **Error** : in extraction", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, saved_file_path, outputs)
                logger.info(
                    f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            print(err)
            return

    await delete_msg(stickeraudio)
    try:
        os.remove(saved_file_path)
    except:
        pass
    try:
        COUNT.remove(user_id)
    except:
        pass

    main_cmds = [
        "ffprobe",
        "-hide_banner",
        "-show_streams",
        "-print_format",
        "json",
        outputs,
    ]
    output = await execute_cmd(main_cmds)
    if not output:
        await clear_server(user_id, outputs)
        await msg_edit(cd, f"⚠️ **Error** : Data not found!!!")
        return

    details = json.loads(output[0])

    try:
        for stream in details["streams"]:
            stream["index"]
            stream["codec_name"]
    except Exception as e:
        await clear_server(user_id, outputs)
        logger.info(f"{e}")
        e = f"{e}"
        e = e[0:3000]
        await msg_edit(cd, f"⚠️ **Error 4:** Streams could not find\n{e}")
        return
    buttons = []
    STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"] = {}
    UPLOADS[f"{update.message.chat.id}-{cd.id}"] = {}

    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("audio", "subtitle", "video"):
            pass
        else:
            continue
        try:
            langs = stream["tags"]["language"]
        except:
            langs = mapping

        chat_msg_id = f"{update.message.chat.id}-{cd.id}"
        streams_cd = "reprocess/{}/{}/{}/{}".format(
            stream_type, stream_name, mapping, chat_msg_id
        )
        upload_streams = "fstreamup/{}/{}".format(mapping, chat_msg_id)

        UPLOADS[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "location": outputs,
        }
        STREAMS_INDEX[f"{update.message.chat.id}-{cd.id}"][int(mapping)] = {
            "map": mapping,
            "name": stream_name,
            "type": stream_type,
            "lang": langs,
            "location": outputs,
        }
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{stream_type.capitalize()} - {str(langs).capitalize()} - {str(stream_name).capitalize()}",
                    callback_data=(streams_cd).encode("UTF-8"),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("❌ Cancel", callback_data="nytcancl"),
            InlineKeyboardButton(
                "✅ Upload", callback_data=(upload_streams).encode("UTF-8")
            ),
        ]
    )
    aaa = "✶ Do you want to remove more streams? Then click below button.\n\n**✅ Upload:** Now, If you want to upload video."
    bbb = "\n\n**❌ Cancel:** To cancel the whole process.\n\n✶ If you want custom file name in output video, "
    ccc = "Then Activate ✏️ **Rename File: Yes** in /settings\n\n✶ Top first audio is **Default Audio**, Which will play in Telegram. "
    ddd = "\n\n**Select Your Required Option 👇**"

    try:
        ef = await cd.edit(
            f"{aaa}{bbb}{ccc}{ddd}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                f"{aaa}{bbb}{ccc}{ddd}",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=reply_msg.id,
            )
        except Exception as e:
            await clear_server(user_id, outputs)
            logger.info(
                f" ⚠️⚠️ can't send ef message {e} {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return
