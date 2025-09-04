import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Diksha:

    VIDEO_CONVERTER = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎥 Video Converter", callback_data="streamvid"),
            ],
            [
                InlineKeyboardButton("Convert To MP4", callback_data="mkv_mp4"),
                InlineKeyboardButton("Convert To MKV", callback_data="convmkv"),
            ],
            [
                InlineKeyboardButton("Convert as Video", callback_data="docvid"),
                InlineKeyboardButton("Convert as File", callback_data="viddoc"),
            ],
            [InlineKeyboardButton("Main Menu", callback_data="vmainback")],
        ]
    )

    VIDEO_RENAMER = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎥 Video Renamer", callback_data="renamerf"),
            ],
            [
                InlineKeyboardButton("Rename as Video", callback_data="vrenamev"),
                InlineKeyboardButton("Rename as File", callback_data="frenamef"),
            ],
            [InlineKeyboardButton("Back", callback_data="vmainback")],
        ]
    )

    AUDIO_MERGER = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("➕ Merge 2 Audios", callback_data="merger_audio"),
            ],
            [
                InlineKeyboardButton("➕ Merge 3 Audios", callback_data="threeaudio"),
                InlineKeyboardButton("➕ Merge 5 Audios", callback_data="fifthaudio"),
            ],
            [InlineKeyboardButton("Main Menu", callback_data="amainback")],
        ]
    )

    VCAPTION_EDITOR = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Forwarded Tag Remove", callback_data="copyfile"),
            ],
            [
                InlineKeyboardButton(
                    "Add Caption And Buttons", callback_data="baddcapbut"
                ),
            ],
            [
                InlineKeyboardButton("Remove Caption", callback_data="capremove"),
                InlineKeyboardButton("Add New Caption", callback_data="capadd"),
            ],
            [
                InlineKeyboardButton("Remove Buttons", callback_data="removebutton"),
                InlineKeyboardButton("Add New Buttons", callback_data="capbutton"),
            ],
            [InlineKeyboardButton("Main Menu", callback_data="vmainback")],
        ]
    )

    ACAPTION_EDITOR = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Forwarded Tag Remove", callback_data="copyfile"),
            ],
            [
                InlineKeyboardButton(
                    "Add Caption And Buttons", callback_data="baddcapbut"
                ),
            ],
            [
                InlineKeyboardButton("Remove Caption", callback_data="capremove"),
                InlineKeyboardButton("Add New Caption", callback_data="capadd"),
            ],
            [
                InlineKeyboardButton("Remove Buttons", callback_data="removebutton"),
                InlineKeyboardButton("Add New Buttons", callback_data="capbutton"),
            ],
            [InlineKeyboardButton("Main Menu", callback_data="amainback")],
        ]
    )

    VIDEO_TRIMMER = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Trimmer 1", callback_data="opcut"),
                InlineKeyboardButton("Trimmer 2", callback_data="chhcut"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    MEDIAINFO_FPROBE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Fprobe", callback_data="fprobe"),
                InlineKeyboardButton("MediaInfo", callback_data="infomedia"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )


# -------- MediaInfo Generator----------#


@Client.on_callback_query(filters.regex("^real_info"))
async def mediainfo_fprob(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "**Fprobe :** For Media Information by Fprobe\n\n**MediaInfo :** For Media Information by Mediainfo\n\n**Choose your appropriate action  👇**",
            reply_markup=Diksha.MEDIAINFO_FPROBE,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# -------- Video Caption & Tag Remove----------#


@Client.on_callback_query(filters.regex("^randtrim"))
async def maintrim_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "**Trimmer 1 :** __For Start Time to EndTime__\n\n**Example** 👉 __Start time `0:01:00` And End Time `0:10:00` Then Video will be trimmed `0:01:00` To `0:10:00` (hh:mm:ss). Means 9 Minutes__\n\n**Trimmer 2 :** __Trimmed Duration From Start Time__\n\n**Example** 👉 __Start Time `0:05:00` And Trimmed Duration `0:10:00` Then Video will be Trimmed `0:10:00` From `0:05:00` (hh:mm:ss) __\n\n**Choose your appropriate action  👇**",
            reply_markup=Diksha.VIDEO_TRIMMER,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# -------- Video Caption & Tag Remove----------#
@Client.on_callback_query(filters.regex("^vvcaption"))
async def vvcaption_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "**Choose your appropriate action  👇**", reply_markup=Diksha.VCAPTION_EDITOR
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# -------- Audio Caption & Tag Remove----------#
@Client.on_callback_query(filters.regex("^aacaption"))
async def aacaption_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "**Choose your appropriate action  👇**", reply_markup=Diksha.ACAPTION_EDITOR
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# --------------- For video ------------------#
@Client.on_callback_query(filters.regex("^vconvertmain"))
async def _vconvertmain(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "__✶ If you want to set custom thumbnail on video, then first send an image and save as Custom Thumbnail.\n\n**Note** : Settings don't work on mensioned options; **As video/As file**__\n\n**Choose your appropriate action 👇**",
            reply_markup=Diksha.VIDEO_CONVERTER,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


@Client.on_callback_query(filters.regex("^vrenamemain"))
async def vrenamemain_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "__✶ If you want to set custom thumbnail on video, then first send an image and save as Custom Thumbnail.\n\n**Note** : Settings don't work on mensioned options; **As video/As file**__\n\n**Choose your appropriate action 👇**",
            reply_markup=Diksha.VIDEO_RENAMER,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# -------------------- For Audio --------------#
@Client.on_callback_query(filters.regex("^amerget"))
async def amerget_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            "__✶ For Longer audio, it will take time. Because Encoding is a slow process And It needs more RAM. So, added File_Size & Duration limit.\n\n**Note** : First Go to `/Settings` And **Set Audio Quality**__\n\n**Choose your appropriate action 👇**",
            reply_markup=Diksha.AUDIO_MERGER,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)
