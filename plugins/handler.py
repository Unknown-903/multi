import asyncio
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
GB_USERS = []

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Ranjan_:

    SELECT_BUTTON = InlineKeyboardMarkup(
        [
             [
                InlineKeyboardButton("⬆️ Google Drive Uploader", callback_data="updrive"),
             ],
            [
                InlineKeyboardButton("🎥 Compress Video", callback_data="commm"), 
            ],
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
                InlineKeyboardButton(
                    "✏️ Caption And Buttons Editor", callback_data="vvcaption"
                ),
            ],
            [
                InlineKeyboardButton("✂️ Video Trimmer", callback_data="randtrim"),
                InlineKeyboardButton("➕ Video Merger", callback_data="vmerge"),
            ],
            [
                InlineKeyboardButton("🔇 Remove Audio", callback_data="mute_video"),
                InlineKeyboardButton("Merge 🎥 And 🎵", callback_data="video_audio"),
            ],
            [
                InlineKeyboardButton("🎥 Video To GIF", callback_data="gifvideo"),
                InlineKeyboardButton("🎥 Video Optimize", callback_data="reorderst"),
                # InlineKeyboardButton("🎥 Compress Video", callback_data="commm"), # reorderst
            ],
            [
                InlineKeyboardButton("🖼️ Screenshots", callback_data="mvscreenshot"),
                InlineKeyboardButton("🖼️ Manual S-Shots", callback_data="mvshots"),
            ],
            [
                InlineKeyboardButton("🎥 Generate Sample", callback_data="disampl"),
                InlineKeyboardButton("🎵 Video To Audio", callback_data="vidbutmore"),
            ],
            [
                InlineKeyboardButton("🎥 Video Converter", callback_data="vconvertmain"),
                InlineKeyboardButton("✏️ Video Renamer", callback_data="vrenamemain"),
            ],
            [
                InlineKeyboardButton("Media Information", callback_data="real_info"),
                InlineKeyboardButton("📂 Create Archive ", callback_data="archiverpro"),
                #       InlineKeyboardButton("🎥 Video To mp4", callback_data="avi_mp4"),
            ],
            [InlineKeyboardButton("Cancel  ❌", callback_data="cancel_query")],
        ]
    )

    AUDIO_BUTTON = InlineKeyboardMarkup(
        [
            # [
            #    InlineKeyboardButton("⬆️ Google Drive Uploader", callback_data="updrive"),
            # ],
            [
                InlineKeyboardButton(
                    "✏️ Caption & Buttons Editor", callback_data="aacaption"
                ),
            ],
            [
                InlineKeyboardButton("🎵 Slowed & Reverb", callback_data="psox"),
                InlineKeyboardButton("🎵 Audio Converter", callback_data="allaudfunc"),
            ],
            [
                #       InlineKeyboardButton("🎵 Karaoke Maker", callback_data="akaraoke"), # aspliter akaraoke
                InlineKeyboardButton("📂 Create Archive ", callback_data="archiverpro"),
                InlineKeyboardButton("➕ Audio Merger", callback_data="amerget"),
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
                InlineKeyboardButton("✏️ Rename Audio", callback_data="renamaud"),
                InlineKeyboardButton("✍️ Mp3 Tag Editor", callback_data="tagmp3"),
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

    A_BUTTON_MORE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎵 Convert To Audio", callback_data="choosbelow"
                ),  # undifineaud
            ],
            [
                InlineKeyboardButton("AC3", callback_data="acaudio3"),
                InlineKeyboardButton("MP3", callback_data="mpthreege"),
            ],
            [
                InlineKeyboardButton("WAV", callback_data="wav_audio"),
                InlineKeyboardButton("FLAC", callback_data="flac_audio"),
            ],
            [
                InlineKeyboardButton("OGG", callback_data="ogg_audio"),
                InlineKeyboardButton("OPUS", callback_data="opus_audio"),
            ],
            [
                InlineKeyboardButton("AAC", callback_data="acc_audio"),
                InlineKeyboardButton("M4A", callback_data="madio4a"),
            ],
            [
                InlineKeyboardButton("AIFF", callback_data="finfrast"),
                InlineKeyboardButton("WMA", callback_data="wmaaud"),
            ],
            [InlineKeyboardButton("CANCEL", callback_data="cancel_query")],
        ]
    )

    VID_BUT_MORE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎵 Convert To Audio", callback_data="choosbelow"),
            ],
            [
                InlineKeyboardButton("AC3", callback_data="acaudio3"),
                InlineKeyboardButton("MP3", callback_data="mpthreege"),
            ],
            [
                InlineKeyboardButton("WAV", callback_data="wav_audio"),
                InlineKeyboardButton("FLAC", callback_data="flac_audio"),
            ],
            [
                InlineKeyboardButton("OGG", callback_data="ogg_audio"),
                InlineKeyboardButton("OPUS", callback_data="opus_audio"),
            ],
            [
                InlineKeyboardButton("AAC", callback_data="acc_audio"),
                InlineKeyboardButton("M4A", callback_data="madio4a"),
            ],
            [
                InlineKeyboardButton("AIFF", callback_data="finfrast"),
                InlineKeyboardButton("WMA", callback_data="wmaaud"),
            ],
            [InlineKeyboardButton("CANCEL", callback_data="cancel_query")],
        ]
    )

    DOCUMENT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏️ File Renamer", callback_data="renamerf"),
            ],
            [
                InlineKeyboardButton("Create Archive ", callback_data="archiverpro"),
                InlineKeyboardButton("Extract Archive", callback_data="aextract"),
            ],
            # [
            #    InlineKeyboardButton("⬆️ Google Drive Uploader", callback_data="updrive"),
            # ],
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
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )

    ONLY_COMPRESSOR = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎥 Compress Video", callback_data="commm"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
        ]
    )


@Client.on_callback_query(filters.regex("^choosbelow"))
async def auodate_ch(bot, update):
    try:
        await update.answer(f"Select the button below 👇", show_alert=True)
    except Exception as e:
        print(e)


@Client.on_callback_query(filters.regex("^finfrast"))
async def infrea(bot, update):
    try:
        await update.answer(
            f"⚠️ Currently Removed this Option!!!\n\nPlz Select the Another Option",
            show_alert=True,
        )
    except Exception as e:
        print(e)


@Client.on_message(
    filters.incoming & filters.private & filters.media
)  # & filters.user(Config.AUTH_USERS)
async def video_filter_(bot, update):
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Functions", callback_data="function"),
                InlineKeyboardButton("Instructions", callback_data="instruct"),
            ],
            [InlineKeyboardButton("Pay Now", url="https://te.legra.ph/Payment-07-06")],
        ]
    )
    user_id = update.from_user.id
    logger.info(
        f"👉 Sent A File 👈 By User {update.from_user.id} @{update.from_user.username}"
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
                "**⚠️ Sorry You're Banned❗**\n\nFor help message @Legend_Shivam_7"
            )
            return
    except:
        await update.reply("⚠️ First Click on /start, Then try again")
        return

    # -------- Starting Media Filtration-------#
    if update.media:
        if update.photo:
            try:
                ab = await update.reply_text(
                    "**Processing....**", reply_to_message_id=update.id
                )
            except Exception as e:
                print(e)
                return
            try:
                await db.set_thumbnail(
                    update.from_user.id, thumbnail=update.photo.file_id
                )
            except Exception as e:
                print(e)
                return
            try:
                await ab.edit(
                    text="Thumbnail Saved Successfully ✅",
                )
            except Exception as e:
                print(e)
                return
            logger.info(
                f" Thumbnail Saved Successfully ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        if update.from_user.id not in Config.AUTH_USERS:
            for_media = Config.OWNER_ID
            if (await db.get_mediafunctions(id=for_media)) is False:
                await update.reply(
                    "⚠️ Media Functions Currently Disabled",
                    reply_to_message_id=update.id,
                )
                return

        if update.from_user.id not in Config.AUTH_USERS:
            if update.from_user.id not in Config.VERIFIED_USERS:
                if len(COUNT) > Config.NUMBER:
                    await update.reply(
                        f"**⚠️ Already {Config.NUMBERS}/{Config.NUMBERS} Process Running**\n\n👉 Bot is Overloaded. So, Try after a few minutes.\n\nIntrested users can Upgrade to Paid bot, To avoid Waiting Time and Process limits. @MultiUsageBot (Paid Bot)",
                        reply_to_message_id=update.id,
                    )
                    return

        if update.from_user.id not in Config.AUTH_USERS:
            if update.from_user.id not in Config.VERIFIED_USERS:
                if Config.TIME_GAP:
                    time_gap = await timegap_check(update)
                    if time_gap:
                        if Config.PAID_BOT.upper() != "YES":
                            await update.reply(
                                f"Interested users can Upgrade to Paid bot, To avoid Waiting Time and Process limits. (Paid Bot) at 30Rs Per month",
                                reply_to_message_id=update.id,
                            )
                        return
                    Config.TIME_GAP_STORE[update.from_user.id] = time.time()

        media = update
        filetype = media.document or media.video or media.audio

        try:
            recogniser_ = filetype.mime_type
        except Exception as e:
            return await update.reply(
                f"⚠️ **Error** : {e}", reply_to_message_id=update.id
            )

        if recogniser_ is None:
            return await update.reply(
                "⚠️ File type not recognised", reply_to_message_id=update.id
            )

        media_file = update.video or update.audio or update.document
        media_file.file_size
        #   if FILE_SIZE >= (1 * 1024 * 1024 * 1024): # 1 GB
        #       GB_USERS.append(update.from_user.id)
        #       COUNTER_GB_USERS = GB_USERS.count(update.from_user.id)
        #       if COUNTER_GB_USERS >= 4:
        #           return await update.reply(f"⚠️ You used 1 GB limit (3/3)\n\n👉 So, Now send below than 1 GB", reply_to_message_id=update.message_id)
        #       await update.reply(f"⚠️ You are working with more than 1 GB file\n\n👉 Free Users has Limit ({COUNTER_GB_USERS}/3) for more than 1 GB files", reply_to_message_id=update.message_id)

        if filetype.mime_type.startswith("audio/"):
            try:
                msg = await update.reply(
                    "**Processing....**", reply_to_message_id=update.id
                )
            except Exception as e:
                print(e)
                return
            download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
            if os.path.isdir(download_path):
                return await msg.edit(
                    "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__"
                )
            try:
                await msg.edit(
                    f"✶ If you want New Name in Output Audio, Then Activate ✅ **Rename File**.\n\n✶ Your File will be Uploaded as {'🔊 **Audio**' if (await db.get_upload_as(id=user_id)) is True else '📁 **Document**'}  (You can Change it in /settings)\n\n**Choose your appropriate action 👇**",
                    reply_markup=Ranjan_.AUDIO_BUTTON,
                )
            except Exception as e:
                print(e)

            logger.info(
                f"Audio 🔊 sent by User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            if Config.LOG_CHANNEL:
                try:
                    cmfaudio = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmfaudio.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Filters Audio"
                    )
                except Exception as e:
                    print(e)
            return

        if filetype.mime_type.startswith("video/"):
            try:
                msg = await update.reply(
                    "**Processing....**", reply_to_message_id=update.id
                )
            except Exception as e:
                print(e)
                return
            download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
            if os.path.isdir(download_path):
                return await msg.edit(
                    "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__"
                )
            try:
                await msg.edit(
                    f"✶ If you want New Name in Output video, Then Activate ✅ **Rename File**.\n\n✶ Your File will be Uploaded as {'🎥 **Video**' if (await db.get_asvideos(id=user_id)) is True else '📁 **Document**'}  (You can change it in /settings)\n\n**Choose your appropriate action 👇**",
                    reply_markup=Ranjan_.SELECT_BUTTON,
                )
            except Exception as e:
                print(e)
            logger.info(
                f"File 🗃️ sent by User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Filters Video"
                    )
                except Exception as e:
                    print(e)
            # For owner
            """
            if update.from_user.id in Config.AUTH_USERS:
                try:
                    await update.reply(
                        f"✶ **Choose your appropriate action 👇**",
                        reply_markup=Ranjan_.ONLY_COMPRESSOR,
                        reply_to_message_id=update.id,
                    )
                except Exception as e:
                    logger.info(
                        f"Error: {e} User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                    )
            """
        else:
            try:
                msg = await update.reply(
                    "**Processing....**", reply_to_message_id=update.id
                )
            except Exception as e:
                print(e)
                return
            download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
            if os.path.isdir(download_path):
                return await msg.edit(
                    "⚠️ Please wait untill the previous task complete\n\n__✶ If you want Force Use, Then first clear your previous task from server__\n\n__✶ Use command **/force_use**__"
                )
            try:
                await msg.edit(
                    f"✶ __Your File will be Uploaded as__ {'🎥 **Video**' if (await db.get_asvideos(id=user_id)) is True else '📁 **Document**'}  (__Change it in__ /settings)\n\n**Create Archive :** Make Archive (zip, rar, 7z)\n\n**Extract Archive :** Extract Archive (Unzip) zip, rar etc Almost all Archive.\n\n**Choose your appropriate action 👇**",
                    reply_markup=Ranjan_.DOCUMENT_BUTTONS,
                )
            except Exception as e:
                print(e)

            logger.info(
                f"File 🗃️ sent by User {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )

            if Config.LOG_CHANNEL:
                try:
                    cmf2v = await update.copy(chat_id=Config.LOG_CHANNEL)
                    await cmf2v.reply_text(
                        f"**User Information** :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed Filters Else Documents"
                    )
                except Exception as e:
                    print(e)


# ----------------- For Audio ----------------#
@Client.on_callback_query(filters.regex("^allaudfunc"))
async def audp_more_mp3(bot, update):
    mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"✶ Now Audio Quality will convert to Bit-Rate **{mainquality_audio} kbps**"
            f"\n\nYou can customise **Bit-Rate (Audio Quality)** in /settings"
            f"\n\n✶ **Note :** __Bit-Rate won't change in Lossless codecs ex. WAV & FLAC__"
            f"\n\n✶ **Note :** __Output WMA audio does not play in Telegram. __",
            reply_markup=Ranjan_.A_BUTTON_MORE,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# ------------------- For Video ---------------#
@Client.on_callback_query(filters.regex("^vidbutmore"))
async def vidbutmor(bot, update):
    update.from_user.id
    mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"✶ Now Audio Quality will convert to Bit-Rate **{mainquality_audio} kbps**"
            f"\n\nYou can customise **Bit-Rate (Audio Quality)** in /settings"
            f"\n\n✶ **Note :** __Bit-Rate won't change in Lossless codecs ex. WAV & FLAC__"
            f"\n\n✶ **Note :** __Output WMA audio does not play in Telegram. __",
            reply_markup=Ranjan_.VID_BUT_MORE,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# ------------ Video Back To Main ------------#
@Client.on_callback_query(filters.regex("^vmainback"))
async def vmainback(bot, update):
    user_id = update.from_user.id
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"✶ If you want New Name in Output video. Then Activate ✅ **Rename File**.\n\n✶ Your File will be Uploaded as {'🎥 **Video**' if (await db.get_asvideos(id=user_id)) is True else '📁 **Document**'}  (You can change it in /settings)\n\n**Choose your appropriate action 👇**",
            reply_markup=Ranjan_.SELECT_BUTTON,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


# ------------ Audio Back To Main ------------#
@Client.on_callback_query(filters.regex("^amainback"))
async def amainback(bot, update):
    user_id = update.from_user.id
    try:
        await update.answer()
    except:
        pass
    try:
        await update.message.edit(
            f"✶ If you want New Name in Output Audio. Then Activate ✅ **Rename File**.\n\n✶ Your File will be Uploaded as {'🔊 **Audio**' if (await db.get_upload_as(id=user_id)) is True else '📁 **Document**'}  (You can Change it in /settings)\n\n**Choose your appropriate action 👇**",
            reply_markup=Ranjan_.AUDIO_BUTTON,
        )
    except MessageNotModified:
        pass
    except Exception as err:
        print(err)


@Client.on_callback_query(filters.regex("^cancel_query"))
async def cancellls(bot, update):
    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if not os.path.isdir(download_path):
        if update.from_user.id not in Config.AUTH_USERS:
            try:
                del Config.TIME_GAP_STORE[update.from_user.id]
            except Exception as e:
                logger.info(
                    f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )

    try:
        await update.message.edit(text="__Trying To Cancel....__")
        await asyncio.sleep(0.6)
        await update.message.edit("**Process Cancelled  ✅**")
    except:
        try:
            await update.message.edit("**Process Cancelled  ✅**")
        except:
            pass
