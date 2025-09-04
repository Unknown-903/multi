import asyncio
import logging
import os
import random
import time

from PIL import Image
from config import Config
from pyrogram.file_id import FileId
from pyrogram import Client, ContinuePropagation, enums, filters
from pyrogram.emoji import *
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions import MessageNotModified
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from database.database import Database
from plugins.progress import Progress
from plugins.audio import (
    CANCEL_PROCESS,
    COUNT,
    clear_server,
    clear_server_two,
    media_file_id,
    delete_msg,
    dmsg_edit,
    msg_edit,
    humanbytes,
)
from plugins.audio_helper import Ranjan, take_screen_shot
from plugins.others.playlist_uploader import playlist_uploader
from plugins.processors import media_uploader, Chitranjan as CH
db = Database()

QueueDB = {}
ReplyDB = {}

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

class Merge:
    @staticmethod
    async def Dprogress_msg(c, m, msg, texts):
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
                logger.info(
                    f" ⚠️⚠️ {texts} can't send message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
        return bool, bc

async def single_process(video_file, output_directory):
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-async",
        "1",
        "-strict",
        "-2",
        "-codec",
        "copy",
        output_directory,
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(output_directory):
        return output_directory
    else:
        return None


def get_size(Folderpath):
    total_size = 0
    for ele in os.scandir(Folderpath):
        total_size += os.path.getsize(ele)
    return total_size

async def MergeVideo(
    input_file: str, user_id: int, message: Message, new_file_name, format_: str
):
    output_vid = (
        f"{Config.DOWNLOAD_LOCATION}/{new_file_name}.{format_.lower()}" # {str(user_id)}/
    )
    file_generator_command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        input_file,
        "-async",
        "1",
        "-strict",
        "-2",
        "-c",
        "copy",
        output_vid,
    ]
    process = None

    process = await asyncio.create_subprocess_exec(
        *file_generator_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    #logger.error(f"Error: {e_response}")
    if os.path.lexists(output_vid):
        return output_vid
    else:
        return None


@Client.on_callback_query(filters.regex("^vmerge"))  # & filters.user(Config.AUTH_USERS)
async def vmerge_(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    msg = None
    thumb = None

    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
        os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

    media = reply_msg.video or reply_msg.document

    if QueueDB.get(m.from_user.id, None) is None:
        QueueDB.update({m.from_user.id: []})
    if (len(QueueDB.get(m.from_user.id)) >= 0) and (
        len(QueueDB.get(m.from_user.id)) <= Config.MAX_VIDEOS
    ):
        QueueDB.get(m.from_user.id).append(reply_msg.id)

    CANCEL_BUTTONSP = ReplyKeyboardMarkup(
        [["Cancel"]], resize_keyboard=True, one_time_keyboard=True
    )
    next_video = await c.ask(
        m.from_user.id,
        "Now Send The Next Video",
        reply_markup=CANCEL_BUTTONSP,
        reply_to_message_id=reply_msg.id,
    )
    if next_video.text:
        if next_video.text == "Cancel":
            await clear_server(user_id, input)
            try:
                QueueDB.update({m.from_user.id: []})
            except:
                pass
            await delete_msg(next_video, next_video.request)
            await m.message.reply_text(
                "Process Cancelled ✅",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
            return

        else:
            await delete_msg(next_video, next_video.request)
            next_video = await c.ask(
                m.from_user.id,
                "⚠️ Don't send Test words\n\n👉 Now Send The Next Video To Merge",
                reply_markup=CANCEL_BUTTONSP,
                reply_to_message_id=reply_msg.id,
            )
        # ---------------------------------------------#
    while True:
        MERGE_BUTTONO = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Merge Videos", callback_data="vnowmerge")],
                [InlineKeyboardButton("Cancel", callback_data="vmcancel")],
            ]
        )

        MERGER_BUTTONS = ReplyKeyboardMarkup(
            [["Merge Videos"], ["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )

        if next_video.text:
            if next_video.text == "Cancel":
                await clear_server(user_id, input)
                QueueDB.update({m.from_user.id: []})
                if ReplyDB.get(m.from_user.id, None) is not None:
                    await c.delete_messages(
                        chat_id=m.message.chat.id,
                        message_ids=ReplyDB.get(m.from_user.id),
                    )
                try:
                    await msg.edit(
                        "Process Cancelled ✅", reply_markup=ReplyKeyboardRemove()
                    )
                except:
                    await m.message.reply_text(
                        "Process Cancelled ✅",
                        reply_markup=ReplyKeyboardRemove(),
                        reply_to_message_id=reply_msg.id,
                    )
                break
            elif next_video.text == "Merge Videos":
                if ReplyDB.get(m.from_user.id, None) is not None:
                    await c.delete_messages(
                        chat_id=m.message.chat.id,
                        message_ids=ReplyDB.get(m.from_user.id),
                    )
                try:
                    await msg.edit(
                        "If you want Custom file name in Output Video, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Again Click on **Merge Videos** 👇",
                        reply_markup=MERGE_BUTTONO,
                    )
                except:
                    await m.message.reply_text(
                        "If you want Custom file name in Output Video, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Again Click on **Merge Videos** 👇",
                        reply_markup=MERGE_BUTTONO,
                        reply_to_message_id=reply_msg.id,
                    )

                cancd = await m.message.reply_text(
                    ".", reply_markup=ReplyKeyboardRemove()
                )
                await delete_msg(cancd)
                break

            else:
                next_video = await c.ask(
                    m.from_user.id,
                    "⚠️ You are Doing Wrong.\n\n👉 Send me the next video to merge, Or\n\n👉 Click on the Below Button 👇",
                    reply_markup=MERGER_BUTTONS,
                    reply_to_message_id=next_video.id,
                )
                continue

        if next_video.video or next_video.document:
            filetype = next_video.document or next_video.video
            try:
                recogniser_ = filetype.mime_type
            except Exception as e:
                next_video = await c.ask(
                    m.from_user.id,
                    f"⚠️ **Error** : {e}\n\n👉 Getting Error in this video. So, Send me Another Video to Merge",
                    reply_to_message_id=next_video.id,
                )
                continue
            if recogniser_ is None:
                next_video = await c.ask(
                    m.from_user.id,
                    "⚠️ File type not recognised\n\n👉 So, Send me Another Video to Merge",
                    reply_to_message_id=next_video.id,
                )
                continue

            if not filetype.mime_type.startswith("video/"):
                next_video = await c.ask(
                    m.from_user.id,
                    "⚠️ Send a Valid video file to Merge",
                    reply_to_message_id=next_video.id,
                )
                continue

            msg = await m.message.reply_text(
                "**Please wait....**", reply_to_message_id=next_video.id
            )

            if len(QueueDB.get(m.from_user.id)) > Config.MAX_VIDEOS:
                if ReplyDB.get(m.from_user.id, None) is not None:
                    await c.delete_messages(
                        chat_id=m.message.chat.id,
                        message_ids=ReplyDB.get(m.from_user.id),
                    )
                try:
                    await msg.edit(
                        text="⚠️ Reached Video Limit !!!\n👉 Max **{} Videos** Allowed to Merge Together".format(
                            len(QueueDB.get(m.from_user.id))
                        )
                    )
                except MessageNotModified:
                    pass
                except Exception:
                    pass
                next_video = await c.ask(
                    m.from_user.id,
                    "If you want Custom file name in Output Video, Then Activate ✏️ **Rename File: Yes** in /settings.\n\nNow Press **Merge Videos** Button or Cancel The Process 👇",
                    reply_markup=MERGE_BUTTONO,
                    reply_to_message_id=next_video.id,
                )
                ReplyDB.update({m.from_user.id: next_video.request.id})
            if QueueDB.get(m.from_user.id, None) is None:
                QueueDB.update({m.from_user.id: []})
            if (len(QueueDB.get(m.from_user.id)) >= 0) and (
                len(QueueDB.get(m.from_user.id)) <= Config.MAX_VIDEOS
            ):
                QueueDB.get(m.from_user.id).append(next_video.id)

                if ReplyDB.get(m.from_user.id, None) is not None:
                    await c.delete_messages(
                        chat_id=m.message.chat.id,
                        message_ids=ReplyDB.get(m.from_user.id),
                    )

                try:
                    await msg.edit(
                        text="Total Videos : **{}**".format(
                            len(QueueDB.get(m.from_user.id))
                        )
                    )
                except MessageNotModified:
                    pass
                except Exception:
                    pass
                next_video = await c.ask(
                    m.from_user.id,
                    f"Now Send Me The Next Video",
                    reply_markup=MERGER_BUTTONS,
                    reply_to_message_id=next_video.id,
                )
                ReplyDB.update({m.from_user.id: next_video.request.id})

        else:
            next_video = await c.ask(
                m.from_user.id,
                "⚠️ Send Me Only Video file\n\n👉 Or Click on **Merge Videos** To Merge",
                reply_markup=MERGER_BUTTONS,
                reply_to_message_id=next_video.id,
            )
            ReplyDB.update({m.from_user.id: next_video.request.id})

@Client.on_callback_query()
async def callback_handlers(c, m):
    await delete_msg(m.message)
    reply_msg = m.message.reply_to_message
    user_id = m.from_user.id
    msg = None
    input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
    BUTTONO_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    if "vnowmerge" in m.data:
        video_list = list()
        VIDEO_FORMAT = ReplyKeyboardMarkup(
            [["mp4", "mkv"],["Cancel"]], resize_keyboard=True, one_time_keyboard=True
        )
        try:
            formats = await asyncio.wait_for(
                c.ask(
                    chat_id=m.message.chat.id,
                    text=f"**mp4** : MP4 Container doesn't supports all audio formats.\n\n**✶ Send me The output video format**",
                    reply_markup=VIDEO_FORMAT,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                Config.PROCESS_TIMEOUT,
            )
            try:
                await formats.delete()
                await formats.request.delete()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                ccc = await m.message.reply(".", reply_markup=ReplyKeyboardRemove())
                await ccc.delete()
            except:
                pass
            await clear_server(user_id, input)
            QueueDB.update({update.from_user.id: []})
            await m.message.reply(
                f"⚠️ Error : Process Time Out",
                reply_to_message_id=reply_msg.id,
            )
            return
 
        if formats.text == "Cancel":
            await clear_server(user_id, input)
            QueueDB.update({update.from_user.id: []})
            await m.message.reply(
                f"Process Cancelled ✅",
                reply_to_message_id=reply_msg.id,
            )
            return
        else:
            formats = f"{formats.text}"

        VIDEO_EXTENSIONS = ["mp4", "mkv"]
        if formats in VIDEO_EXTENSIONS:
            formats = formats.lower()
        else:
            formats = "mkv"

        new_file_name = "Default_Name"
        if (await db.get_auto_rename(m.from_user.id)) is True:
            try:
                ask_ = await asyncio.wait_for(
                    c.ask(
                        chat_id=m.message.chat.id,
                        text=f"**Now Send The Name of Output Video**",
                        reply_markup=BUTTONO_CANCEL,
                        filters=filters.text,
                        reply_to_message_id=reply_msg.id,
                    ),
                    Config.PROCESS_TIMEOUT,
                )
                try:
                    await ask_.delete()
                    await ask_.request.delete()
                except:
                    pass
                cfile_name = ask_.text
            except asyncio.TimeoutError:
                try:
                    ccc = await m.message.reply(".", reply_markup=BUTTONO_CANCEL)
                    await ccc.delete()
                except:
                    pass
                cfile_name = "Default_Name"

            if cfile_name == "Cancel":
                await clear_server(user_id, input)
                QueueDB.update({update.from_user.id: []})
                await m.message.reply(
                    "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                )
                logger.info(
                    f" Process Cancelled  ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
                return

            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[:60] # File name reduced
                         
            IF_LONG_FILE_NAME = """⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"""
            if len(cfile_name) > 60:
                await clear_server(user_id, input)
                QueueDB.update({m.from_user.id: []})
                await m.message.reply(
                    IF_LONG_FILE_NAME.format(alimit="60", num=len(cfile_name)), reply_to_message_id=reply_msg.id
                )
                return

            new_file_name = f"{cfile_name}"

        list_message_ids = QueueDB.get(m.from_user.id, None)
        list_message_ids.sort()
        txt_inputs = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}/input.txt"
        if list_message_ids is None:
            await clear_server(user_id, input)
            QueueDB.update({m.from_user.id: []})
            await m.message.reply(
                "⚠️ File List is Empty. There is not any video in your list", reply_to_message_id=reply_msg.id
            )
            return

        if len(list_message_ids) < 2:
            await clear_server(user_id, input)
            QueueDB.update({m.from_user.id: []})
            await m.message.reply(
                "⚠️ There is Only one video in your list, So can't merge", reply_to_message_id=reply_msg.id
            )
            return

        if not os.path.exists(f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}/"):
            os.makedirs(f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}/")

        try:
            msg = await m.message.reply(
                "**Processing....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await clear_server(user_id, input)
            QueueDB.update({m.from_user.id: []})
            logger.info(e)
            return

        await CH.start_counting(m)
        countings = 0
        for i in await c.get_messages(
            chat_id=m.from_user.id, message_ids=list_message_ids
        ):
            countings += 1
            media = i.video or i.document

            texts = f"**Downloading Video No.{countings} ....**"
            bool, msg = await Merge.Dprogress_msg(c, m, msg, texts)
            if bool:
                QueueDB.get(m.from_user.id).remove(i.id)
                await msg_edit(msg, "⚠️ This video will be Skipped!")
                await asyncio.sleep(3)
                continue

            real_video = None
            inner_file = f"{Config.DOWNLOAD_PATH}/{m.from_user.id}/{i.id}/"
            file_ids = FileId.decode(media_file_id(i))
            try:
                progress_bar = Progress(m.from_user.id, c, msg)
                c_time = time.time()
                real_video = await c.download_media(
                    message=i,
                    file_name=inner_file,
                    progress=progress_bar.ProgressBar,
                    progress_args=(f"Downloading {countings} from DC{file_ids.dc_id}....", c_time),
                )
                if (
                    CANCEL_PROCESS[m.message.chat.id]
                    and msg.id in CANCEL_PROCESS[m.message.chat.id]
                ):
                    await clear_server(user_id, input)
                    QueueDB.update({m.from_user.id: []})
                    return
            except Exception as e:
                QueueDB.get(m.from_user.id).remove(i.id)
                await msg_edit(msg, "⚠️ This video Skipped!!!")
                await asyncio.sleep(3)
                continue
            try:
                durations = await Ranjan.get_duration(real_video)
                file_size_output = os.path.getsize(real_video)
            except Exception as e:
                QueueDB.get(m.from_user.id).remove(i.id)
                try:
                    await m.message.reply(
                        f"⚠️ **Error:** I can't Merge this 👉 Video {countings}\n\nSo, Skipped that Video!!!",
                        reply_to_message_id=reply_msg.id,
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                continue
            
            if isinstance(durations, str):
                QueueDB.get(m.from_user.id).remove(i.message_id)
                try:
                    await m.message.reply(
                        f"⚠️ **Error:** I can't Merge this video 👉 {countings} \n\nSo, Skipped that Video!!!",
                        reply_to_message_id=reply_msg.id,
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                continue

            output_directory = f"/app/DOWNLOADS/{m.from_user.id}/{i.id}/{str(countings)}.{formats}"
            outputs = await single_process(real_video, output_directory)
            if outputs is None:
                await clear_server_two(inner_file, output_directory)
                QueueDB.get(m.from_user.id).remove(i.id)
                try:
                    await m.message.reply(
                        f"⚠️ **Error:** I can't Merge this video 👉 {countings} \n\nSo, Skipped that Video!!!",
                        reply_to_message_id=reply_msg.id,
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                continue
            if os.path.isfile(real_video):
                os.remove(real_video)

            try:
                video_list.append(f"file '{output_directory}'")
            except Exception as e:
                print(e)
                await clear_server(user_id, input)
                QueueDB.update({m.from_user.id: []})
                await msg_edit(msg, f"⚠️ ** Error :** {e}")
                return

        cache_list = list()
        for i in range(len(video_list)):
            if video_list[i] not in cache_list:
                cache_list.append(video_list[i])
        video_list = cache_list

        if (len(video_list) < 2) and (len(video_list) > 0):
            await clear_server(user_id, input)
            QueueDB.update({m.from_user.id: []})
            await msg_edit(
                msg,
                "⚠️ There only One Video in Queue!\nMaybe you sent same video multiple times.",
            )
            return

        try:
            msg = await msg.edit(f"**Merging....**")
        except:
            await delete_msg(msg)
            try:
                msg = await m.message.reply(
                    "**Merging....**", reply_to_message_id=reply_msg.id
                )
            except:
                await clear_server(user_id, input)
                logger.info(
                    f" ⚠️⚠️ can't send cd message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
                QueueDB.update({m.from_user.id: []})
                return

        with open(txt_inputs, "w") as lists:
            lists.write("\n".join(video_list))

        output = None
        output = await MergeVideo(
            input_file=txt_inputs,
            user_id=m.from_user.id,
            message=msg,
            new_file_name=new_file_name,
            format_= formats,
        )

        if output is None:
            await clear_server(user_id, input, output)
            QueueDB.update({m.from_user.id: []})
            await msg_edit(msg, "⚠️ Failed to Merge Video, Something Went Wrong!!!")
            return

        bool, output_size = await CH.get_file_size(m, msg, input, output)
        if bool:
            await clear_server(user_id, input, output)
            QueueDB.update({m.from_user.id: []})
            return

        captions = (
            f"File Name : {new_file_name}.{formats}"
            + "\n\n➕ **{}** Videos Merged  ✅".format(
                len(QueueDB.get(m.from_user.id))
            )
        )
        ft = "Videos Merged ✅"
        premium_upload = CH.U4GB_VMerger
        if output_size > CH.Upload_Size_Limit:  # 1999mb
            await CH.delete_message(msg)
            try:
                await media_uploader(c, m, output, captions, ft, premium_upload)
            except:
                pass
            await clear_server(user_id, input, output)
            QueueDB.update({m.from_user.id: []})
            return

        bool, mduration = await CH.find_duration(m, msg, output)
        if bool:
            await clear_server(user_id, input, output)
            QueueDB.update({m.from_user.id: []})
            return

        texts = CH.uploading_txt
        bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
        if bool:
            await clear_server(user_id, input, output)
            QueueDB.update({m.from_user.id: []})
            return

        await CH.video_upload(c, m, msg, input, output, mduration, captions, ft)
        QueueDB.update({m.from_user.id: []})
        await CH.waiting_time(c, m)


    elif "vmcancel" in m.data:
        await clear_server(user_id, input)
        QueueDB.update({m.from_user.id: []})
        await delete_msg(m.message)
        try:
            await m.message.reply(
                "Process Cancelled ✅", reply_to_message_id=reply_msg.id
            )
        except:
            pass

    else:
        raise ContinuePropagation
