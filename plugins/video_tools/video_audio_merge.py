import asyncio
import datetime
import logging
import os
import random
import time

from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import Config
from database.database import Database
from helpers.display_progress import Progress, humanbytes
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    humanbytes,
    delete_msg,
    dmsg_edit,
    msg_edit,
)
from plugins.audio_helper import Ranjan, take_screen_shot
from plugins.others.playlist_uploader import playlist_uploader
from plugins.processors import media_uploader, Chitranjan as CH
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

supported_audio_formats = (
    "Opus, Vorbis, MP2, MP3, LC-AAC, HE-AAC, WMAv1, WMAv2, AC3, E-AC3"
)

async def asking_file(c, m, texts):
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    ASK_AUDIO_B = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_file = await asyncio.wait_for(
            c.ask(
                chat_id=m.message.chat.id,
                text=texts,
                reply_markup=ASK_AUDIO_B,
                reply_to_message_id=reply_msg.id,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await ask_file.request.delete()
        except:
            pass
    except asyncio.TimeoutError:
        try:
            await m.message.reply(
                "⚠️ Process Time Out\n\n👉 Resend your files And try Again",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
        await clear_server(user_id, input)
        ask_file = False

    if ask_file.text == "Cancel":
        await clear_server(user_id, input)
        await m.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )

    return ask_file


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

@Client.on_callback_query(filters.regex("^video_audio"))
async def audio_videom_(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
    msg = None

    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

    BUTTON_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    if reply_msg.media:
        VA_MERGE = ReplyKeyboardMarkup(
            [["Merger 1", "Merger 2"], ["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            merging_type = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"✶ **Merger 1** : __In this Function, All existing audio track will be replaced. And will be added your sent Audio (Single Audio).__\n\n✶ **Merger 2** : __In this Function, Your sent Audio track will be Merged, WITHOUT Replacing Existing Audio Tracks and Subtitles (Multi Audio & Subtitles)__\n\n🥰 __Currently the added Audio track will play in Telegram in Both Merger__\n\n✶ __**Click the Button of your choice**__ 👇",
                    reply_markup=VA_MERGE,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await merging_type.delete()
                await merging_type.request.delete()
            except:
                pass
            merging_type = merging_type.text
        except asyncio.TimeoutError:
            try:
                await m.message.reply(
                    "⚠️ Process Time Out, Resend Video",
                    reply_markup=ReplyKeyboardRemove(),
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass
            return
            merging_type = "Cancel"

        if merging_type == "Merger 1":
            merging_type = "Replace_All_Track"
        elif merging_type == "Merger 2":
            merging_type = "Merge_All_Track"
        elif merging_type == "Cancel":
            merging_type = "Cancel"
        else:
            merging_type = "Cancel"

        if merging_type == "Cancel":
            await m.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        new_file_name = "Default_Name"
        if (await db.get_auto_rename(m.from_user.id)) is True:
            texts = f"**Now Send Name of Output Video**"
            bool, cfile_name = await CH.first_ask_name(c, m, texts)
            if bool:
                return

        # ------------ Asking For Audio ----------#
        texts = f"✶ **Supported Audio Formats :** {supported_audio_formats}\n\n**Now Send 🎵 Audio File To Merge**"
        request_aud = await asking_file(c, m, texts)
        while True:
            if request_aud.text:
                if request_aud.text in BOT_CMDS:
                    texts = f"⚠️ Currently Don't use Commands!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(c, m, texts)

                elif request_aud.text == "Cancel":
                    break

                else:
                    texts = f"⚠️ Currently Don't send me Texts\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(c, m, texts)
                    continue

            if request_aud.video or request_aud.audio or request_aud.document:
                filetype = (
                    request_aud.document or request_aud.audio or request_aud.video
                )

                try:
                    recogniser_ = filetype.mime_type
                except Exception:
                    texts = f"⚠️ File Type Not found!!!\n\n👉 **Send me Audio 🎵 File To Merge**"
                    request_aud = await asking_file(c, m, texts)
                    continue

                if recogniser_ is None:
                    texts = f"⚠️ File Type Not found!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(c, m, texts)

                if filetype.mime_type.startswith("audio/"):
                    break

                elif filetype.mime_type.startswith("video/"):
                    texts = f"⚠️ I am Asking you for 🎵 Audio File.\n\n👉 So, currently Don't send video file"
                    request_aud = await asking_file(c, m, texts)

                else:
                    texts = f"⚠️ You are using Video-Audio Merger\n\n👉 So, Now send me 🎵 Audio file"
                    request_aud = await asking_file(c, m, texts)
                    continue

            else:
                texts = f"⚠️ You are using Video-Audio Merger\n\n👉 So, Send me Now 🎵 Audio file"
                request_aud = await asking_file(c, m, texts)
                continue

        if request_aud.text == "Cancel":
            return
        # -------------- Audio Language Name ------------#
        AUD_LANGUAGE = ReplyKeyboardMarkup(
            [["Skip", "Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            audio_language = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"✶ Now send Name of Audio Language in 3 Words to set in metadata.\n\nExamples: \nFor English Audio - `eng`\nFor Hindi Audio - `hin`\nFor Tamil Audio - `tam`\nFor Telugu Audio - `tel` etc.\n\n✶ **Now send me Name of Audio Language**__",
                    reply_markup=AUD_LANGUAGE,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await audio_language.delete()
                await audio_language.request.delete()
            except:
                pass
            audio_language = audio_language.text
        except asyncio.TimeoutError:
            try:
                await m.message.reply(
                    "⚠️ Process Time Out, Resend Video",
                    reply_markup=ReplyKeyboardRemove(),
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass
            return
            audio_language = "Cancel"

        audio_languages = "new"
        if audio_language == "Skip":
            audio_languages = "new"
        elif audio_language == "Cancel":
            audio_languages = "Cancel"
        else:
            audio_languages = audio_language

        if audio_languages == "Cancel":
            await m.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        audio_languages = str(audio_languages)
        audio_languages = audio_languages[0:3]  # truncated_text
        audio_languages = audio_languages.lower()
        logger.info(
            f"🎥 + 🎵 Merger: Audio Language: {audio_languages} By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
        # -------------- Downloading ------------#
        if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
            os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

        texts = CH.processing_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        texts = "**Downloading Video File....**"
        bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
        if bool:
            return

        await CH.start_counting(m)

        bool, real_video = await CH.multi_download(c, m, msg, reply_msg, input)
        if bool:
            return

        texts = f"Video Downloaded Successfully ✅"
        bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
        if bool:
            return
        # ---------- Downloading Audio ------------#
        audio_file_path = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.audio.mp3"

        texts = "**Downloading Audio File....**"
        bool, msg = await CH.DUprogress_msg(c, m, msg, audio_file_path, texts)
        if bool:
            await clear_server_two(input)
            return

        bool, real_audio = await CH.multi_download(c, m, msg, request_aud, audio_file_path)
        if bool:
            await clear_server_two(input)
            return

        texts = f"Audio Downloaded Successfully ✅"
        bool, msg = await CH.cb_message_edit(c, m, msg, audio_file_path, texts)
        if bool:
            await clear_server_two(input)
            return

    else:
        await m.message.reply(
            "⚠️ Video file not Found", reply_to_message_id=reply_msg.id
        )
        return

    bool, duration = await CH.find_duration(m, msg, input)
    if bool:
        await clear_server_two(audio_file_path)
        return

    if reply_msg.media:
        files_name = await CH.WE_file_name(reply_msg)

    else:
        files_name = await CH.url_WE_name(input)

    if (await db.get_auto_rename(m.from_user.id)) is True:
        try:
            files_name = f"{cfile_name}"
        except:
            files_name = "Default_Name"

    new_file_name = files_name
   
    sticker = await CH.simple_sticker_send(c, m)

    output_directory = f"{Config.DOWNLOAD_PATH}/{new_file_name}.mkv"
    if merging_type == "Merge_All_Track":
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-i",
            audio_file_path,
            "-map",
            "0:0",
            "-map",
            "1:0",
            "-map",
            "0:1?",
            "-map",
            "0:2?",
            "-map",
            "0:3?",
            "-map",
            "0:4?",
            "-map",
            "0:5?",
            "-map",
            "0:6?",
            "-map",
            "0:7?",
            "-map",
            "0:8?",
            "-map",
            "0:9?",
            "-map",
            "0:10?",
            "-disposition:a:0",
            "default",
            "-disposition:a:1",
            "none",
            "-shortest",
            "-metadata:s:a:0",
            "title=Audio",  # New added By
            "-metadata:s:a:0",
            f"language={audio_languages}",  # eng #@TheNiceBots
            "-async",
            "1",
            "-strict",
            "-2",
            "-c",
            "copy",
            output_directory,
        ]
    else:
        commands = [
            "ffmpeg",
            "-i",
            input,
            "-i",
            audio_file_path,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-metadata:s:a:0",
            "title=Audio",  # New added By
            "-metadata:s:a:0",
            f"language={audio_languages}",  # eng #@TheNiceBots
            "-c",
            "copy",
            "-shortest",
            output_directory,
        ]

    texts = f"**Video-Audio Merging Now....**"
    bool, output, msg = await CH.command_execute(c, m, msg, commands, output_directory, duration, texts)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(input, audio_file_path)
        return

    if output is None:
        await CH.delete_message(sticker)
        await clear_server_two(input, audio_file_path, output)
        texts = f"⚠️ **Error** : Something Went Wrong!!!\n\n👉 Resend your file And Try Again"        
        await CH.edit_msg(msg, texts)
        return

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(audio_file_path)
        return

    if merging_type == "Merge_All_Track":
        Merge_proccess = "Merger 2"
    else:
        Merge_proccess = "Merger 1"

    captions = (
        "File Name : "
        + new_file_name
        + ".mkv"
        + f"\n\nFile Size : {humanbytes(output_size)}\n➕ Video And Audio Merged\nProcess Done By : **{Merge_proccess}**"
    )
    ft = "Video-Audio Merged ✅"
    premium_upload = CH.U4GB_AVMerger
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(sticker, msg)
        try:
            await media_uploader(c, m, output, captions, ft, premium_upload)
        except:
            pass
        await clear_server(m.from_user.id, input, output, audio_file_path)
        return

    bool, mduration = await CH.find_duration(m, msg, output)
    if bool:
        await CH.delete_message(sticker)
        await clear_server_two(input, audio_file_path)
        return

    await CH.delete_message(sticker)

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(output, audio_file_path)
        return

    await CH.video_upload(c, m, msg, input, output, mduration, captions, ft)
    await clear_server_two(audio_file_path)
    await CH.waiting_time(c, m)
