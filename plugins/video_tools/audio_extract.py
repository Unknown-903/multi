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
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    delete_msg,
    msg_edit,
    remove_unwanted,
)
from plugins.audio_helper import Ranjan
from plugins.others.playlist_uploader import playlist_uploader

db = Database()

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


@Client.on_callback_query(filters.regex("^strextract"))
async def strextracto(bot, update):
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
        await msg_edit(bc, f"⚠️ **Error** : Duration not found")
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
        print(e)
        await msg_edit(bc, f"⚠️ **Error :** Duration could not find")
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

        streams_cd = "exstream/{}/{}/{}/{}".format(
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
            InlineKeyboardButton("Cancel", callback_data="nytcancl"),
        ]
    )

    try:
        COUNT.remove(user_id)
    except:
        pass
    try:
        cd = await bc.edit(
            "**Select Your Required Option 👇**",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "☘️ **Select Your Required Option 👇**",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, saved_file_path)
            logger.info(
                f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("exstream"))
)
async def exstream_extract(bot, update):
    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    await delete_msg(update.message)
    updated_data = update.data.split("/")
    codec_name = None
    language = None
    codec_type = None
    mapping = None
    codec_type, codec_name, language, mapping = (
        updated_data[1],
        updated_data[2],
        updated_data[3],
        updated_data[4],
    )
    if reply_msg.media:
        saved_file_path = (
            Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
        )
    else:
        saved_file_path = reply_msg.text
    logger.info(
        f"☘️ Map {mapping}. For User {update.from_user.id} @{update.from_user.username}"
    )
    if codec_type is None:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f"❌ Codec Type: {codec_type}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Codec Type not found in List",
            reply_to_message_id=reply_msg.id,
        )
        return

    if mapping is None:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f"❌ Mapping: {mapping}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Mapping not found in List",
            reply_to_message_id=reply_msg.id,
        )
        return

    if language is None:
        await clear_server(user_id, saved_file_path)
        logger.info(
            f"❌ Language: {language}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Audio Language not found in List",
            reply_to_message_id=reply_msg.id,
        )
        return

    description_ = "Default_Name"
    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.document or file_video.audio
            description_ = media.file_name
            description_ = os.path.splitext(description_)[0]
            description_ = description_[:60]  # truncated_text  # +'.mp4'
        except:
            description_ = "Default_Name"

    else:
        try:
            file_name = os.path.basename(saved_file_path)
            description_ = os.path.splitext(file_name)[0]
            description_ = description_[:60]  # truncated_text
        except:
            description_ = "Default_Name"

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
            await clear_server(user_id, saved_file_path)
            return

        if new_name == "Cancel":
            new_names = "Cancel"
        elif new_name == "Time Out":
            new_names = "TimeUp"
        else:
            new_names = new_name

        if new_names == "Cancel":
            await clear_server(user_id, saved_file_path)
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        if new_names == "TimeUp":
            await clear_server(user_id, saved_file_path)
            await update.message.reply(
                "⚠️ Process Time Out, Resend Again",
                reply_to_message_id=reply_msg.id,
            )
            return

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            file_names = f"{new_names}"
        except:
            file_names = "Default_Name"

    else:
        file_names = description_

    try:
        good_file_name = remove_unwanted(file_names)
    except:
        good_file_name = "G_Default_Name"

    try:
        cd = await update.message.reply(
            "**Extracting....**", reply_to_message_id=reply_msg.id
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

    # Audio Codec
    if "audio" in codec_type:
        if codec_name.lower() == "aac":
            extention = "m4a"  # aac codec was giving duration err
        elif codec_name.lower() == "m4a":
            extention = "m4a"
        elif codec_name.lower() == "mp4a.40.2":
            extention = "m4a"
        elif codec_name.lower() == "mp3":
            extention = "mp3"
        elif codec_name.lower() == "mp2":
            extention = "mp2"
        elif codec_name.lower() == "flac":
            extention = "flac"
        elif codec_name.lower() == "wav":
            extention = "wav"
        elif codec_name.lower() == "opus":
            extention = "opus"
        else:
            extention = "mp3"
            logger.info(
                f"❌❌❌ Codec Name not in list!!!!: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )

    # subtitles
    elif "subtitle" in codec_type:
        if codec_name.lower() == "subrip":
            extention = "srt"
        elif codec_name.lower() == "ass":
            extention = "ass"
        else:
            extention = "srt"
            logger.info(
                f"❌❌❌ New Codec Name found!!!!: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
    # video
    elif "video" in codec_type:
        if codec_name.lower() == "mp4":
            extention = "mp4"
        elif codec_name.lower() == "mkv":
            extention = "mkv"
        else:
            extention = "mkv"
            logger.info(
                f"❌❌❌ New Codec Name found!!!!: {codec_name}. Stream Extractor User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )

    else:
        await clear_server(user_id, saved_file_path)
        await delete_msg(stickeraudio, cd)
        logger.info(
            f"❌❌❌ Codec Name: {codec_name} Not found in List. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Codec Name not found in List\n\n👉 Report this issue in @Helps_Group",
            reply_to_message_id=reply_msg.id,
        )
        return

    if codec_name is None:
        await clear_server(user_id, saved_file_path)
        await delete_msg(stickeraudio, cd)
        logger.info(
            f"Codec Name: {codec_name}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await update.message.reply(
            "⚠️ Codec Name not found in List",
            reply_to_message_id=reply_msg.id,
        )
        return

    outputs = Config.DOWNLOAD_LOCATION + "/" + f"{good_file_name}" + f".{extention}"
    out = "No Error"
    err = "No Error"
    rcode = "No Error"
    pid = "No Error"
    if "audio" in codec_type:
        if codec_name == "mp3":
            main_cmds = [
                "ffmpeg",
                "-i",
                saved_file_path,
                "-map",
                f"0:{mapping}",
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
                    ef = await cd.edit(
                        f"⚠️ **Error Occured** : in extraction, I can't extract audio from this file"
                    )
                except:
                    await delete_msg(cd)
                    try:
                        ef = await update.message.reply(
                            "⚠️ **Error Occured** : in extraction, I can't extract audio from this file",
                            reply_to_message_id=reply_msg.id,
                        )
                    except:
                        await clear_server(user_id, saved_file_path, outputs)
                        logger.info(
                            f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                print(err)
                return

        else:
            main_cmds = [
                "ffmpeg",
                "-i",
                saved_file_path,
                "-map",
                f"0:{mapping}",
                "-async",
                "1",
                "-strict",
                "-2",
                "-c",
                "copy",
                outputs,
                "-y",
            ]
            out, err, rcode, pid = await execute_cmd(main_cmds)
            if rcode != 0:
                await clear_server(user_id, saved_file_path, outputs)
                try:
                    logger.info(
                        f"Out 👉 {out} \n Error 👉 {err} \n👉 {rcode} \nPid 👉 {pid} ❌❌ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                except:
                    pass
                try:
                    await delete_msg(stickeraudio)
                    ef = await cd.edit(
                        f"⚠️ **Error Occured** : in extraction, I can't extract audio from this file"
                    )
                except:
                    await delete_msg(cd)
                    try:
                        ef = await update.message.reply(
                            "⚠️ **Error Occured** : in extraction, I can't extract audio from this file",
                            reply_to_message_id=reply_msg.id,
                        )
                    except:
                        await clear_server(user_id, saved_file_path, outputs)
                        logger.info(
                            f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                return

        await delete_msg(stickeraudio, cd)
        selected_format = f"NameAndSize"
        captions = f"**Language:** {language.upper()}"
        await playlist_uploader(bot, update, outputs, selected_format, captions)
        await clear_server(user_id, saved_file_path, outputs)
        logger.info(
            f"Audio Extracted ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )

    elif "subtitle" in codec_type:
        main_cmds = [
            "ffmpeg",
            "-i",
            saved_file_path,
            "-map",
            f"0:{mapping}",
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
                ef = await cd.edit(f"⚠️ **Error Occured** : in extraction")
            except:
                await delete_msg(cd)
                try:
                    ef = await update.message.reply(
                        "⚠️ **Error Occured** : in extraction",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(user_id, saved_file_path, outputs)
                    logger.info(
                        f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )

            try:
                logger.info(
                    f"Out 👉 {out} \n Error 👉 {err} \n👉 {rcode} \nPid 👉 {pid} ❌❌ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            except:
                pass
            return

        await delete_msg(stickeraudio, cd)
        selected_format = f"NameAndSize"
        captions = f"**Language:** {language.upper()}"
        await playlist_uploader(bot, update, outputs, selected_format, captions)
        await clear_server(user_id, saved_file_path, outputs)
        logger.info(
            f"Subtitles Extracted ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )

    elif "video" in codec_type:
        if "video" in codec_type:
            outputs = (
                Config.DOWNLOAD_LOCATION + "/" + f"{good_file_name}" + f".{extention}"
            )
            main_cmds = [
                "ffmpeg",
                "-i",
                saved_file_path,
                "-map",
                f"0:{mapping}",
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
                            "⚠️ **Error** : in extraction",
                            reply_to_message_id=reply_msg.id,
                        )
                    except:
                        await clear_server(user_id, saved_file_path, outputs)
                        logger.info(
                            f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                print(err)
                return

        await delete_msg(stickeraudio, cd)
        selected_format = f"NameAndSize"
        captions = f"**Only Video Stream**"
        await playlist_uploader(bot, update, outputs, selected_format, captions)
        await clear_server(user_id, saved_file_path, outputs)
        logger.info(
            f"Video Extracted ✅. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )


"""      
ffmpeg -i input.mkv \
-map 0:0 -c copy video_h264.mkv \
-map 0:1 -c copy audio0_vorbis.oga \
-map 0:2 -c copy audio1_aac.m4a \
-map 0:3 -c copy audio2.flac \
-map 0:4 -c copy subtitles.ass

        elif extention == "ac3":
            main_cmds = [
                "ffmpeg",
                "-i",
                saved_file_path,
                "-map",
                f"0:{mapping}",
                "-acodec",
                "ac3",
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
                            "⚠️ **Error** : in extraction",
                            reply_to_message_id=reply_msg.id,
                        )
                    except:
                        await clear_server(user_id, saved_file_path, outputs)
                        logger.info(
                            f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                        )
                print(err)
                return
# Audio
        elif codec_name.lower() == "ac3":
            extention = "ac3"
        elif codec_name.lower() == "eac3":
            extention = "ac3"
        elif codec_name.lower() == "acp": # aacPlus Audio File
            extention = "acp"
        elif codec_name.lower() == "3ga": # 3GPP Audio File
            extention = "3ga"
        elif codec_name.lower() == "wma":
            extention = "wma"
        elif codec_name.lower() == "ogg":
            extention = "ogg"
        elif codec_name.lower() == "vorbis": # right in net
            extention = "ogg" # oga
#Subtitles
        elif codec_name.lower() == "aqtitle":
            extention = "aqt"
        elif codec_name.lower() == "dks":
            extention = "dks"
        elif codec_name.lower() == "microdvd":
            extention = "sub"
        elif codec_name.lower() == "mpsub":
            extention = "sub"
        elif codec_name.lower() == "mpl2":
            extention = "mpl"
        elif codec_name.lower() == "powerdivx":
            extention = "psb"
        elif codec_name.lower() == "subviewer":
            extention = "sub"
        elif codec_name.lower() == "vplayer":
            extention = "txt"
"""
