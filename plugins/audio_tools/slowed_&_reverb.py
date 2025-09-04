import asyncio
import datetime
import logging
import os
import time

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from config import Config
from database.database import Database
from helpers.display_progress import Progress, humanbytes
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    delete_msg,
    dmsg_edit,
    msg_edit,
)
from plugins.audio_helper import Ranjan

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import sox


async def audio_process(video_file, output_directory, new_file_name, audio_quality):
    wav_quality = "pcm_s16le"
    out_put_file_name = output_directory + new_file_name + ".wav"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-acodec",
        f"{wav_quality}",
        "-ar",
        "44100",  # 22050 for less size # 8 bit
        "-filter:a",
        f"atempo={audio_quality}",
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


@Client.on_callback_query(filters.regex("^psox"))
async def psox_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    speeddbaud = await db.get_audio_speed(id=user_id)
    bassaudio = await db.get_bassaudio(id=user_id)
    trebleaudio = await db.get_trebleaudio(id=user_id)
    audio_reverb = await db.get_audio_reverb(user_id)

    CONFIRM_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Continue", callback_data="esox"),
            ],
            [InlineKeyboardButton("Back", callback_data="amainback")],
        ]
    )

    texts_a = f"✶ Effects can be Added (Bass, Treble, Speed, Reverb). Your variables in settings 👇\n\n"
    texts_b = f"Bass Range = **{bassaudio}**, Treble Range = **{trebleaudio}**\n"
    texts_c = f"Audio Speed = **{speeddbaud}**, Audio Reverb = **{audio_reverb}**\n\n"
    texts_d = f"You can change variables in /settings\n\n✶ **Note :-** Output Audio Format is WAV, You can convert that to MP3\n"
    await update.message.reply(
        f"{texts_a}{texts_b}{texts_c}{texts_d}",
        reply_markup=CONFIRM_BUTTON,
        reply_to_message_id=reply_msg.id,
    )
    return


@Client.on_callback_query(filters.regex("^esox"))
async def _esox(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    """
    await update.message.reply(
        "⚠️ Currently Disabled Slowed & Reverb Function", reply_to_message_id=reply_msg.id
    )
    try:
        del Config.TIME_GAP_STORE[update.from_user.id]
    except Exception as e:
        logger.info(f"⚠️ Error Compress TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
    return
    """
    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if os.path.isdir(download_path):
        await update.message.reply(
            "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__",
            reply_to_message_id=reply_msg.id,
        )
        return

    if reply_msg.video or reply_msg.audio:
        try:
            files_audio = update.message.reply_to_message
            medias = files_audio.video or files_audio.audio
            duratio = medias.duration
        except Exception as e:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"**⚠️ Error** : {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if duratio > 1200:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ I Boost Bass of song upto 20 mins",
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
    """
    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.audio or file_video.document
            description_ = media.file_name
        except:
            description_ = "Default_Name.mp3"

    else:
        try:
            description_ = os.path.basename(saved_file_path)
        except:
            description_ = "Default_Name.mp3"

    try:
        saved_file_path = Config.DOWNLOAD_LOCATION + "/" + "/" + str(update.from_user.id) + description_
    except:
        saved_file_path = Config.DOWNLOAD_LOCATION + "/" + "/" + str(update.from_user.id) + "Default_Name.mp3"
    """
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mp3"
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
            f"☘️ Sent file for making audio slowed n Reverb. User {update.from_user.id} @{update.from_user.username}"
        )
        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of Audio**",
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

            if "." in cfile_name:
                try:
                    splitit = cfile_name.split(".")
                    (splitit[-1])
                except:
                    pass
            else:
                pass

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
                    "Media Downloaded Successfully ✅",
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
            f"☘️ Sent url for making audio slowed n Reverb. User {update.from_user.id} @{update.from_user.username}"
        )
        saved_file_path = reply_msg.text
        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of Audio**",
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

            if "." in cfile_name:
                try:
                    splitit = cfile_name.split(".")
                    (splitit[-1])
                except:
                    pass
            else:
                pass

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

    if trim_vid_dur > 600:
        await clear_server(user_id, saved_file_path)
        await msg_edit(
            bc, f"⚠️ Send Songs which duration is less than 00:10:00 minutes."
        )
        return

    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.document or file_video.audio
            description_ = media.file_name
            if "." in description_:
                try:
                    splitit = description_.split(".")
                    (splitit[-1])
                except:
                    pass
            else:
                pass
            description_ = os.path.splitext(description_)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
    else:
        try:
            #  file_name = saved_file_path.split("/")[-1]
            file_name = os.path.basename(saved_file_path)
            description_ = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            description_ = f"{cfile_name}"
        except:
            description_ = "Default_Name"

    try:
        new_file_name = f"{cfile_name}"  # .{extension}
    except:
        new_file_name = f"{description_}"  # .{extension}

    try:
        cd = await bc.edit(f"**Converting....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**Converting....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path)
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
        bassaudio = await db.get_bassaudio(update.from_user.id)
        bassaudio = int(bassaudio)
    except:
        bassaudio = 5

    try:
        trebleaudio = await db.get_trebleaudio(update.from_user.id)
        trebleaudio = int(trebleaudio)
    except:
        trebleaudio = 5

    try:
        audio_quality = await db.get_audio_speed(update.from_user.id)
        audio_quality = int(audio_quality)
        audio_quality = audio_quality / 100
    except:
        audio_quality = 1

    try:
        audio_reverb = await db.get_audio_reverb(update.from_user.id)
        audio_reverb = int(audio_reverb)
    except:
        audio_reverb = 40

    try:
        audio_vol = await db.get_audio_vol(update.from_user.id)
        audio_vol = int(audio_vol)
        audio_vol = audio_vol
    except:
        audio_vol = 50  # room

    try:
        outputs = None
        outputs = await audio_process(
            saved_file_path, Config.DOWNLOAD_LOCATION, new_file_name, audio_quality
        )
    except Exception as e:
        await clear_server(user_id, saved_file_path, outputs)
        print(e)
        await msg_edit(cd, f"⚠️ **Error** : {e}")
        await delete_msg(stickeraudio)
        return

    if outputs is None:
        await clear_server(user_id, saved_file_path, outputs)
        await msg_edit(cd, f"⚠️ **Error** in Conversation")
        await delete_msg(stickeraudio)
        return

    trimn = None
    trimn = Config.DOWNLOAD_LOCATION + "/" + f"{new_file_name}l.wav"
    try:
        tfm = sox.Transformer()
        tfm.bass(gain_db=bassaudio)  # slope=.3
        tfm.treble(gain_db=trebleaudio)  # slope=0.3
        # if audio_quality != 1:
        #    logger.info("Tempo added ✅")
        #    tfm.tempo(factor=audio_quality) #speed
        if audio_reverb != 0:
            logger.info("Reverb added ✅")
            tfm.reverb(reverberance=audio_reverb, wet_gain=2)
        tfm.build(outputs, trimn)
    except Exception as e:
        await clear_server(user_id, saved_file_path, trimn, outputs)
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
            await clear_server(user_id, saved_file_path, trimn)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    if await db.get_audio_reverb(update.from_user.id):
        audio_reverb = await db.get_audio_reverb(update.from_user.id)
    else:
        audio_reverb = " "

    if await db.get_audio_speed(update.from_user.id):
        audio_qualityi = await db.get_audio_speed(update.from_user.id)
    else:
        audio_qualityi = " "

    try:
        duration = await Ranjan.get_duration(trimn)
    except Exception as e:
        await clear_server(user_id, saved_file_path, trimn, outputs)
        print(e)
        await msg_edit(ef, f"⚠️ **Error** : {e}")
        return

    try:
        file_size_output = os.path.getsize(trimn)  # Working
        output_size = humanbytes(file_size_output)
        description_ = (
            "File Name : "
            + description_
            + f".wav"
            + f"\n\nBass Range : {bassaudio}\nTreble Range : {trebleaudio}\nAudio Reverb : {audio_reverb}\nSpeed Changed : {audio_qualityi}%\nFile Size : {output_size}"
        )
    except:
        description_ = description_ + f".wav"

    if (await db.get_upload_as(update.from_user.id)) is True:
        try:
            progress_bar = Progress(update.from_user.id, bot, ef)
            c_time = time.time()
            try:
                await update.message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
            except:
                pass
            diksha = await bot.send_audio(
                chat_id=update.message.chat.id,
                audio=trimn,
                caption=description_,
                duration=duration,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, trimn, outputs)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Eq Booster"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio Eq Boosted ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
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
                await clear_server(user_id, saved_file_path, trimn, outputs)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Eq Booster"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio Eq Boosted ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    await clear_server(user_id, saved_file_path, trimn, outputs)
