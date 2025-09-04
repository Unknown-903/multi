import asyncio
import datetime
import logging
import os
import random
import time
import threading
import math
import re
from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from plugins.progress import Progress
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    delete_msg,
    dmsg_edit,
    media_file_id,
    msg_edit,
    humanbytes,
    TimeFormatter,
) 
import asyncio
import datetime
import logging
import os
import time
from pyrogram.file_id import FileId
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import Config
from database.database import Database
from plugins.progress import Progress
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    delete_msg,
    dmsg_edit,
    msg_edit,
    humanbytes,
)
from plugins.audio_helper import Ranjan
from plugins.processors import media_uploader
db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

class CH:
    # For uploading primium sizes
    U4GB_Renamer = "Yes"
    U4GB_VConverter = "Yes"
    U4GB_MKV_MP4Convert = "Yes"
    U4GB_VReOrder = "Yes"
    U4GB_Trimmer = "Yes"
    U4GB_VMerger = "Yes"
    U4GB_AVMerger = "Yes"
    U4GB_VAMute = "Yes"
    U4GB_AudioWAV = "Yes"
    U4GB_AudioFLAC = "Yes"

    # Upload File size limit 1999mb
    Upload_Size_Limit = (1999 * 1024 * 1024) 
    downloading_txt = "**Your Media file is Downloading....**"
    uploading_txt = "**Now, Your File is Uploading....**"
    processing_txt = "**Processing....**" 
    url_recieved_txt = "🔗 URL Recieved, Please Wait...."
    converting_txt = "**Please wait. Converting Now....**"
    audioConvDurLimit = 10800 # Audio conversion duration limit
    songsEqDurLimit = 7200 # seconds in Audio Bass/Treble booster

    # Advanced Progress CallBack Message
    @staticmethod
    async def DUprogress_msg(c, m, msg, file_path, texts):
        bool = True
        reply_msg = m.reply_to_message
        reply_markup = InlineKeyboardMarkup(
            [
                [                        
                    InlineKeyboardButton(
                        "Progress ⚡",
                        callback_data=f"filedlprog/{msg.chat.id}/{msg.id}"                                                                   
                    ),
                    InlineKeyboardButton(
                        "Cancel ❌",
                        callback_data=(
                            f"progcancel/{msg.chat.id}/{msg.id}/{m.from_user.id}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        try:
            bc = await msg.edit(f"{texts}", reply_markup=reply_markup)
            bool = False
        except Exception:
            await delete_msg(msg)
            try:
                bc = await m.message.reply(
                    f"{texts}", reply_markup=reply_markup, reply_to_message_id=reply_msg.id
                )
                bool = False
            except Exception:
                bc = None
                bool = True
                await clear_server(m.from_user.id, file_path)
                logger.info(
                    f" ⚠️⚠️ {texts} can't send message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
        return bool, bc




    # Advanced Messages Send
    @staticmethod
    async def message_send(bot, update, file_path, texts):
        bool = True
        reply_msg = update.reply_to_message
        try:
            ab = await bot.send_message(
                chat_id=update.chat.id,
                text=f"{texts}",
                reply_to_message_id=reply_msg.id,
            )
            bool = False
        except Exception:
            bool = True
            ab = None
            await clear_server(update.from_user.id, file_path)
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        return bool, ab
    
    @staticmethod
    async def cb_message_edit(bot, update, ab, file_path, texts):
        bool = True
        reply_msg = update.reply_to_message
        try:
            bc = await ab.edit(f"{texts}")
            bool = False
        except Exception:
            await delete_msg(ab)
            try:
                bc = await update.reply(
                    f"{texts}", reply_to_message_id=reply_msg.id
                )
                bool = False
            except Exception:
                bc = None
                bool = True
                await clear_server(update.from_user.id, file_path)
                logger.info(
                    f" ⚠️⚠️ {texts} can't send message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
        return bool, bc
    # File Downloader
    @staticmethod
    async def file_download(bot, update, ab, file_path):
        reply_msg = update.reply_to_message
        file_ids = FileId.decode(media_file_id(reply_msg))
        bool = True
        real_media = None
        try:
            times = time.time()
            progress_bar = Progress(update.from_user.id, bot, ab)            
            real_media = await bot.download_media(
                message=reply_msg,
                file_name=file_path,
                progress=progress_bar.ProgressBar,
                progress_args=(f"Downloading.... from DC{file_ids.dc_id}", times),
            )

            if (
                CANCEL_PROCESS[update.chat.id]
                and ab.id in CANCEL_PROCESS[update.chat.id]
            ):
                await clear_server(update.from_user.id, file_path)
                return True, real_media
            return False, real_media
        except Exception as e:
            await clear_server(update.from_user.id, file_path)
            try:
                await ab.edit(f"**⚠️ DL Error:** {e}")
            except:
                await delete_msg(ab)
                try:
                    await update.message.reply(
                        f"**⚠️ DL Error:** {e}", reply_to_message_id=reply_msg.id
                    )
                except:
                    logger.info(
                        f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
            return True, real_media
    @staticmethod
    async def find_duration(m, bc, file_path):
        reply_msg = m.reply_to_message
        bool = True
        duration = 0

        try:
            duration = await Ranjan.get_duration(file_path)
            bool = False
        except Exception as e:
            bool = True
            await clear_server(m.from_user.id, file_path)
            logger.info(e)
            await msg_edit(bc, f"⚠️ **F Duration Error** : {e}")

        if isinstance(duration, str):
            bool = True
            await clear_server(m.from_user.id, file_path)
            await msg_edit(bc, f"⚠️ **Error** : Could not found Duration")

        return bool, duration
    @staticmethod
    async def start_counting(update):
        if update.from_user.id not in COUNT:
            try:
                COUNT.append(update.from_user.id)
            except Exception as e:
                logger.info(
                    f"⚠️ Adding in Count Error: {e}  {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
    
@Client.on_message(filters.private & filters.command("ss"))
async def sss_shots_(c, m):
    user_id = m.from_user.id
    user_name = m.from_user.username
    user_first = m.from_user.first_name
    logger.info(
        f"👉 {m.text} 👈 Sent by User {user_first} {str(user_id)} @{user_name}"
    )
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Features", callback_data="function"),
                InlineKeyboardButton("Instructions", callback_data="instruct"),
            ],
            [InlineKeyboardButton("Pay Now", url="https://t.me/DKBOTZHELP")],
        ]
    )
    if Config.PAID_BOT.upper() == "YES":
        try:
            paid_status = await db.get_paid_status(user_id)
        except:
            await m.reply("⚠️ First Click on /start, Then try again")
            return
        if paid_status["is_paid"]:
            current_date = datetime.datetime.now()
            paid_duration = paid_status["paid_duration"]
            paid_on = paid_status["paid_on"]
            paid_reason = paid_status["paid_reason"]
            integer_paid_duration = int(paid_duration)
            will_expire = paid_on + datetime.timedelta(days=integer_paid_duration)
            if will_expire < current_date:
                try:
                    await db.remove_paid(user_id)
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                try:
                    await c.send_message(
                        m.chat.id,
                        f"👋 Your paid plan has Expired on {will_expire}\n\nIf you want to use the bot, You can do so by Paying.",
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                for i in Config.AUTH_USERS:
                    try:
                        await c.send_message(
                            i,
                            f"🌟 **Plan Expired:** \n\n**User Id:** `{m.from_user.id}`\n\n**User Name:** @{m.from_user.username}\n\n**Plan Validity:** {paid_duration} Days\n\n**Joined On** : {paid_on}\n\n**Discription** : {paid_reason}",
                        )
                    except Exception:
                        logger.info(f"⚠️ Not found id {i}")
                return

            else:
                pass

        else:
            await m.reply_text(
                text="Only paid users can use me. For more information Click on **Instructions** Button\n\nPay ₹49\M Rupees On `dkbotz@ybl` And Send Screenshot To @DKBOTZHELP  ",
                reply_markup=SUB_BUTTONS,
                disable_web_page_preview=True,
                quote=True,
            )
            return

    else:
        if m.from_user.id not in Config.VERIFIED_USERS:
            if Config.FORCE_SUBS:
                owhats = await force_sub(c, m)
                if owhats == 9:
                    return
        # ------------------------------------#
        if m.from_user.id not in Config.VERIFIED_USERS:
            if Config.FORCE_SUBS_TWO:
                whatso = await force_sub_two(c, m)
                if whatso == 9:
                    return
        # ------------------------------------#
        if m.from_user.id not in Config.VERIFIED_USERS:
            if Config.PAID_SUBS:
                whatsp = await paid_service_subs(c, m)
                if whatsp == 9:
                    return

    # ------------------------------------#

    try:
        ban_status = await db.get_ban_status(m.from_user.id)
        if ban_status["is_banned"]:
            await c.delete_messages(
                chat_id=m.chat.id, message_ids=m.id, revoke=True
            )
            await c.send_sticker(
                chat_id=update.chat.id,
                sticker="CAACAgUAAxkBAAESX79jQ3ttwFFl-924jiNO24a4BA_xrgACnAUAApRgGFaLa4T0ra8TrioE",
            )
            await m.reply(
                "**⚠️ Sorry You're Banned❗**\n\nFor help go to @DKBOTZSUPPORT"
            )
            return
    except:
        await m.reply("⚠️ First Click on /start, Then try again")
        return

    if m.from_user.id not in Config.AUTH_USERS:
        for_url = 1969772008
        if (await db.get_urlfunctions(id=for_url)) is False:
            await m.reply(
                "⚠️ URL Functions Currently Disabled ",
                reply_to_message_id=m.id,
            )
            return

    if m.from_user.id not in Config.AUTH_USERS:
        if len(COUNT) > Config.NUMBER:
            await m.reply(
                f"**⚠️ Already {Config.NUMBERS}/{Config.NUMBERS} Process Running**\n\n👉 Bot is Overloaded. So, Try after a few minutes.\n\nIntrested users can Upgrade to Paid bot, To avoid Waiting Time and Process limits.",
                reply_to_message_id=m.id,
            )
            return
    
    reply_msg = m.reply_to_message
    user_id = m.from_user.id
    msg = None

    valid_positions = []
    invalid_positions = []
    manual_shots = 10
    if reply_msg.video:
        try:
            files_video = m.reply_to_message
            medias = files_video.video
            duration = medias.duration
        except Exception as e:
            await m.reply(
                f"**⚠️ Error : **{e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if duration < 6:
            await m.reply(
                f"⚠️ **Error** : Duration is less than 6 Sec\n\n👉 __For Screenshot Generation, Video length should be minimum 6 sec__",
                reply_to_message_id=reply_msg.id,
            )                  
            return

        PROCESS_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            manual_shots = await asyncio.wait_for(
                c.ask(
                    chat_id=m.chat.id,
                    text=f"⏰ Total Duration - {datetime.timedelta(seconds=duration)} ({duration}s)\n\nNow send your list of seconds separated by `,`(comma).\nEx: `5,10,15,20,40`.\nThis will generate screenshots at 5, 10, 15, 20, and 40 seconds.\n\n**None :** The list can have a maximum of 10 valid positions",
                    reply_markup=PROCESS_CANCEL,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await manual_shots.delete()
                await manual_shots.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.message.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await m.reply(
                f"⚠️ Error : Process Time Out",
                reply_to_message_id=reply_msg.id,
            )
            return

        if manual_shots.text == "Cancel":
            await m.reply(
                f"Process Cancelled ✅",
                reply_to_message_id=reply_msg.id,
            )
            return
        else:
            manual_shots = manual_shots.text

        try:
            raw_user_input = [int(i.strip()) for i in manual_shots.split(",")]
        except Exception as e:
            await m.reply(
                f"⚠️ **Error** : {e}\n\nPlease follow this format 👇\n\nDuration List Separate by Comma (,) \nFor Example 👉 `5,10,15,20,40`",
                reply_to_message_id=reply_msg.id,
            )
            return

        for pos in raw_user_input:
            if 0 > pos > duration:
                invalid_positions.append(str(pos))
            else:
                valid_positions.append(pos)
    
        if not valid_positions:
            await m.reply(
                f"⚠️ **Error** Invalid positions are {valid_positions}",
                reply_to_message_id=reply_msg.id,
            )
            return

        if len(valid_positions) > 10:
            await m.message.reply(
                f"⚠️ **Error** : Send below than 10\n\n👉 You sent for {len(valid_positions)} screenshots",
                reply_to_message_id=reply_msg.id,
            )
            return

    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
        os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

    if reply_msg.media:
        texts = CH.processing_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        texts = CH.downloading_txt
        bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
        if bool:
            return

        await CH.start_counting(m)

        bool, real_video = await CH.file_download(c, m, msg, input)
        if bool:
            return

        texts = f"Media Downloaded Successfully ✅"
        bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
        if bool:
            return

    else:
        input = reply_msg.text
        texts = CH.url_recieved_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        await CH.start_counting(m)
    # ----------------- STARTING ------------------#
    bool, duration = await CH.find_duration(m, msg, input)
    if bool:
        return

    if duration < 6:
        await clear_server(user_id, input)
        await msg_edit(
            msg,
            "⚠️ **Error** : Duration is less than 6 Sec\n\n👉 __For Screenshot Generation, Video length should be minimum 6 sec__",
        )
        return
    # ---------------- Script ---------------------#
    if reply_msg.video:
        pass
    else:
        PROCESS_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            manual_shots = await asyncio.wait_for(
                c.ask(
                    chat_id=m.chat.id,
                    text=f"⏰ Total Duration - {datetime.timedelta(seconds=duration)} ({duration}s)\n\nNow send your list of seconds separated by `,`(comma).\nEx: `5,10,15,20,40`.\nThis will generate screenshots at 5, 10, 15, 20, and 40 seconds.\n\n**None :** The list can have a maximum of 10 valid positions",
                    reply_markup=PROCESS_CANCEL,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await manual_shots.delete()
                await manual_shots.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await clear_server(user_id, input)
            await msg_edit(msg, f"⚠️ Process Time Out")
            return

        if manual_shots.text == "Cancel":
            await clear_server(user_id, input)
            await msg_edit(msg, f"Process Cancelled  ✅")
            return
        else:
            manual_shots = manual_shots.text

        try:
            raw_user_input = [int(i.strip()) for i in manual_shots.split(",")]
        except Exception as e:
            await clear_server(user_id, input)
            print(e)
            await msg_edit(
                msg,
                f"⚠️ **Error** : {e}\n\nPlease follow this format 👇\n\nDuration List Separate by Comma (,) \nFor Example 👉 `5,10,15,20,40`",
            )
            return

        for pos in raw_user_input:
            if 0 > pos > duration:
                invalid_positions.append(str(pos))
            else:
                valid_positions.append(pos)
    
        if not valid_positions:
            await clear_server(user_id, input)
            await msg_edit(msg, f"⚠️ **Error** Invalid positions are {valid_positions}")
            return

        if len(valid_positions) > 10:
            await clear_server(user_id, input)
            await msg_edit(
                msg,
                f"⚠️ **Error** : Send below than 10\n\n👉 You sent for {len(valid_positions)} screenshots",
            )
            return

    if len(invalid_positions) >= 1:
        INVALID_POSITION = "Found {invalid_positions_count} invalid positions ({invalid_positions}).\n\nGenerating screenshots after ignoring these!."
        txt = INVALID_POSITION.format(
            invalid_positions_count=len(invalid_positions),
            invalid_positions=", ".join(invalid_positions),
        )
        await update.message.reply(txt, reply_to_message_id=reply_msg.id)
        #await clear_server(user_id, input)
        #return

    else:
        try:
            msg = await msg.edit(f"**Generating Screenshots....**")
        except:
            await delete_msg(msg)
            try:
                msg = await m.reply(
                    "**Generating Screenshots....**",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                await clear_server(user_id, input)
                logger.info(
                    f" ⚠️⚠️ can't send bco message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
                return

    screenshots = []

    ffmpeg_cmd = [
        "ffmpeg",
        "-ss",
        "",  # To be replaced in loop
        "-i",
        input,
        "-vf",
        "scale=1280:-1",
        "-y",
        "-vframes",
        "1",
        "",  # To be replaced in loop
    ]

    logger.info(
        "Generating screenshots at positions %s from location: %s for %s",
        valid_positions,
        input,
        m.chat.id,
    )

    screenshot_dir = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}"
    if not os.path.isdir(screenshot_dir):
        os.makedirs(screenshot_dir)

    for i, sec in enumerate(valid_positions):
        thumbnail_file = os.path.join(screenshot_dir, f"{i+1}.png")
        ffmpeg_cmd[2] = str(sec)
        ffmpeg_cmd[-1] = thumbnail_file
        logger.debug(ffmpeg_cmd)
        output = await Ranjan.run_subprocess(ffmpeg_cmd)
        logger.debug(
            "FFmpeg output\n %s \n %s",
            output[0].decode(),
            output[1].decode(),
        )

        try:
            msg = await msg.edit(
                "`{current}` of `{total}` Screenshots Generated ✅".format(
                    current=i + 1, total=len(valid_positions)
                )
            )
        except FloodWait as f:
            asyncio.sleep(f.x)
            msg = await msg.edit(
                "`{current}` of `{total}` Screenshots Generated ✅".format(
                    current=i + 1, total=len(valid_positions)
                )
            )

        if os.path.exists(thumbnail_file):
            screenshots.append(
                InputMediaPhoto(
                    thumbnail_file,
                    caption="Screenshot at {time}".format(
                        time=datetime.timedelta(seconds=sec)
                    ),
                )
            )
            continue

    if not screenshots:
        await clear_server(user_id, input, screenshot_dir, thumbnail_file)
        await msg_edit(msg, f"⚠️ **Error** in Generating Screenshots")
        return

    try:
        msg = await msg.edit(
            "{count} Screenshots\n\n**Uploading....**".format(
                count=len(valid_positions), total_count=len(screenshots)
            )
        )
    except:
        await delete_msg(msg)
        try:
            msg = await m.reply(
                "{count} Screenshots\n\n**Uploading....**".format(
                    count=len(valid_positions), total_count=len(screenshots)
                ),
                reply_to_message_id=reply_msg.id,
            )
        except:
            await clear_server(user_id, input, thumbnail_file, screenshot_dir)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
            return

    try:
        try:
            await m.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
        except:
            pass
        await c.send_media_group(
            chat_id=m.chat.id,
            media=screenshots,
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f" Manual Screenshots Generated ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
        )
    except Exception as e:
        await clear_server(user_id, input, thumbnail_file, screenshot_dir)
        print(e)
        await msg_edit(msg, f"**Error** : {e}")
        return

    await delete_msg(msg)

    await clear_server(user_id, input, thumbnail_file, screenshot_dir)
