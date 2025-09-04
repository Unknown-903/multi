import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import Config
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_callback_query(filters.regex("^openSettings"))
async def settings_call(bot, update):
    await OpenSettings(update.message, update.from_user.id)
    try:
        alert_text = f"Settings 🏠"
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^audSetting"))
async def a_settings(bot, update):
    await audios_settings(update.message, update.from_user.id)
    try:
        alert_text = f"Audio Settings...."
        await update.answer(alert_text)
    except:
        pass


async def OpenSettings(m: Message, user_id: int):
    comqualitdb = await db.get_audio_quality(id=user_id)
    speeddbaud = await db.get_audio_speed(id=user_id)
    main_quality = await db.get_mainquality_a(id=user_id)
    voludbaud = await db.get_audio_vol(id=user_id)
    bassaudio = await db.get_bassaudio(id=user_id)
    trebleaudio = await db.get_trebleaudio(id=user_id)
    yfilter = await db.get_yfilter(user_id)
    await db.get_audio_reverb(user_id)

    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        try:
            await m.edit(
                text="⚙️ **Config Bot Settings**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"🖼️ Thumbnail : {'Yes' if (await db.get_othumb(id=user_id)) is True else 'No'}",
                                callback_data="othumb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"✏️ Rename File : {'Yes' if (await db.get_auto_rename(id=user_id)) is True else 'No'}",
                                callback_data="auto_rename",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🔊 Upload as Audio' if (await db.get_upload_as(id=user_id)) is True else '🔊 Upload as Doc'}",
                                callback_data="upload_as",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🎥 Upload as Video' if (await db.get_asvideos(id=user_id)) is True else '🎥 Upload as Doc'}",
                                callback_data="asvideos",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"⚙️ Audio Settings",
                                callback_data="audSetting",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "❌ Close Settings", callback_data="closec"
                            )
                        ],
                    ]
                ),
            )

        except MessageNotModified:
            pass
        except Exception as err:
            raise err

    if (
        Config.ONLY_URL_UPLOADER.upper() == "YES"
        or Config.ONLY_YT_PLAYLIST_UPLOAD.upper() == "YES"
    ):
        try:
            await m.edit(
                text="⚙️ **Config Bot Settings**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"🖼️ Thumbnail : {'Yes' if (await db.get_othumb(id=user_id)) is True else 'No'}",
                                callback_data="othumb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"Rename File : {'Yes' if (await db.get_auto_rename(id=user_id)) is True else 'No'}",
                                callback_data="auto_rename",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🔊 Upload as Audio' if (await db.get_upload_as(id=user_id)) is True else '🔊 Upload as Doc'}",
                                callback_data="upload_as",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🎥 Upload as Video' if (await db.get_asvideos(id=user_id)) is True else '🎥 Upload as Doc'}",
                                callback_data="asvideos",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"YTDL Filter : {yfilter}", callback_data="filterytdl"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "❌ Close Settings", callback_data="closec"
                            )
                        ],
                    ]
                ),
            )

        except MessageNotModified:
            pass
        except Exception as err:
            raise err


@Client.on_message(filters.private & filters.command("settings"))
async def settings_(bot, update):
    user_id = update.from_user.id
    comqualitdb = await db.get_audio_quality(id=user_id)
    speeddbaud = await db.get_audio_speed(id=user_id)
    main_quality = await db.get_mainquality_a(id=user_id)
    voludbaud = await db.get_audio_vol(id=user_id)
    bassaudio = await db.get_bassaudio(id=user_id)
    trebleaudio = await db.get_trebleaudio(id=user_id)
    yfilter = await db.get_yfilter(user_id)
    await db.get_audio_reverb(user_id)

    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        try:
            set_tings = await update.reply(
                "**Processing....**", reply_to_message_id=update.id
            )
        except Exception as e:
            print(e)
            return
        try:
            await set_tings.edit(
                text="⚙️ **Config Bot Settings**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"🖼️ Thumbnail : {'Yes' if (await db.get_othumb(id=user_id)) is True else 'No'}",
                                callback_data="othumb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"✏️ Rename File : {'Yes' if (await db.get_auto_rename(id=user_id)) is True else 'No'}",
                                callback_data="auto_rename",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🔊 Upload as Audio' if (await db.get_upload_as(id=user_id)) is True else '🔊 Upload as Doc'}",
                                callback_data="upload_as",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🎥 Upload as Video' if (await db.get_asvideos(id=user_id)) is True else '🎥 Upload as Doc'}",
                                callback_data="asvideos",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"⚙️ Audio Settings",
                                callback_data="audSetting",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "❌ Close Settings", callback_data="closec"
                            )
                        ],
                    ]
                ),
            )
            logger.info(
                f"👨‍💼 (/settings) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except MessageNotModified:
            pass
        except Exception as err:
            raise err

    if (
        Config.ONLY_URL_UPLOADER.upper() == "YES"
        or Config.ONLY_YT_PLAYLIST_UPLOAD.upper() == "YES"
    ):
        try:
            set_tings = await update.reply(
                "**Processing....**", reply_to_message_id=update.id
            )
        except Exception as e:
            print(e)
            return
        try:
            await set_tings.edit(
                text="⚙️ **Config Bot Settings**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"🖼️ Thumbnail : {'Yes' if (await db.get_othumb(id=user_id)) is True else 'Yes'}",
                                callback_data="othumb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"Rename File : {'Yes' if (await db.get_auto_rename(id=user_id)) is True else 'No'}",
                                callback_data="auto_rename",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🔊 Upload as Audio' if (await db.get_upload_as(id=user_id)) is True else '🔊 Upload as Doc'}",
                                callback_data="upload_as",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"{'🎥 Upload as Video' if (await db.get_asvideos(id=user_id)) is True else '🎥 Upload as Doc'}",
                                callback_data="asvideos",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"YTDL Filter : {yfilter}", callback_data="filterytdl"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "❌ Close Settings", callback_data="closec"
                            )
                        ],
                    ]
                ),
            )
            logger.info(
                f"👨‍💼 (/settings) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except MessageNotModified:
            pass
        except Exception as err:
            raise err


####-----;;;;;;;;;-#&+((()))
async def audios_settings(m: Message, user_id: int):
    comqualitdb = await db.get_audio_quality(id=user_id)
    speeddbaud = await db.get_audio_speed(id=user_id)
    main_quality = await db.get_mainquality_a(id=user_id)
    voludbaud = await db.get_audio_vol(id=user_id)
    bassaudio = await db.get_bassaudio(id=user_id)
    trebleaudio = await db.get_trebleaudio(id=user_id)
    await db.get_yfilter(user_id)
    audio_reverb = await db.get_audio_reverb(user_id)

    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        try:
            await m.edit(
                text="⚙️ **Config Bot Settings**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"🔊 Audio Quality : {main_quality} kbps",
                                callback_data="mainqualitycb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Audio Speed : {speeddbaud}%",
                                callback_data="speeddbaud",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Compress Audio : {comqualitdb}",
                                callback_data="comqualitdb",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Bass Booster : {bassaudio}",
                                callback_data="bassctrl",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Treble Booster : {trebleaudio}",
                                callback_data="treblectrl",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Audio Volume : {voludbaud}%",
                                callback_data="volumectrl",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                f"🔊 Audio Reverb : {audio_reverb}%",
                                callback_data="areverb",
                            )
                        ],
                        [InlineKeyboardButton("⬅️ Back", callback_data="openSettings")],
                    ]
                ),
            )

        except MessageNotModified:
            pass
        except Exception as err:
            raise err
