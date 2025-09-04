import asyncio
import logging

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from config import Config
from plugins.admin.paid import check_user_plan

##################### Objects ##################


class Chitranjan(object):
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Functions", callback_data="function"),
                InlineKeyboardButton("Instructions", callback_data="instruct"),
            ],
            [InlineKeyboardButton("Pay Now", url="https://t.me/Legend_Shivam_7")],
        ]
    )

    BACK_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="nsback"),
            ]
        ]
    )

    SUBS_TEXTS = """Only paid users can use me.
"""

    INSTRUCTION_TEXTS = """ 
✶ __This Bot is for those users, who don't want to wait for next process in free bot. We made this on demanding of Users.__\n
Your User Id: {}
User Type: {}\n
✶ **Here is our Paid plans** 👇\n
✶ **Features:** There will No Time Gap, No process limit, No upload limit and many more.\n
✶ Paid Plan: €1.00 or 1$ or ₹49/Month.\n
✶ For UPI/Google Pay/Phone Pe/Paytm Pay On `shivam342003@paytm`\n
✶ After making payment, Send screenshot to [Shivam](https://t.me/Legend_Shivam_7) for plan Activation.\n
"""

    PAID_TEXTS = """ 
✶ __Dear User **{}**, Here is your Plan Details:__\n
**Your User Id:** `{}`\n
**User Type:** {}\n
**Plan Validity:** {} Days\n
**Plan Started On:** {}\n
**Your Plan Left:** {}\n
**Your Plan will Expire On:** {}\n
Message [Shivam](https://t.me/Legend_Shivam_7), if you have any problems using the bot. 
"""
    # --------------- Universal-------------------#
    START_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("About", callback_data="about"),
                InlineKeyboardButton("Help", callback_data="help"),
            ],
            [InlineKeyboardButton("Close", callback_data="close")],
        ]
    )

    HELP_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("About", callback_data="about"),
                InlineKeyboardButton("Home", callback_data="home"),
            ],
            [InlineKeyboardButton("Close", callback_data="close")],
        ]
    )

    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Home", callback_data="home"),
                InlineKeyboardButton("Help", callback_data="help"),
            ],
            [InlineKeyboardButton("Close", callback_data="close")],
        ]
    )

    LIST_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Home", callback_data="home"),
                InlineKeyboardButton("Help", callback_data="help"),
            ]
        ]
    )

    CLOSE_BUTTON = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Close", callback_data="close")],
        ]
    )
    # https://telegra.ph/Bot-Functions-02-07
    # https://telegra.ph/Multi-Usage-Bot-10-20
    # --------------- Universal-------------------#
    BOT_LIST = """**Our Bot List**\n

✶ **Note** :- __If you want to see functions of [Multi Usage Bot](https://telegra.ph/Bot-Functions-02-07) 👈 Click__
"""

    # ---------- Only 4 URL Uploader--------------#
    if Config.ONLY_URL_UPLOADER.upper() == "YES":
        START_TEXT = """**Hi {}**\n
I am an Url Uploader Bot.\n
Custom File Format Filter is available Go to /settings And set ytdl filter according to your need\n
Custom Thumbnail/FileName Support\n
Click help button for more details.
"""

        HELP_TEXT = """**Do you need help ?**\n
✶ If you want to Rename Output file. Then Activate ✅ Rename File in ⚙️ settings (𝚘𝚙𝚝𝚒𝚘𝚗𝚊𝚕)\n
✶ Send me the custom thumbnail to save it permanently. (𝚘𝚙𝚝𝚒𝚘𝚗𝚊𝚕)\n
✶ Also you can customise Option (Thumbnail On/Off)\n
✶ Now send me the url which you want to upload\n
✶ Now select the desired format.\n
✶ Then wait, By the time your file is uploaded.\n

✶ __**Note :-** Do not send more than an url at once. Otherwise the Time Gap will be increased to 2 minutes.__"""

    # ------- Only 4 Playlist Uploader------------#
    if Config.ONLY_YT_PLAYLIST_UPLOAD.upper() == "YES":
        START_TEXT = """**Hi {}**\n
This is yt playlist downloader.\n
You can Download whole playlist by using Spacific Range.\n
You can set your custom thumbnail too\n
Click on help button for more details.
"""

        HELP_TEXT = """✶ Send the custom thumbnail to save it permanently. (Optional)\n
✶ There are 3 Methods to Download Playlist\n 
✶ If your playlist length is more than 50 Videos, Then use **Specific Range** Method\n
✶ Example : `21-30` Then 10 Videos will Upload from 21-30 of Your playlist\n
✶ Check your Upload Mode in /settings\n
✶ Now send the YouTube url or playlist url\n
✶ Then select Quality & Playlist Download Mode\n
✶ Then wait, By the time your videos are uploaded.\n
✶ __**Note** :- Don't send more than an url at once. Otherwise time_gap will be increased to 10 minutes. __
"""

    # --------- Only Spotify Downloader------------#
    if Config.ONLY_SPOTIFY_DOWNLOADER.upper() == "YES":
        START_TEXT = """**Hi {}**\n
I am a Spotify Songs downloader.\n
You can Download whole Spotify Songs playlist.\n
I am able to Download Track/Playlist/Album/Artist Links.\n
Click on help button for more details.
"""

        HELP_TEXT = """**Do you need help ?** 🤔\n
✶ Send the custom thumbnail to save it permanently. (Optional)\n
✶ Very simple to Use, just send me url\n
✶ Then an option will appear for Audio Format Selection\n
✶ Formats are mp3/wav/m4a/flac/ogg/opus \n
✶ Now Select the desired audio format\n 
✶ Then wait, By the time your audio is uploaded\n
✶ **Note :-** Do not send more than an url at once. Otherwise the Time Gap will be increased to 5 minutes.
"""

    # --------------- Universal-------------------#
    if Config.ONLY_UNI_START_TEXT.upper() == "YES":
        START_TEXT = """**Hi {}**\n
I Am A URL Uploader Bot.\n
With Many Features\n
🌟 Supports 4 GB Upload For Premium Account\n
More Than 4GB File/Video Will Be Split in Parts.\n
For Audio, Before Using, First Set Audio Quality in /settings\n
For Upload Setting Use /usettings
"""

        HELP_TEXT = """✶ You can customise /Settings (Rename File, Upload Mode)\n 
✶ **If you send Video**, Then this option will come 👇\n 
__(1). Audio & Subtitles Remover\n
(2). Audio & Subtitles Extractor\n
(3). Caption & Buttons Editor\n
(4). Video Trimmer\n
(5). Video Merger\n
(6). Mute Audio in Video File \n
(7). Video And Audio Merger \n
(8). Video to GIF Converter\n
(9). Screenshot generator\n
(10). Manual Screenshot generator\n
(11). Video sample generator\n
(12). Video to (wav, mp3, ac3, aac, flac, wma, m4a, opus, ogg) Converter in Customisable Quality.\n
(13). Video converter (Stream, mkv, mp4)\n
(14). Video Renamer\n
(15). Media Information\n
(16). Make Archive File (zip, rar, 7z) (Password Optional)\n__

✶ **If you send Audio**, Then this option will come 👇\n 
__(1). Caption & Buttons Editor\n
(2). Song Slowed & Reverb Maker\n
(3). Audio Converter (wav, mp3, ac3, aac, flac, wma, m4a, opus, ogg etc) in Customisable Quality.\n
(4). Make Archive File (zip, rar, 7z)\n
(5). Audio Merger, Set Quality in /settings\n
(6). Audio 8D Converter With many options.\n
(7). Music Equalizer (Volume, Bass, Treble, Speed)\n
(8). Audio Bass Booster with Range (-20 To 20)\n
(9). Audio Treble Booster with Range (-20 To 20)\n
(10). Audio Trimmer - from Start_time to End_time.\n
(11). Auto Audio Trimmer with Start_time and Trim Duration\n
(12). Rename Audio files or documents\n
(13). Audio Tag Editor (Album Art) ✍️\n
(14). Audio speed Changer 50-200% /settings\n
(15). Volume Changer, changes volume of audio 10 to 200%\n
(16). Media Information\n
(17). Compress Audio, Customise audio compress Range in /settings\n__

✶ **If you send URL**, Then this option will come According to Your Link 👇\n 
__(1). 🖼️ Thumbnail Downloader\n
(2). 🔗 Make Direct/Stream Link\n
(3). Extract Archive via Direct Link (Extract zip, rar, 7z, tar etc)\n
(4). 🔗 URL Uploader [(Link To File)](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)\n
(5). Link Shortner & Unshortener\n
(6). If your 🔗 url will be a direct link Then you can use Audio & Video related functions.\n
(7). Fast Download: It Uploads YouTube video Without Downloading (Quality HD)\n
(8). YouTube Video Trimmer ✂️, It Trims YouTube video (Quality HD)\n
(9). YouTube Music & Video, You can download High Quality Music with YouTube Music link.\n__
(10). YouTube Playlist Downloader, with 3 options (Default, Specific Range, Custom Specific Range).\n
(11). Mediafire link downloader\n
(12). Google Drive Downloader ( You can Download anything (Photo, video, archive, documents etc) & Folder too.\n
(13). Spotify Songs Downloader (Track/Playlist/Album/Artist Link) With Option Of Audio Format (mp3/m4a/flac/opus/ogg/wav)\n
✶ **Note :** 🔗 __Direct link supports. And **Custom thumbnail** Supports in All Video functions, Just send an image to set as Custom Thumbnail__\n
"""


############## Subscription ##############


@Client.on_callback_query(filters.regex("^function"))
async def functionb(c, m):
    try:
        await m.answer()
    except:
        pass
    try:
        await m.message.edit_text(
            text=Chitranjan.HELP_TEXT,
            reply_markup=Chitranjan.BACK_BUTTON,
            disable_web_page_preview=True,
        )
    except:
        pass


@Client.on_callback_query(filters.regex("^nsback"))
async def nsback_(c, m):
    try:
        await m.answer()
    except:
        pass
    try:
        await m.message.edit_text(
            text=Chitranjan.SUBS_TEXTS,
            reply_markup=Chitranjan.SUB_BUTTONS,
        )
    except:
        pass


@Client.on_callback_query(filters.regex("^instruct"))
async def instruct_(c, m):
    user_type = "Free"
    user_name = m.from_user.first_name
    user_id = m.from_user.id

    try:
        await m.answer()
    except:
        pass

    (
        paid_usr_count,
        paid_on,
        paid_duration,
        will_expire_days,
        will_expire_on_date,
    ) = await check_user_plan(c, m)
    if paid_usr_count == 0:
        user_type = "Free"

    else:
        user_type = "Paid"
        plan_valid = paid_duration
        joined_on = paid_on
        try:
            await m.message.edit_text(
                text=Chitranjan.PAID_TEXTS.format(
                    user_name,
                    user_id,
                    user_type,
                    plan_valid,
                    joined_on,
                    will_expire_days,
                    will_expire_on_date,
                ),
                reply_markup=Chitranjan.BACK_BUTTON,
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.info(e)
        return

    try:
        await m.message.edit_text(
            text=Chitranjan.INSTRUCTION_TEXTS.format(m.from_user.id, user_type),
            reply_markup=Chitranjan.BACK_BUTTON,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.info(e)


##################### Callbacks ###############


@Client.on_callback_query()
async def cb_button(bot, update):
    if update.data == "close":
        try:
            await update.message.edit_text(text="Closing....")
            await asyncio.sleep(0.3)
            await update.message.edit_text(text="Closed  ✅")
        except:
            pass
    else:
        raise ContinuePropagation


@Client.on_callback_query(filters.regex("^home"))
async def home_cb(c, m):
    try:
        await m.answer()
    except:
        pass
    try:
        await m.message.edit_text(
            text=Chitranjan.START_TEXT.format(m.from_user.mention),
            reply_markup=Chitranjan.START_BUTTONS,
        )
    except:
        pass


@Client.on_callback_query(filters.regex("^help"))
async def help_cb(c, m):
    try:
        await m.answer()
    except:
        pass
    try:
        await m.message.edit_text(
            text=Chitranjan.HELP_TEXT,
            reply_markup=Chitranjan.HELP_BUTTONS,
            disable_web_page_preview=True,
        )
    except:
        pass


@Client.on_callback_query(filters.regex("^about"))
async def about_cb(c, m):
    try:
        await m.answer()
    except:
        pass
    try:
        await m.message.edit_text(
            text=Chitranjan.BOT_LIST.format(m.from_user.mention),
            reply_markup=Chitranjan.ABOUT_BUTTONS,
            disable_web_page_preview=True,
        )
    except:
        pass


###################### Commands ###################


@Client.on_message(filters.private & filters.command("start"))
async def start_(bot, update):
    b = None
    try:
        b = await bot.send_message(
            chat_id=update.chat.id,
            text="Processing....",
            reply_to_message_id=update.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    try:
        await bot.edit_message_text(
            text=Chitranjan.START_TEXT.format(update.from_user.mention),
            reply_markup=Chitranjan.START_BUTTONS,
            chat_id=update.chat.id,
            message_id=b.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    logger.info(
        f"👨‍💼 (/start) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_message(filters.private & filters.command("help"))
async def help_(bot, update):
    try:
        b = await bot.send_message(
            chat_id=update.chat.id,
            text="Processing....",
            reply_to_message_id=update.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    try:
        await bot.edit_message_text(
            text=Chitranjan.HELP_TEXT,
            reply_markup=Chitranjan.HELP_BUTTONS,
            chat_id=update.chat.id,
            message_id=b.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    logger.info(
        f"👨‍💼 (/help) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_message(filters.private & filters.command("about"))
async def about_(bot, update):
    try:
        c = await bot.send_message(
            chat_id=update.chat.id,
            text="Processing....",
            reply_to_message_id=update.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    try:
        await bot.edit_message_text(
            text=Chitranjan.BOT_LIST.format(update.from_user.mention),
            reply_markup=Chitranjan.ABOUT_BUTTONS,
            chat_id=update.chat.id,
            message_id=c.id,
            disable_web_page_preview=True,
        )
    except:
        pass
    logger.info(
        f"👨‍💼 (/about) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_message(filters.command(["upgrade", "plan", "plans"]))
async def upgrade_(bot, update):
    user_type = "Free"
    user_name = update.from_user.first_name
    user_id = update.from_user.id
    logger.info(
        f"👨‍💼 (/upgrade) Command Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    try:
        replied = await update.reply(
            "**Processing....**", reply_to_message_id=update.id
        )
    except Exception as e:
        logger.info(e)

    (
        paid_usr_count,
        paid_on,
        paid_duration,
        will_expire_days,
        will_expire_on_date,
    ) = await check_user_plan(bot, update)
    if paid_usr_count == 0:
        user_type = "Free"

    else:
        user_type = "Paid"
        plan_valid = paid_duration
        joined_on = paid_on
        try:
            await replied.edit(
                text=Chitranjan.PAID_TEXTS.format(
                    user_name,
                    user_id,
                    user_type,
                    plan_valid,
                    joined_on,
                    will_expire_days,
                    will_expire_on_date,
                ),
                reply_markup=Chitranjan.CLOSE_BUTTON,
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.info(e)
        return

    try:
        await replied.edit(
            text=Chitranjan.INSTRUCTION_TEXTS.format(update.from_user.id, user_type),
            reply_markup=Chitranjan.CLOSE_BUTTON,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.info(e)


@Client.on_message(filters.private & filters.command("premium"))
async def primiumcheck(bot, update):
    user = update.from_user
    check_primium = False
    try:
        check_primium = user.is_premium
        if user.is_premium:
            check_primium = user.is_premium
        else:
            check_primium = False
    except:
        check_primium = False

    try:
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"👦 User Id: {update.from_user.id}\n\n🌟 Premium User: {check_primium}",
            reply_to_message_id=update.id,
            disable_web_page_preview=True,
        )
    except:
        pass


"""
    if Config.PAID_SUBS:
        try:
            chat = await bot.get_chat_member(
                chat_id=(
                    int(Config.PAID_SUBS)
                    if Config.PAID_SUBS.startswith("-100")
                    else Config.PAID_SUBS
                ),
                user_id=update.from_user.id,
            )
            chat_stats = chat.status
            if f"{chat_stats}" == "ChatMemberStatus.BANNED":
                user_type = "Banned"
            if f"{chat_stats}" == "ChatMemberStatus.OWNER":
                user_type = "Owner"
            if f"{chat_stats}" == "ChatMemberStatus.ADMINISTRATOR":
                user_type = "Admin"
            if f"{chat_stats}" == "ChatMemberStatus.MEMBER":
                user_type = "Paid"
            if f"{chat_stats}" == "ChatMemberStatus.RESTRICTED":
                user_type = "Restricted"
            if f"{chat_stats}" == "ChatMemberStatus.LEFT":
                user_type = "Left"
        except UserNotParticipant:
            user_type = "Free"
        except Exception:
            user_type = "Free"

"""
