import logging

from pyrogram import Client, filters
from pyrogram.types import ForceReply

from config import Config
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

LENGTH_OF_FILE_NAME = """⚠️ **Error **\n\nFile Name Limit Allowed By Telegram is {alimit} Characters.\n\nThe Given File Name Has {num} Characters.\n\nPlease Short Your File Name And Try Again !"""


@Client.on_callback_query(filters.regex("^capremove"))
async def rm_cap(bot, update):
    await update.message.delete()
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    if update.from_user.id not in Config.AUTH_USERS:
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
    try:
        await reply_msg.copy(update.message.chat.id, caption="")
        logger.info(
            f"Successfully Caption Removed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        if Config.LOG_CHANNEL:
            cr = await reply_msg.copy(chat_id=Config.LOG_CHANNEL)
            await cr.reply_text(
                f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used Caption remover ✅"
            )
    except Exception as e:
        print(e)
        await update.message.reply(
            f"⚠️ **Error :** Occurred", reply_to_message_id=reply_msg.id
        )


@Client.on_callback_query(filters.regex("^capadd"))
async def caption_(bot, update):
    await update.message.delete()
    update.message.chat.id
    reply_msg = update.message.reply_to_message
    if update.from_user.id not in Config.AUTH_USERS:
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
    chitranjan_diksha = await bot.ask(
        chat_id=update.message.chat.id,
        text="✶ Send me **Caption** to add\n\n👉 **Caption :** The Texts that are at the bottom of the File\n\n__✶ Or Send /cancel To Stop__",
        reply_markup=ForceReply(True),
        filters=filters.text,
        reply_to_message_id=reply_msg.id,
    )
    #  await chitranjan_diksha.delete()
    await chitranjan_diksha.request.delete()
    file_name = chitranjan_diksha.text
    if file_name.lower() == "/cancel":
        await update.message.reply_text(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        return

    if len(file_name) > 1024:
        await update.message.reply_text(
            LENGTH_OF_FILE_NAME.format(alimit="1024", num=len(file_name)),
            reply_to_message_id=reply_msg.id,
        )
        return

    try:
        await reply_msg.copy(update.message.chat.id, caption=file_name)
        logger.info(
            f"Successfully Caption Added ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )

        if Config.LOG_CHANNEL:
            cad = await reply_msg.copy(chat_id=Config.LOG_CHANNEL, caption=file_name)
            await cad.reply_text(
                f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used Caption Adder ✅"
            )
    except Exception as e:
        print(e)
        await update.message.reply(
            f"⚠️ **Error :** Occurred", reply_to_message_id=reply_msg.id
        )


@Client.on_callback_query(filters.regex("^copyfile"))
async def allcopy_(bot, update):
    await update.message.delete()
    reply_msg = update.message.reply_to_message
    if update.from_user.id not in Config.AUTH_USERS:
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
    try:
        await reply_msg.copy(update.message.chat.id)
        logger.info(
            f"Successfully Forwarded Tag Removed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
        if Config.LOG_CHANNEL:
            cf = await reply_msg.copy(chat_id=Config.LOG_CHANNEL)
            await cf.reply_text(
                f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\nUsed forwarded tag remover ✅"
            )
    except Exception as e:
        print(e)
        await update.message.reply(
            f"⚠️ **Error :** Occurred", reply_to_message_id=reply_msg.id
        )


"""
msg = await client.get_messages(int(chat), int(id))

print(msg.caption)
"""
