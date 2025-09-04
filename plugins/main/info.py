import logging

logger = logging.getLogger(__name__)
from pyrogram import Client, filters


@Client.on_message(filters.command(["me", "info", "information"]))
async def info(bot, update):
    if (not update.reply_to_message) and (
        (not update.forward_from) or (not update.forward_from_chat)
    ):
        info = user_info(update.from_user)
    elif update.reply_to_message and update.reply_to_message.forward_from:
        info = user_info(update.reply_to_message.forward_from)
    elif update.reply_to_message and update.reply_to_message.forward_from_chat:
        info = chat_info(update.reply_to_message.forward_from_chat)
    elif (update.reply_to_message and update.reply_to_message.from_user) and (
        not update.forward_from or not update.forward_from_chat
    ):
        info = user_info(update.reply_to_message.from_user)
    else:
        return
    try:
        await update.reply_text(text=info, disable_web_page_preview=True, quote=True)
        logger.info(
            f"Command /Info Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    except Exception as error:
        await update.reply_text(error)


def user_info(user):
    text = "--**User Details :**--\n"
    text += f"\n\n**🦚 First Name :** `{user.first_name}`"
    text += f"\n\n**🐧 Last Name :** `{user.last_name}`" if user.last_name else ""
    text += f"\n\n**👤 User Id :** `{user.id}`"
    text += f"\n\n**👦 Username :** @{user.username}" if user.username else ""
    text += f"\n\n**🔗 User Link :** {user.mention}" if user.username else ""
    try:
        user.is_premium
        text += (
            f"\n\n**🌟 Premium User :** {user.is_premium}"
            if user.is_premium
            else f"\n\n**🌟 Premium User :** False"
        )
    except:
        pass
    text += f"\n\n**💬 DC ID :** `{user.dc_id}`" if user.dc_id else ""
    text += f"\n\n**❌ Is Deleted :** True" if user.is_deleted else ""
    text += f"\n\n**🤖 Is Bot :** True" if user.is_bot else ""
    text += f"\n\n**✅ Is Verified :** True" if user.is_verified else ""
    text += f"\n\n**✖️ Is Restricted :** True" if user.is_verified else ""
    text += f"\n\n**💨 Is Scam :** True" if user.is_scam else ""
    text += f"\n\n**👺 Is Fake :** True" if user.is_fake else ""
    text += f"\n\n**🤔 Is Support :** True" if user.is_support else ""
    text += (
        f"\n\n**📃 Language Code :** {user.language_code}" if user.language_code else ""
    )

    text += f"\n\n**💫 Status :** {user.status}" if user.status else ""
    text += f"\n\nIf you need user id, Then just tap and copy. "
    return text


def chat_info(chat):
    text = "--**Chat Details :**--\n"
    text += f"\n\n**Title :** `{chat.title}`"
    text += f"\n\n**Chat ID :** `{chat.id}`"
    text += f"\n\n**Username :** @{chat.username}" if chat.username else ""
    text += f"\n\n**Type :** `{chat.type}`"
    text += f"\n\n**DC ID :** `{chat.dc_id}`"
    try:
        chat.is_premium
        text += (
            f"\n\n**Primium User :** {chat.is_premium}"
            if chat.is_premium
            else f"\n\n**Primium User :** False"
        )
    except:
        pass

    text += f"\n\n**Is Verified :** True" if chat.is_verified else ""
    text += f"\n\n**Is Restricted :** True" if chat.is_verified else ""
    text += f"\n\n**Is Creator :** True" if chat.is_creator else ""
    text += f"\n\n**Is Scam :** True" if chat.is_scam else ""
    text += f"\n\n**Is Fake :** True" if chat.is_fake else ""
    return text
