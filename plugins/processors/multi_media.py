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

from config import Config
from database.database import Database

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
from plugins.audio_helper import Ranjan, take_screen_shot 
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

db = Database()

logger = logging.getLogger(__name__)

# ------------- Progress -----------------#
FFMPEG_BOX = {}
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("ffmprogres"))
)
async def ffmpeg_progress(c, m):
    updated_data = m.data.split("/")
    chat_id, message_id = updated_data[1], updated_data[2]
    p_message = "Work in Progress....\n\n{progressbar} {percentage}%"
    try:
        await m.answer(
            text=p_message.format(
                **FFMPEG_BOX[f"{chat_id}_{message_id}"]
            ),
            show_alert=True,
        )
    except Exception as e:
        print(f"⚠️ Ffmpeg Processing {e}")
        try:
            await c.answer_callback_query(
                callback_query_id=m.id,
                text=f"Processing....",
                show_alert=True,
                cache_time=0,
            )
        except:
            pass

def is_cancelled(m, chat_id, message_id):
    cancelled = False
    if CANCEL_PROCESS[chat_id] and message_id in CANCEL_PROCESS[chat_id]:
        cancelled = True
    return cancelled

class Chitranjan:
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
        reply_msg = m.message.reply_to_message
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

    # Audio duration limit 
    @staticmethod
    async def audio_dur_limit(c, m, msg, duration, input, limits):
        bool = False
        if duration > limits:
            await clear_server(m.from_user.id, input)
            await msg_edit(msg, f"⚠️ Send Audio/Video which duration is less than 03:00:00")
            bool = True

        return bool

    # User Waiting Time
    @staticmethod
    async def audio_dur_limito(bot, update, limits):
        reply_msg = update.message.reply_to_message
        bool = False
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
                bool = True

            if duratio > limits:
                ab = await bot.send_message(
                    chat_id=update.message.chat.id,
                    text=f"⚠️ Send Audio/Video which duration is less than 03:00:00",
                    reply_to_message_id=reply_msg.id,
                )
                bool = True 

        return bool

    # User Waiting Time
    @staticmethod
    async def waiting_time(c, m):
        bool = False

        return bool

    # User Process limit
    @staticmethod
    async def user_process_limit(bot, update):
        update.message.reply_to_message
        bool = False
        """
        if update.from_user.id in COUNT:
            bool = True
            text="Already Your 1 Request Processing",
            await Chitranjan.simple_message_send(bot, update, reply_msg, texts)
        """
        return bool

    @staticmethod
    async def improvements(bot, update, files, ft):
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await files.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n{ft}"
                )
            except FloodWait:
                await asyncio.sleep(5)
            except Exception as e:
                logger.info(e)
                
    @staticmethod
    def thread_looping(bot, update, files, ft):
        try:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(Chitranjan.improvement_purpose(bot, update, files, ft))
        except Exception as e:
            logger.info(f"⚠️ L Threading Looping Error: {e}")
            
    @staticmethod
    async def improvementszt(bot, update, files, ft):
        try:
            erggs = (bot, update, files, ft)
            test_thread = threading.Thread(target=Chitranjan.thread_looping, args=erggs, daemon=True) 
            test_thread.start()
        except Exception as e:
            logger.info(f"⚠️ L Threading Error: {e}")
            await clear_server(update.from_user.id)

    # One Process limit
    @staticmethod
    async def one_process_limit(bot, update):
        reply_msg = update.message.reply_to_message
        bool = False
        download_paths = f"{Config.DOWNLOAD_PATH}/{update.from_user.id}"
        if os.path.isdir(download_paths):
            bool = True
            texts = "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__"
            await Chitranjan.simple_message_send(bot, update, reply_msg, texts)

        return bool

    # Count limit
    @staticmethod
    async def total_count_limit(bot, update):
        reply_msg = update.message.reply_to_message
        bool = False
        if len(COUNT) > Config.NUMBER:
            bool = True
            texts = f"**⚠️ Already {Config.NUMBERS} Process Running**\n\n👉 Try again after a few minutes"
            await Chitranjan.simple_message_send(bot, update, reply_msg, texts)

        return bool

    # Edit Messages
    @staticmethod
    async def edit_msg(msg_id, texts):
        id = None
        try:
            id = await msg_id.edit(texts)
        except:
            pass
        return id

    # Delete Messages
    @staticmethod
    async def delete_message(one, two=None, three=None, four=None, five=None):
        try:
            await one.delete()
        except:
            pass
        try:
            await two.delete()
        except:
            pass
        try:
            await three.delete()
        except:
            pass
        try:
            await four.delete()
        except:
            pass
        try:
            await five.delete()
        except:
            pass

    # Find File Name without Ext
    @staticmethod
    async def get_file_size(update, cd, file_path, file):
        bool = True
        output_size = 0
        try:
            output_size = os.path.getsize(file)
            bool = False
        except Exception as e:
            bool = True
            await clear_server(update.from_user.id, file_path, file)
            await msg_edit(cd, f"⚠️ OS Error occured: {e}")
            logger.info(
                f"⚠️ Error occured: {e}. User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )

        return bool, output_size

    # Find File Name without Ext
    @staticmethod
    async def WE_file_name(files):
        description_ = "Default_Name"
        try:
            media = files.video or files.document or files.audio
            description_ = media.file_name
            description_ = os.path.splitext(description_)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"

        return description_

    # Find File Name From URL Without Ext
    @staticmethod
    async def url_WE_name(urls):
        description_ = "Default_Name"
        try:
            #  file_name = urls.split("/")[-1]
            file_name = os.path.basename(urls)
            description_ = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"

        return description_

    # Find Durations
    @staticmethod
    async def find_duration(m, bc, file_path):
        reply_msg = m.message.reply_to_message
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

    # Ask New File Name
    @staticmethod
    async def first_ask_name(bot, update, texts):
        reply_msg = update.message.reply_to_message
        cfile_name = "Default_Name"
        BUTTON_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        bool = True
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"{texts}",
                reply_markup=BUTTON_CANCEL,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            )
            try:
                await ask_.delete()
                await ask_.request.delete()
            except:
                pass
            cfile_name = ask_.text
            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[:60]  # File name reduced
            bool = False
            if cfile_name == "Cancel":
                try:
                    await update.message.reply(
                        "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                    )
                except:
                    pass
                logger.info(
                    f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
                await clear_server(update.from_user.id)
                bool = True

            LONG_FILE_NAME = "⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"
            if len(cfile_name) > 60:
                try:
                    await update.message.reply(
                        LONG_FILE_NAME.format(alimit="60", num=len(cfile_name))
                    )
                except:
                    pass
                await clear_server(update.from_user.id)
                bool = True
            return bool, cfile_name
    '''
    # Command line Executor
    @staticmethod
    async def command_execute(commands, output_directory):
        process = await asyncio.create_subprocess_exec(
            *commands,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if os.path.lexists(output_directory):
            return output_directory
        else:
            return None
    '''

    # Command line Executor
    @staticmethod
    async def command_execute(c, m, msg, commands, output_directory, total_time, texts):
        bool = True
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Progress ⚡",
                        callback_data=f"ffmprogres/{m.message.chat.id}/{msg.id}"                                                                  
                    ),
                    InlineKeyboardButton(
                        "Cancel ❌",
                        callback_data=(
                            f"progcancel/{m.message.chat.id}/{msg.id}/{m.from_user.id}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        try:
            msg = await msg.edit(text=f"{texts}", reply_markup=reply_markup)
        except:
            pass

        current_time = time.time()
        status = f"progress-{current_time}.txt"
        progress = status
        with open(progress, "w") as f:
            pass
        commands.append("-hide_banner")
        commands.append("-loglevel")
        commands.append("quiet")
        commands.append("-progress")
        commands.append(progress)

        process = await asyncio.create_subprocess_exec(
            *commands,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )       
        while process.returncode != 0:
            await asyncio.sleep(1)
            with open(status, "r+") as file:
                text = file.read()
                frame = re.findall("frame=(\d+)", text)
                time_in_us = re.findall("out_time_ms=(\d+)", text)
                progress = re.findall("progress=(\w+)", text)
                speed = re.findall("speed=(\d+\.?\d*)", text)
                if len(frame):
                    frame = int(frame[-1])
                else:
                    frame = 1
                if len(speed):
                    speed = speed[-1]
                else:
                    speed = 1
                if len(time_in_us):
                    time_in_us = time_in_us[-1]
                else:
                    time_in_us = 1

                if len(progress):
                    # ['continue', 'continue', 'end']
                    if progress[-1] == "end":
                        bool = False
                        percentage = 0
                        break

                else:
                    bool = True
                    try:
                        await msg.edit(f"**This Process Failed  ❌**\n\nSomething Went Wrong!!!") 
                        logger.info(f"This Process Failed ❌ For {str(m.from_user.id)} @{m.from_user.username}")                                                
                    except:
                        pass
                    percentage = 0
                    break

                if is_cancelled(m, m.message.chat.id, msg.id):
                    bool = True
                    percentage = 0
                    logger.info(f"Ffmpeg Process Cancelled ❌❌ By {str(m.from_user.id)} @{m.from_user.username}")
                    try:
                        await msg.edit(f"**Process Cancelled ✅**",)                                                   
                    except:
                        pass                   
                    if process.pid:
                        try:
                            os.kill(process.pid, 9)
                        except Exception as e:
                            logger.info(f"⚠️ Process pid error: {e}")

                    break

                elapsed_time = int(time_in_us) / 1000000
                difference = math.floor((total_time - elapsed_time) / float(speed))
                percentag = math.floor(elapsed_time * 100 / total_time)
                percentage = (round(percentag, 2))
                progressbar = "[{0}{1}]".format(
                    "".join(["■" for i in range(math.floor(percentage / 10))]),
                    "".join(["□" for i in range(10 - math.floor(percentage / 10))]),
                )
                FFMPEG_BOX[f"{m.message.chat.id}_{msg.id}"] = {
                    "progressbar": progressbar,
                    "percentage": percentage,
                }
        stdout, stderr = await process.communicate()
        if os.path.lexists(output_directory):
            return bool, output_directory, msg
        else:
            return bool, None, msg

    # Start Counting Users
    @staticmethod
    async def start_counting(update):
        if update.from_user.id not in COUNT:
            try:
                COUNT.append(update.from_user.id)
            except Exception as e:
                logger.info(
                    f"⚠️ Adding in Count Error: {e}  {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

    # Simple Sticker Send
    @staticmethod
    async def simple_sticker_send(c, m):
        sticker = None
        
        try:
            sticker = await m.message.reply_sticker(
                "CAACAgUAAxkBAAESX81jQ4atc_bS1YcfJ3IfCuTfSfoKkwACegYAAgu2GVYTpn876J0baCoE",
            )
        except Exception as e:
            sticker = None
            logger.info(
                f" ⚠️⚠️ {e} can't send sticker message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
        
        return sticker

    # Simple Messages Send
    @staticmethod
    async def simple_message_send(bot, update, texts):
        reply_msg = update.message.reply_to_message
        try:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"{texts}",
                reply_to_message_id=reply_msg.id,
            )
        except Exception:
            ab = None
            await clear_server(update.from_user.id)
            logger.info(
                f" ⚠️⚠️ can't send ab message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        return ab

    # Advanced Messages Send
    @staticmethod
    async def message_send(bot, update, file_path, texts):
        bool = True
        reply_msg = update.message.reply_to_message
        try:
            ab = await bot.send_message(
                chat_id=update.message.chat.id,
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

    # Advanced Edit CallBack Message
    @staticmethod
    async def cb_message_edit(bot, update, ab, file_path, texts):
        bool = True
        reply_msg = update.message.reply_to_message
        try:
            bc = await ab.edit(f"{texts}")
            bool = False
        except Exception:
            await delete_msg(ab)
            try:
                bc = await update.message.reply(
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
        reply_msg = update.message.reply_to_message
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
                CANCEL_PROCESS[update.message.chat.id]
                and ab.id in CANCEL_PROCESS[update.message.chat.id]
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

    # File Downloader
    @staticmethod
    async def multi_download(bot, update, ab, download_msg, file_path):
        reply_msg = update.message.reply_to_message
        file_ids = FileId.decode(media_file_id(reply_msg))
        bool = True
        real_media = None
        try:
            times = time.time()
            progress_bar = Progress(update.from_user.id, bot, ab)            
            real_media = await bot.download_media(
                message=download_msg,
                file_name=file_path,
                progress=progress_bar.ProgressBar,
                progress_args=(f"Downloading.... from DC{file_ids.dc_id}", times),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ab.id in CANCEL_PROCESS[update.message.chat.id]
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

    # Video Uploader
    @staticmethod
    async def video_upload(
        c, m, ef, file_path, output_file, duration, captions, ft
    ):
        bot = c
        update = m
        width = 0
        height = 0
        reply_msg = m.message.reply_to_message
        thumb = None
        thumbnail = None
        if (await db.get_othumb(m.from_user.id)) is False:
            thumb = None
        else:
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumbnail = await db.get_thumbnail(m.from_user.id)
            except Exception as e:
                thumbnail = None
                logger.info(
                    f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
                )
            if thumbnail is not None:
                try:
                    thumb = await c.download_media(message=thumbnail, file_name=thumb)
                except Exception as e:
                    logger.info(
                        f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                    )
                    await db.set_thumbnail(m.from_user.id, thumbnail=None)

            else:
                try:
                    thumb = await take_screen_shot(
                        output_file,
                        os.path.dirname(thumb),
                        random.randint(0, duration - 1),
                    )
                except Exception as e:
                    await clear_server(
                        m.from_user.id, file_path, output_file, thumb
                    )
                    logger.info(
                        f" ⚠️ Thumbnail Ss Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                    )
                    await msg_edit(ef, f"⚠️ **Thumbnail Ss Error** : {e}")
                    return 

            t_height = 0
            try:
                metadata = extractMetadata(createParser(thumb))
                if metadata.has("height"):
                    t_height = metadata.get("height")
                else:
                    t_height = 0
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, t_height))
                img.save(thumb, "JPEG")
            except Exception as e:
                logger.info(f"⚠️ Thumbnail H Error: {e}")
                if thumbnail is not None:
                    await db.set_thumbnail(m.from_user.id, thumbnail=None)
                thumb = f"{Config.DOWNLOAD_PATH}/dkbotz{m.from_user.id}.jpg"
                try:
                    thumb = await take_screen_shot(
                        output_file,
                        os.path.dirname(thumb),
                        random.randint(0, duration - 1),
                    )
                except Exception as e:
                    logger.info(
                        f" ⚠️ Thumbnail Ss2 Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                    )
                    thumb = None

        try:
            width, height = await Ranjan.get_dimentions(output_file)
        except Exception as e:
            await clear_server(
                m.from_user.id, file_path, output_file, thumb
            )
            logger.info(
                f" ⚠️ V HW Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
            )
            await msg_edit(ef, f"⚠️ **Video Hight Width Error** : {e}")
            return 

        if (await db.get_asvideos(m.from_user.id)) is True:
            try:
                progress_bar = Progress(m.from_user.id, m, ef)
                times = time.time()
                try:
                    await m.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_VIDEO
                    )
                except:
                    pass
                diksha = await c.send_video(
                    chat_id=m.message.chat.id,
                    video=output_file,
                    caption=captions,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.ProgressBar,
                    progress_args=("Uploading....", times),
                )

                if (
                    CANCEL_PROCESS[m.message.chat.id]
                    and ef.id in CANCEL_PROCESS[m.message.chat.id]
                ):
                    await clear_server(
                        m.from_user.id, file_path, output_file, thumb
                    )
                    return

                await delete_msg(ef)
                await Chitranjan.improvements(c, m, diksha, ft)

                logger.info(
                    f" {ft} By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ UP Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(ef, f"⚠️ **UP Error** : {e}")

        else:
            try:
                progress_bar = Progress(m.from_user.id, c, ef)
                times = time.time()
                try:
                    await m.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_DOCUMENT
                    )
                except:
                    pass
                diksha = await c.send_document(
                    chat_id=m.message.chat.id,
                    document=output_file,
                    caption=captions,
                    thumb=thumb,
                    force_document=True,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.ProgressBar,
                    progress_args=("Uploading....", times),
                )

                if (
                    CANCEL_PROCESS[m.message.chat.id]
                    and ef.id in CANCEL_PROCESS[m.message.chat.id]
                ):
                    await clear_server(
                        m.from_user.id, file_path, output_file, thumb
                    )
                    return

                await delete_msg(ef)
                await Chitranjan.improvements(c, m, diksha, ft)

                logger.info(
                    f"{ft} By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ UP Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(ef, f"⚠️ **UP Error** : {e}")

        await clear_server(m.from_user.id, file_path, output_file, thumb)
        return 

    # Audio Uploader
    @staticmethod
    async def audio_upload(
        c, m, ef, file_path, output_file, duration, captions, ft
    ):
        reply_msg = m.message.reply_to_message
        thumb = None
        thumbnail = None

        if (await db.get_othumb(m.from_user.id)) is False:
            thumb = None
        else:
            thumb = f"{Config.DOWNLOAD_PATH}/thenicebots{m.from_user.id}.jpg"
            try:
                thumbnail = await db.get_thumbnail(m.from_user.id)
            except Exception as e:
                thumbnail = None
                logger.info(
                    f"⚠️ DB Thumbnail Error: {e} ✅ By {str(m.from_user.id)} @{m.from_user.username}"
                )
            if thumbnail is not None:
                try:
                    thumb = await c.download_media(message=thumbnail, file_name=thumb)
                    t_height = 0
                    try:
                        metadata = extractMetadata(createParser(thumb))
                        if metadata.has("height"):
                            t_height = metadata.get("height")
                        else:
                            t_height = 0
                        Image.open(thumb).convert("RGB").save(thumb)
                        img = Image.open(thumb)
                        img.resize((320, t_height))
                        img.save(thumb, "JPEG")
                    except Exception as e:
                        logger.info(f"⚠️ Thumbnail H Error: {e}")
                        thumb = None
                        if thumbnail is not None:
                            await db.set_thumbnail(m.from_user.id, thumbnail=None)
                except Exception as e:
                    logger.info(
                        f" ⚠️ Thumbnail DL Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                    )
                    await db.set_thumbnail(m.from_user.id, thumbnail=None)
                    thumb = None

            else:
                thumb = None

        if (await db.get_upload_as(m.from_user.id)) is True:
            try:
                progress_bar = Progress(m.from_user.id, c, ef)
                times = time.time()
                try:
                    await m.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_AUDIO
                    )
                except:
                    pass
                diksha = await c.send_audio(
                    chat_id=m.message.chat.id,
                    audio=output_file,
                    caption=captions,
                    duration=duration,
                    thumb=thumb,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.ProgressBar,
                    progress_args=("Uploading....", times),
                )

                if (
                    CANCEL_PROCESS[m.message.chat.id]
                    and ef.id in CANCEL_PROCESS[m.message.chat.id]
                ):
                    await clear_server(
                        m.from_user.id, file_path, output_file, thumb
                    )
                    return

                await delete_msg(ef)
                await Chitranjan.improvements(c, m, diksha, ft)

                logger.info(
                    f" {ft} By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ UP Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(ef, f"⚠️ **UP Error** : {e}")

        else:
            try:
                progress_bar = Progress(m.from_user.id, c, ef)
                times = time.time()
                try:
                    await m.message.reply_chat_action(
                        enums.ChatAction.UPLOAD_DOCUMENT
                    )
                except:
                    pass
                diksha = await c.send_document(
                    chat_id=m.message.chat.id,
                    document=output_file,
                    caption=captions,
                    thumb=thumb,
                    force_document=True,
                    reply_to_message_id=reply_msg.id,
                    progress=progress_bar.ProgressBar,
                    progress_args=("Uploading....", times),
                )

                if (
                    CANCEL_PROCESS[m.message.chat.id]
                    and ef.id in CANCEL_PROCESS[m.message.chat.id]
                ):
                    await clear_server(
                        m.from_user.id, file_path, output_file, thumb
                    )
                    return

                await delete_msg(ef)
                await Chitranjan.improvements(c, m, diksha, ft)

                logger.info(
                    f"{ft} By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
            except Exception as e:
                logger.info(
                    f" ⚠️ UP Error: {e} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await msg_edit(ef, f"⚠️ **UP Error** : {e}")

        await clear_server(m.from_user.id, file_path, output_file, thumb)
        return 

