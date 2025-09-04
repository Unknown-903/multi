import datetime
import logging
import os
import time

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ForceReply, ReplyKeyboardMarkup

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

import io

from music_tag import load_file
from PIL import Image


@Client.on_callback_query(filters.regex("^tagmp3"))
async def mp3_tag_(bot, update):
    await delete_msg(update.message)
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
    ef = None
    thumb = None
    stickeraudio = None
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
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mp3"
    )

    CANCEL_SKIP = ReplyKeyboardMarkup(
        [["Cancel", "Skip"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    BUTTON_CANCEL = ReplyKeyboardMarkup(
        [["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if reply_msg.media:
        logger.info(
            f"☘️ Sent file for Changing Audio Tag. User {update.from_user.id} @{update.from_user.username}"
        )
        new_file_name = "Default_Name"
        if (await db.get_auto_rename(update.from_user.id)) is True:
            ask_ = await bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Now Send Name of New Audio Name** with Extension (Ex: .mp3, .acc, etc)",
                reply_markup=ForceReply(True),
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            )
            #   await ask_.delete()
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
                    extension = splitit[-1]
                except:
                    extension = "mp3"
            else:
                extension = "mp3"

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

        title = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Audio Title**",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        # await title.delete()
        await title.request.delete()
        logger.info(
            f"Audio Title is 👉 {title.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if title.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        album = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Name of Album **",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        # await album.delete()
        await album.request.delete()
        logger.info(
            f"Audio album is 👉 {album.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if album.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        genre = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Name of genre **",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        # await genre.delete()
        await genre.request.delete()
        logger.info(
            f"Audio genre is 👉 {genre.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if genre.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        comment = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Audio comment **",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        # await comment.delete()
        await comment.request.delete()
        logger.info(
            f"Audio comment is 👉 {comment.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if comment.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        lyrics = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Audio lyrics **",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        # await lyrics.delete()
        await lyrics.request.delete()
        logger.info(
            f"Audio lyrics is 👉 {lyrics.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if lyrics.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        artist = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Artist Name**",
            reply_markup=CANCEL_SKIP,
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #  await artist.delete()
        await artist.request.delete()
        logger.info(
            f"Audio Artist Name is 👉 {artist.text} For user {update.from_user.id} @{update.from_user.username}"
        )
        if artist.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            await clear_server(user_id, saved_file_path)
            return

        answer = await bot.ask(
            chat_id=update.message.chat.id,
            text=f"**✶ Send me The Album Art Image**",
            filters=filters.photo | filters.text,  # filters.photo | filters.text
            reply_markup=CANCEL_SKIP,
            reply_to_message_id=reply_msg.id,
        )
        await answer.request.delete()
        if answer.text == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
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
        if not os.path.exists(
            Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
        ):
            os.makedirs(Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/")

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

    try:
        duration = await Ranjan.get_duration(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : {e}")
        return

    try:
        time_format = datetime.timedelta(seconds=duration)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ **Error** : Duration not found")
        return

    try:
        music = load_file(saved_file_path)
    except Exception as e:
        await clear_server(user_id, saved_file_path)
        print(e)
        await msg_edit(bc, f"⚠️ Music loading failed\n\n👉 First convert it to mp3")
        return

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
            file_name = os.path.basename(saved_file_path)
            extension = "mp3"
            description_ = os.path.splitext(file_name)[0]  # +'.mp4'
        except:
            description_ = "Default_Name"
            extension = "mp3"

    try:
        cd = await bc.edit(f"**Music Tag Editing....**")
    except:
        await delete_msg(bc)
        try:
            cd = await update.message.reply(
                "**Music Tag Editing....**", reply_to_message_id=reply_msg.id
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
        artist = f"{artist.text}"
        album = f"{album.text}"
        genre = f"{genre.text}"
        comment = f"{comment.text}"
        lyrics = f"{lyrics.text}"
    except:
        artist = "."
        album = "."
        genre = "."
        comment = "."
        lyrics = "."

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            description_ = f"{cfile_name}.{extension}"
        except:
            description_ = f"{description_}.{extension}"
    # ----------------- Art --------------
    if artist != "Skip":
        try:
            music.remove_tag("album")
        except:
            pass
        try:
            music["album"] = album
        except:
            pass

    if genre != "Skip":
        try:
            music.remove_tag("genre")
        except:
            pass
        try:
            music["genre"] = genre
        except:
            pass

    if comment != "Skip":
        try:
            music.remove_tag("comment")
        except:
            pass
        try:
            music["comment"] = comment
        except:
            pass

    if lyrics != "Skip":
        try:
            music.remove_tag("lyrics")
        except:
            pass
        try:
            music["lyrics"] = lyrics
        except:
            pass

    # ---------------------------------------------
    try:
        new_file_name = f"{cfile_name}.{extension}"
    except:
        new_file_name = f"{description_}.{extension}"

    try:
        title = f"{title.text}"
    except:
        title = new_file_name

    # ---------- Art Removing & Adding -------------
    if artist != "Skip":
        try:
            music.remove_tag("artist")
        except:
            pass
        try:
            music["artist"] = artist
        except:
            pass

    if title != "Skip":
        try:
            music.remove_tag("title")
        except:
            pass
        try:
            music["title"] = title
        except:
            pass

    thumb = "temp/artwork.jpg"
    if not answer.text:
        if answer.photo:
            await bot.download_media(message=answer.photo, file_name=thumb)
            music.remove_tag("artwork")
            with open(thumb, "rb") as img_in:
                music["artwork"] = img_in.read()
    music.save()

    image_data = None
    if not answer.text:
        try:
            artwork = music["artwork"]
            image_data = artwork.value.data
            img = Image.open(io.BytesIO(image_data))
            img.save(thumb)
        except ValueError:
            image_data = None

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
            await clear_server(user_id, saved_file_path, thumb)
            logger.info(
                f" ⚠️⚠️ can't send ef message To {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

    if (await db.get_auto_rename(update.from_user.id)) is True:
        try:
            file_name = f"{cfile_name}.{extension}"
        except:
            file_name = f"{description_}.{extension}"
    else:
        file_name = f"{description_}.{extension}"

    try:
        file_size_output = os.path.getsize(real_audio)  # Working best
        output_size = humanbytes(file_size_output)
        description_ = (
            "File Name : " + f"`{file_name}`" + f"\n\nFile Size : {output_size}"
        )
    except:
        description_ = f"`{file_name}`"

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
                audio=saved_file_path,
                file_name=new_file_name,
                performer=artist if artist != "Skip" else None,
                title=title if title != "Skip" else None,
                caption=description_,
                duration=duration,
                thumb=thumb if answer.photo or image_data else None,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, thumb)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Mp3 Tag Editor"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio Tag Added ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
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
                document=saved_file_path,
                file_name=new_file_name,
                caption=description_,
                force_document=True,
                thumb=thumb if answer.photo or image_data else None,
                reply_to_message_id=reply_msg.id,
                progress=progress_bar.progress_for_pyrogram,
                progress_args=("**Uploading....**", c_time),
            )

            if (
                CANCEL_PROCESS[update.message.chat.id]
                and ef.id in CANCEL_PROCESS[update.message.chat.id]
            ):
                await clear_server(user_id, saved_file_path, thumb)
                return

            last_msg = None
            last_msg = await dmsg_edit(ef, ".")
            await delete_msg(last_msg)

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await diksha.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Mp3 Tag Editor"
                    )
                except FloodWait:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(e)
            logger.info(
                f" Audio Tag Added ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except Exception as e:
            print(e)
            await msg_edit(ef, f"⚠️ **Error** : {e}")

    await clear_server(user_id, saved_file_path, thumb)
