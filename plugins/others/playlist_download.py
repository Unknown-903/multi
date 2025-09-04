import asyncio
import json
import logging
import math
import os

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import Config
from database.database import Database
from helpers.display_progress import humanbytes
from plugins.audio import CANCEL_PROCESS, COUNT, delete_msg, msg_edit, pl_server_clear

db = Database()

logger = logging.getLogger(__name__)

from plugins.others.playlist_uploader import cli_call, playlist_uploader

dl_msg = None
request_length = 0


def remove_space(string):
    return string.replace(" ", "")


@Client.on_callback_query(filters.regex("^yplaylist"))
async def zyplayist_(bot, update):
    global dl_msg, request_length
    try:
        await update.message.delete()
    except:
        pass
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    user_id = update.from_user.id
    ab = None
    bc = None
    cd = None
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

    #  if user_id in COUNT:
    #      ab = await bot.send_message(
    #          chat_id=update.message.chat.id,
    #          text="Already Your 1 Request Processing",
    #          reply_to_message_id=reply_msg.id
    #      )
    #      return

    url = reply_msg.text.strip()
    try:
        url = remove_space(url)
        print(url)
    except:
        pass
    if not "playlist?list=" in url:
        await update.message.reply(
            "⚠️ It's not a playlist link", reply_to_message_id=reply_msg.id
        )
        return

    ab = await bot.send_message(
        update.message.chat.id,
        "**Processing....**",
        reply_to_message_id=reply_msg.id,
    )
    # --no-warnings
    cmd = f"yt-dlp -i --flat-playlist --dump-single-json {url}"

    try:
        out, err = await asyncio.wait_for(cli_call(cmd), 600)
    except asyncio.TimeoutError:
        await ab.edit("⚠️ Processing time exceeded.")
        return

    try:
        playlist_data = json.loads(out)
        entities = playlist_data.get("entries")
        playlist_length = len(entities)
        if playlist_length <= 0:
            await ab.edit(
                "Cannot load the videos from this playlist. It shuold be a public or unlisted youtube playlist."
            )
            return
    except:
        await ab.edit("⚠️ Failed to fetch the playlist")
        return

    try:
        await ab.delete()
    except:
        pass

    # ----------------- Format Buttons ------------#
    FORMAT_BUTTONS = ReplyKeyboardMarkup(
        [
            ["🎬 144p", "🎬 240p", "🎬 360p"],
            ["🎬 480p", "🎬 720p", "🎬 1080p"],
            ["🎵 Best Audios", "🎬 Best Videos"],
            ["🎵 Mp3 128k", "🎵 Mp3 192k", "🎵 Mp3 320k"],
            ["Cancel"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_format = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Found {playlist_length} videos in the playlist**\n\nNow select Quality in Below keyboard\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=FORMAT_BUTTONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        # await ask_format.delete()
        await ask_format.request.delete()
        selected_format = ask_format.text
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out, ReSend your link",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    type_formats = None
    if selected_format == "🎬 144p":
        type_formats = "pvideos"
        vformat = "144"
    elif selected_format == "🎬 240p":
        type_formats = "pvideos"
        vformat = "240"
    elif selected_format == "🎬 360p":
        type_formats = "pvideos"
        vformat = "360"
    elif selected_format == "🎬 480p":
        type_formats = "pvideos"
        vformat = "480"
    elif selected_format == "🎬 720p":
        type_formats = "pvideos"
        vformat = "720"
    elif selected_format == "🎬 1080p":
        type_formats = "pvideos"
        vformat = "1080"
    elif selected_format == "🎬 Best Videos":
        type_formats = "pvideos"
        vformat = "Best_Videos"
    elif selected_format == "🎵 Best Audios":
        type_formats = "paudios"
        aformat = "best"
    elif selected_format == "🎵 Mp3 128k":
        type_formats = "paudios"
        aformat = "128k"
    elif selected_format == "🎵 Mp3 192k":
        type_formats = "paudios"
        aformat = "192k"
    elif selected_format == "🎵 Mp3 320k":
        type_formats = "paudios"
        aformat = "320k"
    elif selected_format == "Cancel":
        type_formats = "Cancel"
    else:
        type_formats = "Cancel"

    if type_formats == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        #    await clear_server(user_id)
        return

    # --------------------------------------------#
    CHOICE_BUTTONS = ReplyKeyboardMarkup(
        [["Default"], ["Specific Range"], ["Custom Specific Range"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        ask_choice = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text=f"**Found {playlist_length} videos in the playlist**\n\n✶ Currently Bot supports to upload Upto **{Config.PMAX_LENGTH}** at a time.\n\n**Playlist Upload Modes Are** 👇\n\n**(1). Default :** __Upto {Config.PMAX_LENGTH} Videos, Ex.1-{Config.PMAX_LENGTH}__\n\n**(2). Specific Range :** __Ex. 21-30, Then 10 Videos will upload 21-30 of playlist__\n\n**(3). Custom Specific Range :** __You can choose videos of playlist. Ex. 2,6,8,9 Then 4 video will upload 2, 6, 8, 9 of playlist__\n\n**Select the Playlist Upload Mode **👇",
                reply_markup=CHOICE_BUTTONS,
                filters=filters.text,
                reply_to_message_id=reply_msg.id,
            ),
            600,
        )
        #  await ask_choice.delete()
        await ask_choice.request.delete()
        ask_choice = ask_choice.text
    except asyncio.TimeoutError:
        try:
            await update.message.reply(
                "⚠️ Process Time Out, ReSend your link",
                reply_markup=ReplyKeyboardRemove(),
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
        logger.info(
            f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if ask_choice == "Default":
        asked_choice = "Default"
    elif ask_choice == "Specific Range":
        asked_choice = "Specific_Range"
    elif ask_choice == "Custom Specific Range":
        asked_choice = "Custom_Specific_Range"
    elif ask_choice == "Cancel":
        asked_choice = "Cancel"
    else:
        asked_choice = "Cancel"

    if asked_choice == "Cancel":
        await update.message.reply(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        logger.info(
            f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if asked_choice == "Default":
        if user_id not in Config.AUTH_USERS:
            if playlist_length > Config.PMAX_LENGTH:  # limit max videos
                await update.message.reply(
                    f"⚠️ Playlist length max {Config.PMAX_LENGTH} videos allowed as of now. This has {playlist_length}\n\n👉 So, You can Download by using **Specific Range**",
                    reply_to_message_id=reply_msg.id,
                )
                asked_choice = "Specific_Range"

    if asked_choice == "Specific_Range":
        SRANGE_BUTTONS = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            srange_ask = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"Found {playlist_length} videos in the playlist\n\n**Specific Range :** You can Choose Range of playlist\n\nNow send Range of Playlist ex. `11-15` Then 5 videos will upload `11-15` of playlist",
                    reply_markup=SRANGE_BUTTONS,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                600,
            )
            #  await srange_ask.delete()
            await srange_ask.request.delete()
            srange_ask = srange_ask.text
        except asyncio.TimeoutError:
            try:
                await update.message.reply(
                    "⚠️ Process Time Out, ReSend your link",
                    reply_markup=ReplyKeyboardRemove(),
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass
            logger.info(
                f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        if srange_ask == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        try:
            start_point, end_point = srange_ask.split("-")
        except Exception as e:
            print(e)
            await update.message.reply(
                f"⚠️ Wrong value entered!\n\n👉 Use `-` to separate value, Ex.`11-15`",
                reply_to_message_id=reply_msg.id,
            )
            return

        if int(end_point) > int(playlist_length):
            await update.message.reply(
                f"⚠️ End Range {end_point} is greater than Playlist Length {playlist_length}\n\n👉 So, Enter a number less than Playlist Length.",
                reply_to_message_id=reply_msg.id,
            )
            return

        if int(start_point) > int(playlist_length):
            await update.message.reply(
                f"⚠️ Start Range {start_point} is greater than Playlist Length {playlist_length}\n\n👉  So, Enter a number less than Playlist Length.",
                reply_to_message_id=reply_msg.id,
            )
            return

        if int(start_point) > int(end_point):
            await update.message.reply(
                f"⚠️ Start Range {start_point} is greater Than End range {end_point}\n\n👉  So, Enter Start Range less than End Range, Ex.`12-18`",
                reply_to_message_id=reply_msg.id,
            )
            return

        try:
            plimit = int(end_point) - int(start_point)
        except Exception as e:
            print(e)
            await update.message.reply(
                f"⚠️ Error : {e}\n\n👉 You are doing wrong",
                reply_to_message_id=reply_msg.id,
            )
            return

        if user_id not in Config.AUTH_USERS:
            if plimit > Config.PMAX_LENGTH:
                await update.message.reply(
                    f"⚠️ You are Entered for more than {Config.PMAX_LENGTH} Files\n\n👉 So, Enter for less than {Config.PMAX_LENGTH} files\n\n👉 Or, you can use @YoutubePlaylistDLBot",
                    reply_to_message_id=reply_msg.id,
                )
                return

        number_srlimit = plimit + int(1)
    #####-------------------
    if asked_choice == "Custom_Specific_Range":
        CS_RANGE = ReplyKeyboardMarkup(
            [["Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            cs_range = await asyncio.wait_for(
                bot.ask(
                    chat_id=update.message.chat.id,
                    text=f"**Found {playlist_length} videos in the playlist**\n\n✶ **Custom Specific Range :** You can choose videos of playlist. Ex. `2,6,8,9` Then 4 video will upload 2, 6, 8, 9 of playlist\n\nNow send place value of video with separated by comma(,)",
                    reply_markup=CS_RANGE,
                    filters=filters.text,
                    reply_to_message_id=reply_msg.id,
                ),
                600,
            )
            # await cs_range.delete()
            await cs_range.request.delete()
            cs_range = cs_range.text
        except asyncio.TimeoutError:
            try:
                await update.message.reply(
                    f"⚠️ Process Time Out, ReSend your link",
                    reply_markup=ReplyKeyboardRemove(),
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass
            logger.info(
                f"⚠️ Process Time Out For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        if cs_range == "Cancel":
            await update.message.reply(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            logger.info(
                f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
            return

        try:
            raw_user_input = [int(i.strip()) for i in cs_range.split(",")]
        except Exception as e:
            print(e)
            await update.message.reply(
                f"⚠️ Error : {e}", reply_to_message_id=reply_msg.id
            )
            return

        valid_positions = []
        invalid_positions = []

        for pos in raw_user_input:
            if 0 > pos > duration:
                invalid_positions.append(str(pos))
            else:
                valid_positions.append(pos)

        if user_id not in Config.AUTH_USERS:
            if len(valid_positions) > Config.PMAX_LENGTH:
                await update.message.reply(
                    text=f"⚠️ **Limit Exceeded** : Send number of videos less than {Config.PMAX_LENGTH}\n\n👉 You sent for {len(valid_positions)} videos\n\n👉 Or, you can use @YoutubePlaylistDLBot",
                    reply_to_message_id=reply_msg.id,
                )
                return
        custom_range = cs_range
        number_csv = len(valid_positions)
    # ---------------------------------------------#

    output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
    if not os.path.exists(output_folder):  # os.path.isdir
        os.makedirs(output_folder)

    COUNT.append(user_id)

    if asked_choice == "Default":
        download_message = f"Playlist Length : {playlist_length} Files\nUpload Mode : Default\n\n{playlist_length} Files are Downloading...."
        requested_length = f"{playlist_length}"
        if type_formats == "paudios":
            if aformat == "best":
                final_cmd = f"yt-dlp -i --ignore-errors --extract-audio --add-metadata --audio-format {aformat} --audio-quality 0 -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --ignore-errors --extract-audio --add-metadata --audio-format mp3 --audio-quality {aformat} -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"

        if type_formats == "pvideos":
            if vformat == "Best_Videos":
                final_cmd = f"yt-dlp -i --ignore-errors --continue --no-warnings --prefer-ffmpeg -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --ignore-errors --continue --no-warnings --prefer-ffmpeg -S 'ext,height:{vformat}' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"  # --embed-subs

    if asked_choice == "Specific_Range":
        download_message = f"Playlist Length : {playlist_length} Files\nUpload Mode : Specific Range\nPlaylist Range : {start_point}-{end_point}\n\n{number_srlimit} Files are Downloading...."
        requested_length = f"{number_srlimit}"
        if type_formats == "paudios":
            if aformat == "best":
                final_cmd = f"yt-dlp -i --playlist-start {start_point} --playlist-end {end_point} --ignore-errors --extract-audio --add-metadata --audio-format {aformat} --audio-quality 0 -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --playlist-start {start_point} --playlist-end {end_point} --ignore-errors --extract-audio --add-metadata --audio-format mp3 --audio-quality {aformat} -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"

        if type_formats == "pvideos":
            if vformat == "Best_Videos":
                final_cmd = f"yt-dlp -i --playlist-start {start_point} --playlist-end {end_point} --ignore-errors --continue --no-warnings --prefer-ffmpeg -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --playlist-start {start_point} --playlist-end {end_point} --ignore-errors --continue --no-warnings --prefer-ffmpeg -S 'ext,height:{vformat}' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"

    if asked_choice == "Custom_Specific_Range":
        download_message = f"Playlist Length : {playlist_length} Files\nUpload Mode : Custom Specific Range\n\n{number_csv} Files are Downloading...."
        requested_length = f"{number_csv}"
        if type_formats == "paudios":
            if aformat == "best":
                final_cmd = f"yt-dlp -i --playlist-items {custom_range} --ignore-errors --extract-audio --add-metadata --audio-format {aformat} --audio-quality 0 -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --playlist-items {custom_range} --ignore-errors --extract-audio --add-metadata --audio-format mp3 --audio-quality {aformat} -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"

        if type_formats == "pvideos":
            if vformat == "Best_Videos":
                final_cmd = f"yt-dlp -i --playlist-items {custom_range} --ignore-errors --continue --no-warnings --prefer-ffmpeg -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"
            else:
                final_cmd = f"yt-dlp -i --playlist-items {custom_range} --ignore-errors --continue --no-warnings --prefer-ffmpeg -S 'ext,height:{vformat}' -o '{output_folder}/%(playlist_index)s - %(title)s.%(ext)s' {url}"

    dl_msg = download_message
    request_length = requested_length
    progress_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Progress", callback_data=(f"zplpro"))]]
    )
    bc = await bot.send_message(
        update.message.chat.id,
        f"**Playlist Downloading....**",
        reply_markup=progress_markup,
        reply_to_message_id=reply_msg.id,
    )

    out, err = await cli_call(final_cmd)
    ofiles = 0
    ofiles = len(os.listdir(output_folder))

    if err and ofiles < 2:
        try:
            await update.message.reply(
                f"Failed to download the videos `{err}`",
                reply_to_message_id=reply_msg.id,
            )
        except:
            pass
    else:
        if err:
            try:
                await update.message.reply(
                    "Some videos from this have Errored in download. May be Deleted, Hiden etc.\n\nUploading which are successfull.",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass

    if ofiles < 1:
        await pl_server_clear(user_id, output_folder)
        await msg_edit(
            bc,
            f"⚠️ **Failed** to Download Playlist\n\n👉 May be videos are Hidden, Deleted, Or Wrong Input, etc.",
        )
        logger.info(
            f"⚠️ Failed to download url For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    if getFolderSize(output_folder) < 25:  # if folder size will less than 25kb
        await pl_server_clear(user_id, output_folder)
        await msg_edit(
            bc,
            f"⚠️ **Failed** To Download Playlist\n\n👉 May be videos are Hidden, Deleted, Or Wrong Input, etc.",
        )
        logger.info(
            f"⚠️ Failed to download url For {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        return

    await delete_msg(bc)
    try:
        cance_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Cancel",
                        callback_data=(
                            f"progcancel/{update.message.chat.id}/{reply_msg.id}/{update.from_user.id}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        cd = await update.message.reply(
            f"**{ofiles} Files Are Uploading....**",
            reply_markup=cance_markup,
            reply_to_message_id=reply_msg.id,
        )
    except:
        try:
            cd = await update.message.reply(
                f"**Files Are Uploading....**", reply_to_message_id=reply_msg.id
            )
        except Exception as e:
            await pl_server_clear(user_id, output_folder)
            print(e)
            return

    if (
        CANCEL_PROCESS[update.message.chat.id]
        and reply_msg.id in CANCEL_PROCESS[update.message.chat.id]
    ):
        try:
            await cd.edit("Process Cancelled ✅")
            print("Process Cancelled ✅")
        except:
            pass
        await pl_server_clear(user_id, output_folder)
        try:
            dl_msg = None
            request_length = 0
        except:
            pass
        return

    try:
        files_folder = sorted(list_files(output_folder, []))
    except Exception as e:
        await pl_server_clear(user_id, output_folder)
        print(e)
        try:
            dl_msg = None
            request_length = 0
        except:
            pass
        await cd.edit(f"⚠️ **Error :** {e}")
        return
    premium_upload = "Yes"
    captions = None
    numbers = 0
    for i, single_file in enumerate(files_folder):
        if os.path.exists(single_file):
            try:
                await playlist_uploader(
                    bot, update, single_file, selected_format, captions, premium_upload
                )
                numbers = f"{i+1}"
            except Exception as e:
                try:
                    await update.message.reply(
                        f"⚠️ **Error :** {single_file}\n\nFor File : __{single_file}__",
                        reply_to_message_id=reply_msg.id,
                    )
                    print(e)
                except:
                    pass
                continue
    await delete_msg(cd)
    try:
        dl_msg = None
        request_length = 0
    except:
        pass

    await pl_server_clear(user_id, output_folder)
    if int(numbers) >= int(request_length):
        if int(numbers) == 1:
            texts = f"**{numbers}** Video is Uploaded ✅"
        else:
            texts = f"Total **{numbers}** Videos are Uploaded ✅"
        await bot.send_message(
            update.message.chat.id,
            f"{texts}",
            reply_to_message_id=reply_msg.id,
        )
        logger.info(
            f"Playlist DL, {numbers} Videos are uploaded By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    else:
        return  

# ---------------- Folder Size ----------------#
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


# ---------------- Progress ------------------#
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("zplpro"))
)
async def uzplpro_(bot, update):
    global dl_msg, request_length

    try:
        output_folder = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/"
        requested = int(request_length)
        downloaded = len(os.listdir(output_folder))
        if downloaded > requested:
            downloaded = requested
        dl_size = getFolderSize(output_folder)
        download_size = humanbytes(dl_size)

        total_perc = int(downloaded) * int(100) / requested
        percentage = round(total_perc, 2)
        # ●○
        progressbar = "[{0}{1}]".format(
            "".join(["■" for i in range(math.floor(total_perc / 10))]),
            "".join(["□" for i in range(10 - math.floor(total_perc / 10))]),
        )

        await bot.answer_callback_query(
            callback_query_id=update.id,
            text=f"Total Downloaded : {downloaded} Of {requested}\n\n{progressbar} \n\nPercentage : {percentage}%\n\nDownloaded : {download_size}",
            show_alert=True,
            cache_time=0,
        )
    except Exception as e:
        print(e)


# -------------- List Of Files ----------------#
def list_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return list_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst
