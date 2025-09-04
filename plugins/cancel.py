import logging

from pyrogram import Client, filters

from config import Config
from plugins.audio import CANCEL_PROCESS, clear_server

logger = logging.getLogger(__name__)


@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("progcancel"))
)
async def progress_cancel_(bot, update):
    user_id = update.from_user.id
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )
    updated_data = update.data.split("/")
    chat_id, message_id, from_users = updated_data[1], updated_data[2], updated_data[3]
    if int(update.from_user.id) == int(from_users):
        try:
            await bot.answer_callback_query(
                update.id, text="Trying to Cancel...", show_alert=False
            )
            CANCEL_PROCESS[int(chat_id)].append(int(message_id))
        except:
            pass

    else:
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text="⚠️ **Error**",
            show_alert=True,
            cache_time=0,
        )
    await clear_server(user_id, saved_file_path)
    return


# used in ytdl ---------------
@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("nytcancl"))
)
async def nytcancl(bot, update):
    try:
        await update.message.delete()
    except:
        pass

    user_id = update.from_user.id
    reply_msg = update.message.reply_to_message
    saved_file_path = (
        Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".download.mkv"
    )

    await clear_server(user_id, saved_file_path)
    try:
        await update.message.reply(
            "Process Cancelled ✅",
            reply_to_message_id=reply_msg.id,
        )
    except:
        pass
    logger.info(
        f" Process Cancelled  ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
