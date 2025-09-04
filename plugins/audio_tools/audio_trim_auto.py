import asyncio
import datetime
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
    delete_msg,
    dmsg_edit,
    msg_edit,
)
from plugins.audio_helper import Ranjan

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^aautotrimmer"))
async def aautotrimmer_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
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
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )
    if not os.path.exists(
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    ):
        os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

    if reply_msg.media:
        logger.info(
            f"☘️ Sent file for Auto Trimming Audio. User {update.from_user.id} @{update.from_user.username}"
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
            f"☘️ Sent url for Auto Trimming Audio. User {update.from_user.id} @{update.from_user.username}"
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

    # ----------------- STARTING ------------------#
    try:
        duration = 0
        duration = await Ranjan.get_duration(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : {e}")
        return

    if isinstance(duration, str):
        await clear_server(user_id, saved_file_path)
        await msg_edit(bc, f"⚠️ **Error** : Duration not found")
        return

    try:
        time_format = datetime.timedelta(seconds=duration)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : Duration not found")
        return

    if duration < 1:
        await clear_server(user_id, saved_file_path)
        await msg_edit(
            bc,
            f"⚠️ **Error** : Duration is less than 1 Sec\n\n👉 __For Audio Trimming, Audio length should be minimum 6 sec__",
        )
        return
    # ---------------- Script ---------------------#
    PROCESS_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    try:
        auto_trim_sec = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"Total Duration - {time_format} ({duration}s)\n\nNow send your list of seconds separated by `,`(comma).\nEx: `5,20,30,15,10`.\nThis will Trim Audio at 5, 20, 30, 15, and 10 seconds.\n\n**Note :** The list can have a maximum of 15 valid positions",
                reply_markup=PROCESS_CANCEL,
                filters=filters.text,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await auto_trim_sec.delete()
            await auto_trim_sec.request.delete()
        except:
            pass
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=PROCESS_CANCEL)
            await ccc.delete()
        except:
            pass
        await clear_server(user_id, saved_file_path)
        try:
            await bc.edit(
                text=f"⚠️ Process Time Out\n\n👉 Now Resend your Audio/Direct link"
            )
        except:
            pass
        return

    if auto_trim_sec.text == "Cancel":
        await clear_server(user_id, saved_file_path)
        await bc.edit(text=f"Process Cancelled  ✅")
        return
    else:
        auto_trim_sec = auto_trim_sec.text

    DURATION_BUTTON = ReplyKeyboardMarkup(
        [["5", "10", "15"], ["20", "25", "30"], ["40", "50", "60"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        atrim_duration = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text="Select the Interval Duration of Triming\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=DURATION_BUTTON,
                filters=filters.text,
            ),
            Config.PROCESS_TIMEOUT,
        )
        try:
            await atrim_duration.delete()
            await atrim_duration.request.delete()
        except:
            pass
        atrim_duration = atrim_duration.text
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=DURATION_BUTTON)
            await ccc.delete()
        except:
            pass
        atrim_duration = "Cancel"

    if atrim_duration == "5":
        atrim_duration = "5"
    elif atrim_duration == "10":
        atrim_duration = "10"
    elif atrim_duration == "15":
        atrim_duration = "15"
    elif atrim_duration == "20":
        atrim_duration = "20"
    elif atrim_duration == "25":
        atrim_duration = "25"
    elif atrim_duration == "30":
        atrim_duration = "30"
    elif atrim_duration == "40":
        atrim_duration = "40"
    elif atrim_duration == "50":
        atrim_duration = "50"
    elif atrim_duration == "60":
        atrim_duration = "60"
    else:
        atrim_duration = atrim_duration

    if atrim_duration == "Cancel":
        await clear_server(user_id, saved_file_path)
        await msg_edit(bc, f"⚠️ Process Time out, Resend file again")
        return

    try:
        mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    except:
        mainquality_audio = 128

    if reply_msg.media:
        try:
            file_video = update.message.reply_to_message
            media = file_video.video or file_video.document or file_video.audio
            description_ = media.file_name
            if "." in description_:
                try:
                    splitit = description_.split(".")
                    extension = splitit[-1]
                except:
                    extension = "mp3"
            else:
                extension = "mp3"
            description_ = os.path.splitext(description_)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
            extension = "mp3"

    else:
        try:
            #  file_name = saved_file_path.split("/")[-1]
            file_name = os.path.basename(saved_file_path)
            extension = "mp3"
            description_ = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
            extension = "mp3"

    try:
        raw_user_input = [int(i.strip()) for i in auto_trim_sec.split(",")]
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(
            bc,
            f"⚠️ **Error** : {e}\n\nPlease follow this format 👇\n\nDuration List Separate by Comma (,) \nFor Example 👉 `5,10,15,20,40`",
        )
        return

    valid_positions = []
    invalid_positions = []

    for pos in raw_user_input:
        if 0 > pos > duration:
            invalid_positions.append(str(pos))
        else:
            valid_positions.append(pos)

    if not valid_positions:
        await clear_server(user_id, saved_file_path)
        await msg_edit(bc, f"⚠️ **Error** Invalid positions are {valid_positions}")
        return

    if len(valid_positions) > 15:
        await clear_server(user_id, saved_file_path)
        await msg_edit(
            bc,
            f"⚠️ **Error** : Send below than 15\n\n👉 You sent {len(valid_positions)} time for Trimming",
        )
        return

    print(f"Valid positions are {valid_positions}")
    print(f"Invalid positions are {invalid_positions}")
    if invalid_positions:
        INVALID_POSITION = "Found {invalid_positions_count} invalid positions ({invalid_positions}).\n\nAudio Trimming is ignoring these!."
        txt = INVALID_POSITION.format(
            invalid_positions_count=len(invalid_positions),
            invalid_positions=", ".join(invalid_positions),
        )
        await update.message.reply(text=txt, reply_to_message_id=reply_msg.id)
    #   await clear_server(user_id, saved_file_path)
    #   return

    else:

        try:
            bco = await bc.edit(f"**Trimming....**")
        except:
            await delete_msg(bc)
            try:
                bco = await update.message.reply(
                    "**Trimming....**", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, saved_file_path)
                logger.info(
                    f" ⚠️⚠️ can't send cd message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                return

    ffmpeg_cmd = [
        "ffmpeg",
        "-ss",
        "",  # To be replaced in loop
        "-i",
        saved_file_path,
        "-t",
        f"{atrim_duration}",
        "-b:a",
        f"{mainquality_audio}K",
        "",  # To be replaced in loop
    ]

    logger.info(
        "Audio Auto Trim at positions %s from location: %s for %s",
        valid_positions,
        saved_file_path,
        update.message.chat.id,
    )

    trim_directory = f"{Config.DOWNLOAD_LOCATION}/{str(update.from_user.id)}"
    if not os.path.isdir(trim_directory):
        os.makedirs(trim_directory)

    for i, sec in enumerate(valid_positions):
        trimmed_audio = os.path.join(trim_directory, f"{i+1}.{extension}")
        ffmpeg_cmd[2] = str(sec)
        ffmpeg_cmd[-1] = trimmed_audio
        logger.debug(ffmpeg_cmd)
        output = await Ranjan.run_subprocess(ffmpeg_cmd)
        logger.debug(
            "FFmpeg output\n %s \n %s",
            output[0].decode(),
            output[1].decode(),
        )

        try:
            cd = await bco.edit(
                "`{current}` of `{total}` Audio Trimmed ✅".format(
                    current=i + 1, total=len(valid_positions)
                )
            )
        except FloodWait as f:
            asyncio.sleep(f.x)
            cd = await bco.edit(
                "`{current}` of `{total}` Audio Trimmed ✅".format(
                    current=i + 1, total=len(valid_positions)
                )
            )

        try:
            ef = await update.message.reply(
                "**Uploading....**", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(user_id, saved_file_path, trimmed_audio, trim_directory)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        try:
            start_sec = datetime.timedelta(seconds=sec)
            end_time_sec = sec + int(atrim_duration)
            end_sec = datetime.timedelta(seconds=end_time_sec)
            file_name = os.path.basename(trimmed_audio)
            file_size_output = os.path.getsize(trimmed_audio)  # Working
            output_size = humanbytes(file_size_output)
            caption = f"File Name : {file_name}\n\nFile Size : {output_size}\nBit Rate : {mainquality_audio} kbps\nTrimmed - {start_sec} To {end_sec}"
        except Exception as e:
            print(e)
            caption = ""

        try:
            duration = await Ranjan.get_duration(trimmed_audio)
        except:
            duration = 0

        if (await db.get_upload_as(update.from_user.id)) is True:
            try:
                progress_bar = Progress(update.from_user.id, bot, ef)
                c_time = time.time()
                try:
                    await update.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_AUDIO
                    )
                except:
                    pass
                diksha = await bot.send_audio(
                    chat_id=update.message.chat.id,
                    audio=trimmed_audio,
                    caption=caption,
                    duration=duration,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.progress_for_pyrogram,
                    progress_args=("**Uploading....**", c_time),
                )

                if (
                    CANCEL_PROCESS[update.message.chat.id]
                    and ef.id in CANCEL_PROCESS[update.message.chat.id]
                ):
                    await clear_server(
                        user_id, saved_file_path, trimmed_audio, trim_directory
                    )
                    return

                last_msg = None
                last_msg = await dmsg_edit(ef, ".")
                await delete_msg(last_msg)
                """
                if Config.LOG_CHANNEL:
                    try:
                        cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                        await cmf2v.reply_text(
                            f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Auto Trimmer"
                        )
                    except FloodWait:
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(e)
                """
            #      logger.info(f" Audio Auto Trimmed Successfully ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}")
            except FloodWait as f:
                await asyncio.sleep(f.x)
            except Exception as e:
                print(e)
                await msg_edit(ef, f"⚠️ **Error** : {e}")
            try:
                os.remove(trimmed_audio)
            except:
                pass
        else:
            try:
                progress_bar = Progress(update.from_user.id, bot, ef)
                c_time = time.time()
                try:
                    await update.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_DOCUMENT
                    )
                except:
                    pass
                diksha = await bot.send_document(
                    chat_id=update.message.chat.id,
                    audio=trimmed_audio,
                    caption=caption,
                    force_document=True,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.progress_for_pyrogram,
                    progress_args=("**Uploading....**", c_time),
                )

                if (
                    CANCEL_PROCESS[update.message.chat.id]
                    and ef.id in CANCEL_PROCESS[update.message.chat.id]
                ):
                    await clear_server(
                        user_id, saved_file_path, trimmed_audio, trim_directory
                    )
                    return

                last_msg = None
                last_msg = await dmsg_edit(ef, ".")
                await delete_msg(last_msg)
                """          
                if Config.LOG_CHANNEL:
                    try:
                        cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                        await cmf2v.reply_text(
                            f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Audio Auto Trimmer"
                        )
                    except FloodWait:
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(e)
                """
            except FloodWait as f:
                await asyncio.sleep(f.x)
            except Exception as e:
                print(e)
                await msg_edit(ef, f"⚠️ **Error** : {e}")
            try:
                os.remove(trimmed_audio)
            except:
                pass
        await asyncio.sleep(2)
        continue

    await delete_msg(cd)
    try:
        await update.message.reply(
            "Your given Durations are `{given_dur}`\n\nAudio Trimmed : `{current}` of `{total}`  ✅".format(
                current=i + 1, total=len(valid_positions), given_dur=auto_trim_sec
            ),
            reply_to_message_id=reply_msg.id,
        )
    except:
        pass
    logger.info(
        f" Audio Auto Trimmed Successfully ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    await clear_server(user_id, saved_file_path, trimmed_audio, trim_directory)
