import asyncio
import logging
import os
import time

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup

from config import Config
from database.database import Database
from helpers.display_progress import Progress, humanbytes
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    delete_msg,
    dmsg_edit,
    msg_edit,
)
from plugins.audio_helper import Ranjan

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def audio_process(
    video_file,
    audio_file,
    output_directory,
    new_file_name,
    mainquality_audio,
    third_file,
    fourth_file,
    fifth_file,
):
    out_put_file_name = output_directory + "/" + new_file_name + ".mp3"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-i",
        audio_file,
        "-i",
        third_file,
        "-i",
        fourth_file,
        "-i",
        fifth_file,
        "-filter_complex",
        "[0:a][1:a][2:a][3:a][4:a]concat=n=5:v=0:a=1",
        "-b:a",
        f"{mainquality_audio}K",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


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


async def asking_file(bot, update, texts):
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".audio_one.mp3"
    )
    ASK_AUDIO_B = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_file = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=texts,
                reply_markup=ASK_AUDIO_B,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        await ask_file.request.delete()
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out\n\n👉 Resend your files And try Again",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await clear_server(user_id, saved_file_path)
        ask_file = False

    if ask_file.text == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        await clear_server(user_id, saved_file_path)

    return ask_file


@Client.on_callback_query(filters.regex("^fifthaudio"))
async def merge_fifth_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
    stickeraudio = None
    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if os.path.isdir(download_path):
        await update.message.reply(
            "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__",
            reply_to_message_id=reply_msg.id,
        )
        return

    file_audios = update.message.reply_to_message
    media = file_audios.video or file_audios.audio or file_audios.document
    media.file_size
    if media.file_size > (100 * 1024 * 1024):  # 100 MB Limit each file
        ab = await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"⚠️ I don't accept more than 100 MB ",
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
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".firstaudio.mp3"
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
            f"☘️ Sent file for Merging Audio 5. User {update.from_user.id} @{update.from_user.username}"
        )
        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of Merged Audio**",
                reply_markup=BUTTON_CANCEL,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            )
            await ask_.delete()
            await ask_.request.delete()
            cfile_name = ask_.text

            if cfile_name == "Cancel":
                await update.message.reply(
                    "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                )
                logger.info(
                    f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                await clear_server(user_id, saved_file_path)
                return

            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[
                :60
            ]  # truncated_text = new_name[0:60] # File name reduced

            IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
            if len(cfile_name) > 60:
                long_msg = await update.message.reply(
                    IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name))
                )
                await clear_server(user_id, saved_file_path)
                return

        # ------------ Asking For Audio 2----------#
        texts = f"**Now Send 🎵 Audio 2 To Merge**"
        request_aud = await asking_file(bot, update, texts)
        while True:
            if request_aud.text:
                if request_aud.text in BOT_CMDS:
                    texts = f"⚠️ Currently Don't use Commands!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(bot, update, texts)

                elif request_aud.text == "Cancel":
                    break

                else:
                    texts = f"⚠️ Currently Don't send me Texts\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(bot, update, texts)
                    continue

            if request_aud.video or request_aud.audio or request_aud.document:
                filetype = (
                    request_aud.document or request_aud.audio or request_aud.video
                )

                try:
                    recogniser_ = filetype.mime_type
                except Exception:
                    texts = f"⚠️ File Type Not found!!!\n\n👉 **Send me Audio 🎵 File To Merge**"
                    request_aud = await asking_file(bot, update, texts)
                    continue

                if recogniser_ is None:
                    texts = f"⚠️ File Type Not found!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    request_aud = await asking_file(bot, update, texts)

                if filetype.mime_type.startswith("audio/"):
                    break

                elif filetype.mime_type.startswith("video/"):
                    texts = f"⚠️ I am Asking you for Audio File.\n\n👉 So, currently Don't send video file"
                    request_aud = await asking_file(bot, update, texts)

                else:
                    texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Now send me another 🎵 Audio"
                    request_aud = await asking_file(bot, update, texts)
                    continue

            else:
                texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Send me Now another 🎵 Audio"
                request_aud = await asking_file(bot, update, texts)
                continue

        if request_aud.text == "Cancel":
            return
        # ------------ Asking For Audio 3----------#
        texts = f"**Now Send 🎵 Audio-3 To Merge**"
        third_audio = await asking_file(bot, update, texts)
        while True:
            if third_audio.text:
                if third_audio.text in BOT_CMDS:
                    texts = f"⚠️ Currently Don't use Commands!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    third_audio = await asking_file(bot, update, texts)

                elif third_audio.text == "Cancel":
                    break

                else:
                    texts = f"⚠️ Currently Don't send me Texts\n\n👉 **Send me 🎵 Audio File To Merge**"
                    third_audio = await asking_file(bot, update, texts)
                    continue

            if third_audio.video or third_audio.audio or third_audio.document:
                filetype = (
                    third_audio.document or third_audio.audio or third_audio.video
                )

                try:
                    recogniser_ = filetype.mime_type
                except Exception:
                    texts = f"⚠️ File Type Not found!!!\n\n👉 **Send me Audio 🎵 File To Merge**"
                    third_audio = await asking_file(bot, update, texts)
                    continue

                if recogniser_ is None:
                    texts = f"⚠️ File Type Not found!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    third_audio = await asking_file(bot, update, texts)

                if filetype.mime_type.startswith("audio/"):
                    break

                elif filetype.mime_type.startswith("video/"):
                    texts = f"⚠️ I am Asking you for Audio File.\n\n👉 So, currently Don't send video file"
                    third_audio = await asking_file(bot, update, texts)

                else:
                    texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Now send me another 🎵 Audio"
                    third_audio = await asking_file(bot, update, texts)
                    continue

            else:
                texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Send me Now another 🎵 Audio"
                third_audio = await asking_file(bot, update, texts)
                continue

        if third_audio.text == "Cancel":
            return

        # ------------ Asking For Audio 4----------#
        texts = f"**Now Send 🎵 Audio-4 To Merge**"
        fourth_audio = await asking_file(bot, update, texts)
        while True:
            if fourth_audio.text:
                if fourth_audio.text in BOT_CMDS:
                    texts = f"⚠️ Currently Don't use Commands!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fourth_audio = await asking_file(bot, update, texts)

                elif fourth_audio.text == "Cancel":
                    break

                else:
                    texts = f"⚠️ Currently Don't send me Texts\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fourth_audio = await asking_file(bot, update, texts)
                    continue

            if fourth_audio.video or fourth_audio.audio or fourth_audio.document:
                filetype = (
                    fourth_audio.document or fourth_audio.audio or fourth_audio.video
                )

                try:
                    recogniser_ = filetype.mime_type
                except Exception:
                    texts = f"⚠️ File Type Not found!!!\n\n👉 **Send me Audio 🎵 File To Merge**"
                    fourth_audio = await asking_file(bot, update, texts)
                    continue

                if recogniser_ is None:
                    texts = f"⚠️ File Type Not found!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fourth_audio = await asking_file(bot, update, texts)

                if filetype.mime_type.startswith("audio/"):
                    break

                elif filetype.mime_type.startswith("video/"):
                    texts = f"⚠️ I am Asking you for Audio File.\n\n👉 So, currently Don't send video file"
                    fourth_audio = await asking_file(bot, update, texts)

                else:
                    texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Now send me another 🎵 Audio"
                    fourth_audio = await asking_file(bot, update, texts)
                    continue

            else:
                texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Send me Now another 🎵 Audio"
                fourth_audio = await asking_file(bot, update, texts)
                continue

        if fourth_audio.text == "Cancel":
            return

        # ------------ Asking For Audio 5----------#
        texts = f"**Now Send 🎵 Audio-5 To Merge**"
        fifth_audio = await asking_file(bot, update, texts)
        while True:
            if fifth_audio.text:
                if fifth_audio.text in BOT_CMDS:
                    texts = f"⚠️ Currently Don't use Commands!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fifth_audio = await asking_file(bot, update, texts)

                elif fifth_audio.text == "Cancel":
                    break

                else:
                    texts = f"⚠️ Currently Don't send me Texts\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fifth_audio = await asking_file(bot, update, texts)
                    continue

            if fifth_audio.video or fifth_audio.audio or fifth_audio.document:
                filetype = (
                    fifth_audio.document or fifth_audio.audio or fifth_audio.video
                )

                try:
                    recogniser_ = filetype.mime_type
                except Exception:
                    texts = f"⚠️ File Type Not found!!!\n\n👉 **Send me Audio 🎵 File To Merge**"
                    fifth_audio = await asking_file(bot, update, texts)
                    continue

                if recogniser_ is None:
                    texts = f"⚠️ File Type Not found!!\n\n👉 **Send me 🎵 Audio File To Merge**"
                    fifth_audio = await asking_file(bot, update, texts)

                if filetype.mime_type.startswith("audio/"):
                    break

                elif filetype.mime_type.startswith("video/"):
                    texts = f"⚠️ I am Asking you for Audio File.\n\n👉 So, currently Don't send video file"
                    fifth_audio = await asking_file(bot, update, texts)

                else:
                    texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Now send me another 🎵 Audio"
                    fifth_audio = await asking_file(bot, update, texts)
                    continue

            else:
                texts = f"⚠️ You are using Audio-Audio Merger\n\n👉 So, Send me Now another 🎵 Audio"
                fifth_audio = await asking_file(bot, update, texts)
                continue

        if fifth_audio.text == "Cancel":
            return
        # ------------------ Downloading 1--------#
        try:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
                text="**Downloading Audio 1....**",
                reply_to_message_id=reply_msg.id,
            )
        except:
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return
        COUNT.append(user_id)

        progress_bar = Progress(update.from_user.id, bot, ab)
        c_time = time.time()
        real_video = await bot.download_media(
            message=reply_msg,
            file_name=saved_file_path,
            progress=progress_bar.progress_for_pyrogram,
            progress_args=("**Downloading Audio-1....**", c_time),
        )

        if (
            CANCEL_PROCESS[update.message.chat.id]
            and ab.id in CANCEL_PROCESS[update.message.chat.id]
        ):
            await clear_server(user_id, saved_file_path)
            return

        try:
            bc = await ab.edit(f"Audio-1 Downloaded Successfully ✅")
        except:
            await delete_msg(ab)
            try:
                bc = await update.message.reply(
                    "Audio-1 Downloaded Successfully ✅",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return
        # ------------------ Downloading 2--------#

        audio_file_path = (
            Config.DOWNLOAD_LOCATION
            + "/"
            + str(update.from_user.id)
            + ".secondaudio.mp3"
        )
        if request_aud.media:
            try:
                bca = await bc.edit(f"**Downloading Audio-2....**")
            except:
                await delete_msg(bc)
                try:
                    bca = await update.message.reply(
                        "**Downloading Audio-2....**",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(user_id, saved_file_path)
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
            progress_bar = Progress(update.from_user.id, bot, bca)
            c_time = time.time()
            real_audio = await bot.download_media(
                message=request_aud,
                file_name=audio_file_path,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Downloading Audio-2....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and bca.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, audio_file_path)
                return

            try:
                bcb = await bca.edit(f"Audio-2 Downloaded Successfully ✅")
            except:
                await delete_msg(bca)
                try:
                    bcb = await update.message.reply(
                        "Audio-2 Downloaded Successfully ✅",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(user_id, saved_file_path, audio_file_path)
                    logger.info(
                        f" ⚠️⚠️ can't send bcb message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
        # ------------------ Downloading 3--------#

        third_audio_path = (
            Config.DOWNLOAD_LOCATION
            + "/"
            + str(update.from_user.id)
            + ".thirdaudio.mp3"
        )
        if third_audio.media:
            try:
                bcc = await bcb.edit(f"**Downloading Audio-3....**")
            except:
                await delete_msg(bcb)
                try:
                    bcc = await update.message.reply(
                        "**Downloading Audio-3....**",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(user_id, saved_file_path, audio_file_path)
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
            progress_bar = Progress(update.from_user.id, bot, bcc)
            c_time = time.time()
            real_audio = await bot.download_media(
                message=third_audio,
                file_name=third_audio_path,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Downloading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and bcc.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(
                    user_id, saved_file_path, audio_file_path, third_audio_path
                )
                return

            try:
                bosi = await bcc.edit(f"Audio-3 Downloaded Successfully ✅")
            except:
                await delete_msg(bcc)
                try:
                    bosi = await update.message.reply(
                        "Audio-3 Downloaded Successfully ✅",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(
                        user_id, saved_file_path, audio_file_path, third_audio_path
                    )
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
        # ------------------ Downloading 4--------#

        fourth_audio_path = (
            Config.DOWNLOAD_LOCATION
            + "/"
            + str(update.from_user.id)
            + ".fourththaudio.mp3"
        )
        if fourth_audio.media:
            try:
                bdd = await bosi.edit(f"**Downloading Audio-4....**")
            except:
                await delete_msg(bosi)
                try:
                    bdd = await update.message.reply(
                        "**Downloading Audio-4....**",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(
                        user_id, saved_file_path, audio_file_path, third_audio_path
                    )
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
            progress_bar = Progress(update.from_user.id, bot, bdd)
            c_time = time.time()
            real_audio = await bot.download_media(
                message=fourth_audio,
                file_name=fourth_audio_path,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Downloading Audio-4....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and bdd.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(
                    user_id, saved_file_path, audio_file_path, third_audio_path
                )
                await clear_server_two(fourth_audio)
                return

            try:
                cmm = await bdd.edit(f"Audio-4 Downloaded Successfully ✅")
            except:
                await delete_msg(bdd)
                try:
                    cmm = await update.message.reply(
                        "Audio-4 Downloaded Successfully ✅",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(
                        user_id, saved_file_path, audio_file_path, third_audio_path
                    )
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
        # ------------------ Downloading 5--------#

        fifth_audio_path = (
            Config.DOWNLOAD_LOCATION
            + "/"
            + str(update.from_user.id)
            + ".fifthaudio.mp3"
        )
        if fifth_audio.media:
            try:
                cmmd = await cmm.edit(f"**Downloading Audio-5....**")
            except:
                await delete_msg(cmm)
                try:
                    cmmd = await update.message.reply(
                        "**Downloading Audio-5....**",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(user_id, saved_file_path, audio_file_path)
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return
            progress_bar = Progress(update.from_user.id, bot, cmmd)
            c_time = time.time()
            real_audio = await bot.download_media(
                message=fifth_audio,
                file_name=fifth_audio_path,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Downloading Audio-5....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and cmmd.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(
                    user_id, saved_file_path, audio_file_path, third_audio_path
                )
                await clear_server_two(fourth_audio, fifth_audio_path)
                return

            try:
                bc = await cmmd.edit(f"Audio-5 Downloaded Successfully ✅")
            except:
                await delete_msg(bcc)
                try:
                    bc = await update.message.reply(
                        "Audio-5 Downloaded Successfully ✅",
                        reply_to_message_id=reply_msg.id,
                    )
                except:
                    await clear_server(
                        user_id, saved_file_path, audio_file_path, third_audio_path
                    )
                    await clear_server_two(fourth_audio, fifth_audio_path)
                    logger.info(
                        f" ⚠️⚠️ can't send bc message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
                    return

    try:
        file_video = update.message.reply_to_message
        media = file_video.video or file_video.audio or file_video.document
        description_ = media.file_name
        description_ = os.path.splitext(description_)[0]  # +'.mp3'
    except:
        description_ = "Default_Name"

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            description_ = f"{cfile_name}"
        except:
            description_ = "Default_Name"

    try:
        new_file_name = f"{cfile_name}"
    except:
        new_file_name = description_

    try:
        cd = await bc.edit(f"**5 Audios Merging....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**5 Audios Merging....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path, audio_file_path)
            await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    stickeraudio = None
    try:
        stickeraudio = await bot.send_sticker(
            chat_id=update.message.chat.id,
            sticker="CAACAgUAAxkBAAIbKGEOVBAhvPJCbV515KyEKMDkMZrXAALEAgACBG2gVsF1Ng9n9CrHHgQ",
        )
    except:
        pass

    try:
        mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    except:
        mainquality_audio = 128

    try:
        trimn = None
        trimn = await audio_process(
            saved_file_path,
            audio_file_path,
            Config.DOWNLOAD_LOCATION,
            new_file_name,
            mainquality_audio,
            third_audio_path,
            fourth_audio_path,
            fifth_audio_path,
        )
    except Exception as e:
        await clear_server(user_id, saved_file_path, trimn, audio_file_path)
        await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
        print(e)
        await msg_edit(cd, f"⚠️ **Error** : {e}")
        await delete_msg(stickeraudio)
        return

    if trimn is None:
        await clear_server(user_id, saved_file_path, trimn, audio_file_path)
        await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
        await msg_edit(cd, f"⚠️ **Error** : in Merging")
        await delete_msg(stickeraudio)
        return

    try:
        merged_duration = await Ranjan.get_duration(trimn)
    except Exception as e:
        await clear_server(user_id, saved_file_path, trimn, audio_file_path)
        await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
        print(e)
        await msg_edit(cd, f"⚠️ **Error** : {e}")
        await delete_msg(stickeraudio)
        return

    try:
        await delete_msg(stickeraudio)
        ef = await cd.edit(f"**Uploading....**")
    except:
        await delete_msg(cd)
        try:
            ef = await update.message.reply(
                "**Uploading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path, trimn, audio_file_path)
            await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    if await db.get_mainquality_a(update.from_user.id):
        mainquality_audioi = await db.get_mainquality_a(update.from_user.id)
    else:
        mainquality_audioi = " "

    try:
        file_size_output = os.path.getsize(trimn)  # Working
        output_size = humanbytes(file_size_output)
        description_ = (
            "File Name : "
            + description_
            + ".mp3"
            + f"\n\nFile Size : {output_size}\nBit Rate : {mainquality_audioi} kbps\n➕ 5 Audio Merged"
        )
    except:
        description_ = description_ + ".mp3" + f"\n\n➕ 5 Audio Merged"

    if (await db.get_upload_as(update.from_user.id)) is True:
        try:
            progress_bar = Progress(update.from_user.id, bot, ef)
            c_time = time.time()
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
            except:
                pass
            diksha = await bot.send_video(
                chat_id=update.message.chat.id,
                video=trimn,
                caption=description_,
                duration=merged_duration,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, trimn, audio_file_path)
                await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Merger"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio Audio Merged ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    else:
        try:
            progress_bar = Progress(update.from_user.id, bot, ef)
            c_time = time.time()
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            except:
                pass
            diksha = await bot.send_document(
                chat_id=update.message.chat.id,
                document=trimn,
                caption=description_,
                force_document=True,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, trimn, audio_file_path)
                await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Merger"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio-Audio Merged ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    await clear_server(user_id, saved_file_path, trimn, audio_file_path)
    await clear_server_two(third_audio_path, fourth_audio, fifth_audio_path)
