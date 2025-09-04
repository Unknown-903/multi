import logging

from pyrogram import Client, filters

logger = logging.getLogger(__name__)


@Client.on_message(filters.private & filters.command("admin"))
async def admin(c, m):
    text_a = "Available admin commands are :\n\n"
    text_b = "➩  /cmds\n\n➩  /paid\n\n➩  /log\n\n➩  /reset\n\n➩  /restart\n\n➩  /status\n\n➩  /broadcast\n\n➩  /ban_user\n\n➩  /unban_user\n\n➩  /banned_users \n\n➩  /set_url\n\n➩  /set_password"
    await m.reply_text(f"{text_a}{text_b}", reply_to_message_id=m.id)
    logger.info(
        f"👦 Admin Command Used By {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
    )


# \n\n➩  /dyno_hours
