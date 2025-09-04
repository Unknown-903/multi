import datetime
import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from plugins.audio import COUNT, force_sub, force_sub_two, paid_service_subs
from plugins.main.timegap_check import timegap_check

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Baby:

    MAIN_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🖼️ Thumbnail Downloader", callback_data="thumbdl"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔗 Make Direct/Stream Link", callback_data="ydlink"
                ),
            ],
            [
                InlineKeyboardButton("Extract Archive", callback_data="aextract"),
                InlineKeyboardButton("🔗 Url Uploader", callback_data="vytvideo"),
            ],
            [
                InlineKeyboardButton(
                    "🔗 Link Short & Unshort", callback_data="shortunshort"
                ),
            ],
            [
                InlineKeyboardButton("🎵 Audio", callback_data="caudio"),
                InlineKeyboardButton("🎥 Video", callback_data="cvideo"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    YT_PLAYLIST = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "YouTube Playlist Downloader", callback_data="yplaylist"
                ),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    SPOTIFY = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Spotify Songs Downloader", callback_data="spotify"
                ),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    URL_UPLOADER = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗 URL Uploader", callback_data="vytvideo"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    YT_MUSIC = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖼️ Thumbnail Download", callback_data="thumbdl"),
            ],
            [
                InlineKeyboardButton(
                    "🔗 Link Short & Unshort", callback_data="shortunshort"
                )
            ],
            [
                InlineKeyboardButton("🎵 YouTube Music", callback_data="oytsong"),
                InlineKeyboardButton("🎥 YouTube Video", callback_data="yonlyyt"),
            ],
            [
                InlineKeyboardButton("🎥 Fast Downloader", callback_data="flashdl"),
                InlineKeyboardButton("✂️ YouTube Trimmer", callback_data="yttrim"),
            ],
            [
                InlineKeyboardButton(
                    "🔗 Make Direct/Stream Link", callback_data="ydlink"
                ),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    MEDIAFIRE_DL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("MediaFireDl File", callback_data="newmfdl"),
            ],
            [
                InlineKeyboardButton("MediaFire DL CLI", callback_data="mediafire"),
            ],
            [
                InlineKeyboardButton(
                    "MediaFire Downloader YTDL", callback_data="vytvideo"
                ),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    GOOGLE_DRIVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗 Url Uploader", callback_data="vytvideo"),
            ],
            [
                InlineKeyboardButton("Extract Archive", callback_data="aextract"),
            ],
            [
                InlineKeyboardButton(
                    "🔗 Link Short & Unshort", callback_data="shortunshort"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Google Drive Downloader", callback_data="folderdldr"
                ),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    VIDEO_FUNCTIONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎵 Audio & Subtitle Remover", callback_data="remstream"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎵 Audio & Subtitle Extractor", callback_data="strextract"
                ),
            ],
            [
                InlineKeyboardButton("✂️ Video Trimmer", callback_data="randtrim"),
                InlineKeyboardButton("🔇 Remove Audio", callback_data="mute_video"),
            ],
            [
                InlineKeyboardButton("🎥 Video To GIF", callback_data="gifvideo"),
                InlineKeyboardButton("🎥 Video Optimize", callback_data="reorderst"),
                # InlineKeyboardButton("🎥 Compress Video", callback_data="commm"),
            ],
            [
                InlineKeyboardButton(
                    "🖼️ Screenshots", callback_data="mvscreenshot"
                ),  # 1. mvscreenshot 2. vscreenshot
                InlineKeyboardButton("🖼️ Manual S-Shots", callback_data="mvshots"),
            ],
            [
                InlineKeyboardButton("🎥 Generate Sample", callback_data="disampl"),
                InlineKeyboardButton("🎵 Video To Audio", callback_data="vidbutmore"),
            ],
            [
                InlineKeyboardButton("Media Information", callback_data="real_info"),
                InlineKeyboardButton("🎥 Video To mp4", callback_data="mkv_mp4"),
            ],
            [InlineKeyboardButton("Cancel  ❌", callback_data="cancel_query")],
        ]
    )

    AUDIO_FUNCTIONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎵 Audio Converter", callback_data="allaudfunc"),
            ],
            [
                InlineKeyboardButton("🎼 8D Converter", callback_data="apulsator8D"),
                InlineKeyboardButton("🎼 Music Equalizer", callback_data="super_eq"),
            ],
            [
                InlineKeyboardButton("🔊 Bass Booster", callback_data="bassboost"),
                InlineKeyboardButton("🔊 Treble Booster", callback_data="trebleboost"),
            ],
            [
                InlineKeyboardButton("✂️ Audio Trimmer", callback_data="trimaud"),
                InlineKeyboardButton("✂️ Auto Trimmer", callback_data="aautotrimmer"),
            ],
            [
                InlineKeyboardButton("🎵 Speed Change", callback_data="speedcng"),
                InlineKeyboardButton("🔊 Volume Change", callback_data="volume_audio"),
            ],
            [
                InlineKeyboardButton("Media Information", callback_data="real_info"),
                InlineKeyboardButton("🔊 Compress Audio", callback_data="compressaud"),
            ],
            [InlineKeyboardButton("Cancel  ❌", callback_data="cancel_query")],
        ]
    )

    FOR_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎵 YouTube Music", callback_data="oytsong"),
                InlineKeyboardButton("🎥 YouTube Video", callback_data="yonlyyt"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )


@Client.on_message(
    filters.incoming & filters.private & filters.regex(pattern=".*http.*")
)
async def urlfilter_(bot, update):
    user_id = update.from_user.id
    user_name = update.from_user.username
    user_first = update.from_user.first_name
    logger.info(
        f"👉 {update.text} 👈 Sent by User {user_first} {str(user_id)} @{user_name}"
    )
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Functions", callback_data="function"),
                InlineKeyboardButton("Instructions", callback_data="instruct"),
            ],
            [InlineKeyboardButton("Pay Now", url="https://t.me/Legend_Shivam_7")],
        ]
    )
    if Config.PAID_BOT.upper() == "YES":
        try:
            paid_status = await db.get_paid_status(user_id)
        except:
            await update.reply("⚠️ First Click on /start, Then try again")
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
                    await bot.send_message(
                        update.chat.id,
                        f"👋 Your paid plan has Expired on {will_expire}\n\nIf you want to use the bot, You can do so by Paying.",
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                for i in Config.AUTH_USERS:
                    try:
                        await bot.send_message(
                            i,
                            f"🌟 **Plan Expired:** \n\n**User Id:** `{update.from_user.id}`\n\n**User Name:** @{update.from_user.username}\n\n**Plan Validity:** {paid_duration} Days\n\n**Joined On** : {paid_on}\n\n**Discription** : {paid_reason}",
                        )
                    except Exception:
                        logger.info(f"⚠️ Not found id {i}")
                return

            else:
                pass

        else:
            await update.reply_text(
                text="Only paid users can use me. For more information Click on **Instructions** Button\n\nPay ₹50\M Rupees On `shivam342003@paytm` And Send Screenshot To @Legend_Shivam_7",
                reply_markup=SUB_BUTTONS,
                disable_web_page_preview=True,
                quote=True,
            )
            return

    else:
        if update.from_user.id not in Config.VERIFIED_USERS:
            if Config.FORCE_SUBS:
                owhats = await force_sub(bot, update)
                if owhats == 9:
                    return
        # ------------------------------------#
        if update.from_user.id not in Config.VERIFIED_USERS:
            if Config.FORCE_SUBS_TWO:
                whatso = await force_sub_two(bot, update)
                if whatso == 9:
                    return
        # ------------------------------------#
        if update.from_user.id not in Config.VERIFIED_USERS:
            if Config.PAID_SUBS:
                whatsp = await paid_service_subs(bot, update)
                if whatsp == 9:
                    return

    # ------------------------------------#

    try:
        ban_status = await db.get_ban_status(update.from_user.id)
        if ban_status["is_banned"]:
            await bot.delete_messages(
                chat_id=update.chat.id, message_ids=update.id, revoke=True
            )
            await bot.send_sticker(
                chat_id=update.chat.id,
                sticker="CAACAgEAAxkBAAECFrdhvdCWEWU-CLXsSot2Dizyn_FkNAAC7wEAAnzn8UWxlVoBHyE2gh4E",
            )
            await update.reply(
                "**⚠️ Sorry You're Banned❗**\n\nFor help go to @Legend_Shivam_7"
            )
            return
    except:
        await update.reply("⚠️ First Click on /start, Then try again")
        return

    if update.from_user.id not in Config.AUTH_USERS:
        for_url = 1969772008
        if (await db.get_urlfunctions(id=Config.OWNER_ID)) is False:
            await update.reply(
                "⚠️ URL Functions Currently Disabled ",
                reply_to_message_id=update.id,
            )
            return

    if update.from_user.id not in Config.AUTH_USERS:
        if len(COUNT) > Config.NUMBER:
            await update.reply(
                f"**⚠️ Already {Config.NUMBERS}/{Config.NUMBERS} Process Running**\n\n👉 Bot is Overloaded. So, Try after a few minutes.\n\nIntrested users can Upgrade to Paid bot, To avoid Waiting Time and Process limits.",
                reply_to_message_id=update.id,
            )
            return

    if update.from_user.id not in Config.AUTH_USERS:
        if Config.TIME_GAP:
            time_gap = await timegap_check(update) 
            if time_gap:
                if Config.PAID_BOT.upper() != "YES":
                    await update.reply(
                        f"Interested users can Upgrade to Paid bot, To avoid Waiting Time and Process limits. (Paid Bot) at 30Rs PerMonth",
                        reply_to_message_id=update.id,
                    )
                return
            Config.TIME_GAP_STORE[update.from_user.id] = time.time()
    try:
        msg = await update.reply(
            "**Processing....**",
            reply_to_message_id=update.id,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(e)
        return




    if not update.text.startswith("http"):
        try:
            await msg.edit("⚠️ Send URL That starts with http")
        except Exception as e:
            print(e)
            return
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    if os.path.isdir(download_path):
        return await msg.edit(
            "⚠️ Please wait untill the previous task complete Or Cancel the previous task\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__"
        )

    #  text_url = update.text.split(None, 1)[0]
    #  if "playlist?list=" in text_url:
    #      await msg.edit("⚠️ I don't support Playlist")
    #      return
    # ---------- Only Spotify Downloader ---------#
    if Config.ONLY_SPOTIFY_DOWNLOADER.upper() == "YES":
        if "spotify.com" in update.text:
            await msg.edit(
                "**Spotify Songs Downloader :** __For Downloading Spotify Links__\n\nSelect your appropriate action 👇",
                reply_markup=Baby.SPOTIFY,
            )
            logger.info(
                f"spotify URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
            )
            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                    )
                except Exception as e:
                    print(e)
            return
        else:
            await msg.edit(
                "⚠️ Send me Only Spotify Song/Playlist/Album/Artist Link",
            )
            return

    # -------- Only YT Playlist Uploader ---------#
    if Config.ONLY_YT_PLAYLIST_UPLOAD.upper() == "YES":
        if "youtu" in update.text:
            text_url = update.text.split(None, 1)[0]
            if "playlist?list=" in text_url:
                await msg.edit(
                    f"**YouTube Playlist Downloader :** __For Downloading YouTube Playlist Video__\n\n**Note :- ** __To Reduce overload, Maxx Playlist Length Support upto **{Config.PMAX_LENGTH}**.__\n\nOr, you can use \n\nSelect your appropriate action 👇",
                    reply_markup=Baby.YT_PLAYLIST,
                )
                logger.info(
                    f"YouTube Playlist Link 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
                )
                if Config.LOG_CHANNEL:
                    try:
                        cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                        await cmf2v.reply_text(
                            f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                        )
                    except Exception as e:
                        print(e)
                return

            await msg.edit(
                "🎵 **YouTube Music :** __For Downloading Songs in High/Low Quality from YouTube__\n\nSelect your appropriate action 👇",
                reply_markup=Baby.YT_MUSIC,
            )
            logger.info(
                f"YouTube URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
            )
            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                    )
                except Exception as e:
                    print(e)
            return
        else:
            await msg.edit(
                "⚠️ Send me Only YouTube Link (Playlist)",
            )
            return
    # -------------------------------------------#
    if update.text.startswith("magnet:?"):
        await msg.edit("⚠️ I am not a magnet link downloader\n\n")
        return

    if "mega.nz" in update.text:
        await msg.edit(
            "⚠️ I don't support mega.nz links\n\n👉 Send me Direct link or YouTube link"
        )
        return

    # if "seeder.cc" in update.text:
    #    await msg.edit("⚠️ I don't support seeder links\n\n👉 Send me Direct link or YouTube link")
    #    return

    if "mediafire.com" in update.text:
        aaa = "✶ **MediaFireDL File:** For Link endwith File and Something Like this **Ex:** `https://www.mediafire.com/file/ia9ryxh9k7006fs/Detailed-Notification-IBPS-Clerk-XII-Posts.pdf/file`"
        bbb = "\n\n✶ **MediaFire DL CLI:** For Downloading via CLI Command line Interface \n\n✶ **MediaFire Downloader YTDL :** __For Downloading via YTDL__\n\n**Note :-** (MediaFire Downloader YTDL) and (MediaFire DL CLI) Upload Only New-Generated-MediaFire Links."
        ccc = "\n\nNow Select Option According to your link 👇"
        await msg.edit(
            f"{aaa}{bbb}{ccc}",
            reply_markup=Baby.MEDIAFIRE_DL,
        )
        logger.info(
            f"MediaFire URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
        )
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                )
            except Exception as e:
                print(e)
        return

    if "spotify.com" in update.text:
        await msg.edit(
            "**Spotify Songs Downloader :** __For Downloading Spotify Links__\n\nSelect your appropriate action 👇",
            reply_markup=Baby.SPOTIFY,
        )
        logger.info(
            f"spotify URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
        )
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                )
            except Exception as e:
                print(e)
        return

    if "drive.google.com" in update.text:
        await msg.edit(
            "**Google Drive Downloader :** __For Downloading Google Drive Folder/File/Video/Photo/Archive etc.__\n\n**Note :** __Supports downloading from Google Drive (about 50 files/day)__\n\nYou can Also Download files over 2 GB.\n\n**Extract Archive:** For Extracting Archive Files. (Unzip/Unrar)\n\nSelect your appropriate action 👇",
            reply_markup=Baby.GOOGLE_DRIVE,
        )
        logger.info(
            f"Google Drive URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
        )
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                )
            except Exception as e:
                print(e)
        return

    if "youtu" in update.text:
        text_url = update.text.split(None, 1)[0]
        if "playlist?list=" in text_url:
            await msg.edit(
                f"**YouTube Playlist Downloader :** __For Downloading YouTube Playlist Video__\n\n**Note :- ** __To Reduce overload, Maxx Playlist Length Support upto **{Config.PMAX_LENGTH}**.__\n\nOr, you can use @YoutubePlaylistDLBot\n\nSelect your appropriate action 👇",
                reply_markup=Baby.YT_PLAYLIST,
            )
            logger.info(
                f"YouTube Playlist Link 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
            )
            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                    )
                except Exception as e:
                    print(e)
            return

        await msg.edit(
            "🎵 **YouTube Music :** __For Downloading Songs in High/Low Quality from YouTube__\n\n🔗 **Make Download/Stream Link :** __Generated link will Play/Download in Browser__\n\nSelect your appropriate action 👇",
            reply_markup=Baby.YT_MUSIC,
        )
        logger.info(
            f"YouTube URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}"
        )
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                )
            except Exception as e:
                print(e)
        return

    # ----------- Only URL Uploader---------------#
    if Config.ONLY_URL_UPLOADER.upper() == "YES":
        await msg.edit(
            "🔗 **URL Uploader :** Upload Link to File\n\nSelect your appropriate action 👇",
            reply_markup=Baby.URL_UPLOADER,
        )
        logger.info(f"URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}")
        if Config.LOG_CHANNEL:
            try:
                cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                await cmf2v.reply_text(
                    f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
                )
            except Exception as e:
                print(e)
        return
    # -------------------------------------------#

    await msg.edit(
        "🎵 **Audio :** For Audio Functions\n\n🎥 **Video :** For Video Functions\n\n**Extract Archive :** For Extracting Zip/Rar/7z etc.\n\n🔗 **Make Download/Stream Link :** Generated link will Play/Download in Browser\n\nSelect your appropriate action 👇",
        reply_markup=Baby.MAIN_BUTTONS,
    )
    logger.info(f"URL 🔗 sent by User {user_first} {str(user_id)} @{user_name}")
    if Config.LOG_CHANNEL:
        try:
            cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
            await cmf2v.reply_text(
                f"**User Information** :\n\n🌷 **First Name :** `{user_first}`\n\n🌷 **User Id :** `{user_id}`\n\n🌷 **User Name :** `@{user_name}`\n\nUsed Filters Regex http"
            )
        except:
            pass

    if update.from_user.id in Config.AUTH_USERS:
        await update.reply(
            "URL Uploader for owner 👇",
            reply_markup=Baby.FOR_ME,
            reply_to_message_id=update.id,
        )


@Client.on_callback_query(filters.regex("^caudio"))
async def caudio_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"Select your appropriate action 👇", reply_markup=Baby.AUDIO_FUNCTIONS
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


@Client.on_callback_query(filters.regex("^cvideo"))
async def cvideo_(bot, update):
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"Select your appropriate action 👇", reply_markup=Baby.VIDEO_FUNCTIONS
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)
