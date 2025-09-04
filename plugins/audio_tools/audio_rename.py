import logging
import os
import asyncio

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from plugins.audio import clear_server, clear_server_two, humanbytes
from config import Config
from plugins.processors import media_uploader, Chitranjan as CH
from database.database import Database
db = Database()

logger = logging.getLogger(__name__)

class Rename:
    @staticmethod
    async def ask_name(c, m, texts):
        reply_msg = m.message.reply_to_message
        cfile_name = "Default_Name"
        extension = "mp3"
        bool = True
        BUTTON_CANCEL = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        if reply_msg.media:
            ask_ = await c.ask(
                chat_id=m.message.chat.id,
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
            if "." in cfile_name:
                try:
                    splited = cfile_name.split(".")
                    extension = splited[-1]
                except:
                    extension = "mp3"
            else:
                extension = "mp3"

            cfile_name = os.path.splitext(cfile_name)[0]  # extension Removed
            cfile_name = cfile_name[:60]  # File name reduced
            bool = False
            if cfile_name == "Cancel":
                try:
                    await m.message.reply(
                        "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
                    )
                except:
                    pass
                logger.info(
                    f" Process Cancelled  ✅ By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
                )
                await clear_server(m.from_user.id)
                bool = True

            LONG_FILE_NAME = "⚠️ **Error**\n\nFile_Name limit allowed by telegram is {alimit} Characters.\n\nThe given file name has {num} Characters.\n\nPlease short your File_Name And Try again"
            if len(cfile_name) > 60:
                try:
                    await m.message.reply(
                        LONG_FILE_NAME.format(alimit="60", num=len(cfile_name))
                    )
                except:
                    pass
                await clear_server(m.from_user.id)
                bool = True

        return bool, cfile_name, extension

@Client.on_callback_query(filters.regex("^renamaud"))
async def audio_renamer(c, m):
    await CH.delete_message(m.message)
    reply_msg = m.message.reply_to_message    
    msg = None

    if reply_msg.media:
        pass
    else:
        return 
    bool = await CH.one_process_limit(c, m)
    if bool:
        return

    bool = await CH.total_count_limit(c, m)
    if bool:
        return

    bool = await CH.user_process_limit(c, m)
    if bool:
        return

    texts = f"**Now Send Name of Output Audio**"
    bool, cfile_name, extension = await Rename.ask_name(c, m, texts)
    if bool:
        return

    new_file_name = "Default_Name"
    if reply_msg.media:
        input = f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}.download.mkv"
        if not os.path.exists(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/"):
            os.makedirs(f"{Config.DOWNLOAD_PATH}/{str(m.from_user.id)}/")

        texts = CH.processing_txt
        bool, msg = await CH.message_send(c, m, input, texts)
        if bool:
            return

        texts = CH.downloading_txt
        bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
        if bool:
            return

        await CH.start_counting(m)

        bool, real_audio = await CH.file_download(c, m, msg, input)
        if bool:
            return

        texts = f"Media Downloaded Successfully ✅"
        bool, msg = await CH.cb_message_edit(c, m, msg, input, texts)
        if bool:
            return

    else:
        return 

    bool, duration = await CH.find_duration(m, msg, input)
    if bool:
        return
    
    new_file_name = f"{cfile_name}.{extension}"

    output = f"{Config.DOWNLOAD_PATH}/{new_file_name}"

    try:
        os.rename(real_audio, output)
    except Exception as e:
        await clear_server(m.from_user.id, input, output)
        print(e)
        await CH.edit_msg(cd, f"⚠️ **R Error** : {e}")
        return

    texts = "**Renaming Audio File....**"
    try:
        msg = await msg.edit(f"{texts}")
    except:
        await CH.delete_message(msg)
        try:
            msg = await m.message.reply(
                f"{texts}", reply_to_message_id=reply_msg.id
            )
        except:
            await clear_server(m.from_user.id, input, output)
            logger.info(
                f" ⚠️⚠️ can't send cd message To {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
            )
            return       

    if output is None:
        await clear_server(m.from_user.id, input, output)
        texts = f"⚠️ **Error** : Something Went Wrong!!!\n\n👉 Resend your file And Try Again"        
        await CH.edit_msg(msg, texts)
        return

    bool, output_size = await CH.get_file_size(m, msg, input, output)
    if bool:
        return

    try:
        file_name = os.path.basename(output)
        captions = (
            "File Name : "
            + f"{file_name}"
            + f"\n\nFile Size : {humanbytes(output_size)}"
        )
    except:
        captions = f"File Name : {file_name}"

    ft = "Audio Renamed ✅ "
    selected_format = "Others"
    if output_size > CH.Upload_Size_Limit:  # 1999mb
        await CH.delete_message(msg)
        try:
            await media_uploader(c, m, output, captions, ft)
        except:
            pass
        await clear_server(m.from_user.id, input, output)
        return

    texts = CH.uploading_txt
    bool, msg = await CH.DUprogress_msg(c, m, msg, input, texts)
    if bool:
        await clear_server_two(output)
        return

    await CH.audio_upload(c, m, msg, input, output, duration, captions, ft)
    await CH.waiting_time(c, m)
