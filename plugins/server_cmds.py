import asyncio
import logging
import shutil

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.database import Database
from plugins.audio import COUNT

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
FORCE_USE = []


class Diksha_:

    CANCEL_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Yes  ✅", callback_data="clear_files"),
                InlineKeyboardButton("No  ❌", callback_data="cancel_no"),
            ]
        ]
    )

    CHITRANJAN_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Yes  ✅", callback_data="clear_count"),
                InlineKeyboardButton("No  ❌", callback_data="clear_no"),
            ]
        ]
    )

    COUNT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Yes  ✅", callback_data="all_count"),
                InlineKeyboardButton("No  ❌", callback_data="all_no"),
            ]
        ]
    )

    BOTH_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Yes  ✅", callback_data="clear_both"),
                InlineKeyboardButton("No  ❌", callback_data="both_no"),
            ]
        ]
    )

    FORCE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Yes  ✅", callback_data="force_count"),
                InlineKeyboardButton("No  ❌", callback_data="force_no"),
            ]
        ]
    )


@Client.on_message(filters.private & filters.command("force_use"))
async def force_use_lt_(bot, update):
    R_COUNTER = FORCE_USE.count(update.from_user.id)
    try:
        ban_status = await db.get_ban_status(update.from_user.id)
        if ban_status["is_banned"]:
            await bot.send_sticker(
                chat_id=update.chat.id,
                sticker="CAACAgEAAxkBAAECFrdhvdCWEWU-CLXsSot2Dizyn_FkNAAC7wEAAnzn8UWxlVoBHyE2gh4E",
            )
            await update.reply(
                "**⚠️ Sorry You're Banned❗**\n\nFor help Go to @Helps_Group",
                reply_to_message_id=update.id,
            )
            return
    except:
        await update.reply("⚠️ First Click on /start, Then try again")
        return

    if R_COUNTER >= 4:
        await bot.send_message(
            chat_id=update.chat.id,
            text="👉 You are Banned 💔\n\n👉Now Go @Helps_Group for help.",
            reply_to_message_id=update.id,
        )
        return
    if R_COUNTER >= 3:
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"⚠️ Already you have used ({R_COUNTER}/3) times.\n\n⚠️ Again I AM WARNING YOU, Don't use, Otherwise you will be BANNED\n\n**Again Do you want to Force Use ?**",
            reply_markup=Diksha_.FORCE_BUTTONS,
            reply_to_message_id=update.id,
        )
        return
    await update.reply_text(
        text=f"✶ It's an emergency Commmand, If your process is stucked or Always server is busy, Then use\n\n⚠️ You have only ({R_COUNTER}/3) Chance to use this, If you use it for the 4th time you will get BANNED\n\n**Again Do you want to Force Use ?**",
        reply_markup=Diksha_.FORCE_BUTTONS,
        reply_to_message_id=update.id,
    )
    logger.info(
        f"(/force_use) Command /force_use Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_callback_query(filters.regex("^force_count"))
async def forc_usec(bot, update):
    reply_msg = update.message.reply_to_message
    servmsg = await update.message.edit(text="__Processing....__")
    await asyncio.sleep(0.6)
    try:
        try:
            COUNT.remove(update.from_user.id)
            logger.info(f"Force Count Cleared  ✅")
        except:
            pass
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}")
            await update.message.reply(
                text="Cleared Successfully  ✅", reply_to_message_id=reply_msg.id
            )
            FORCE_USE.append(update.from_user.id)
            logger.info(f"Force Server Cleared  ✅")
        except:
            await update.message.reply(
                text="⚠️ Your have nothing in Server",
                reply_to_message_id=reply_msg.id,
            )

        R_COUNTER = FORCE_USE.count(update.from_user.id)
        if R_COUNTER >= 4:
            user_id = int(update.from_user.id)
            ban_duration = int(1)
            ban_reason = (
                "For exceeding the limit (3/3). And you didn't follow the Instruction."
            )
            f"Banning user {user_id} for {ban_duration} day(s) for the reason {ban_reason}."

            await db.ban_user(user_id, ban_duration, ban_reason)
            await bot.send_message(
                user_id,
                f"You are Banned to use this bot\n\n" f"Reason : {ban_reason}",
            )

        #    await asyncio.sleep(15*60)
        #    FORCE_USE.remove(update.from_user.id)
        #    logger.info(f"FORCE_USE count Cleared  ✅")

        await servmsg.delete()
        return
    except Exception as e:
        print(e)
        await servmsg.edit(text="⚠️ **Error**")
        return


@Client.on_message(filters.private & filters.command("cmds"))
async def cmd_cl(c, m):
    await m.reply_text(
        "**Some Basic Commands are** 👇"
        "\n\n/info - To know about self"
        "\n\n/user - To find an user from user_id"
        "\n\n/force_use - Emergency Commmand for users"
        "\n\n/count - To know clear Count in bot"
        "\n\n/clear - To clear the bot server"
        "\n\n/list_count - To clear total list Count"
        "\n\n/clear_both - To clear server & Count"
        "\n\n/process - To know users working in bot"
        "\n\n/process_view - To know user_ids in Count",
        reply_to_message_id=m.id,
        quote=True,
    )
    logger.info(
        f"(/cmds) 🧒 Command /cmds Used by {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
    )


# --- Find User


@Client.on_message(filters.private & filters.command("user"))
async def usr_cl(c, m):
    logger.info(
        f"🧒 Command /user Used by {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
    )
    if len(m.command) == 1:
        await m.reply_text(
            "⚠️ Give user_id with command",
            quote=True,
        )
        return

    try:
        int(m.command[1])
        user = await c.get_users(user_ids=int(m.command[1]))
        detail_text = (
            f"**First Name :** [{user.first_name}](tg://user?id={str(user.id)})\n"
            f"**Username :** `@{user.username}`\n"
        )
        await m.reply_text(
            text=detail_text,
            disable_web_page_preview=True,
            reply_to_message_id=m.id,
        )
        return
    except Exception as e:
        await m.reply_text(
            f"**Error :** {e}",
            quote=True,
        )


# ---- Clear both


@Client.on_message(
    filters.private
    & filters.command(["clear_both", "cb"])
    & filters.user(Config.AUTH_USERS)
)
async def clear_cboh(bot, update):
    logger.info(
        f"🧒 Command /clear_both Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
    if len(update.command) == 1:
        await update.reply_text(
            "⚠️ Give user_id with command",
            quote=True,
        )
        return

    user_id = int(update.command[1])
    try:
        dbab = await update.reply_text(
            text="__Trying To Clear Server...__", reply_to_message_id=update.id
        )
        await asyncio.sleep(0.6)
        try:
            COUNT.remove(user_id)
            await bot.send_message(
                chat_id=update.chat.id,
                text="Successfully Count Cleared  ✅",
                reply_to_message_id=update.id,
            )
            logger.info(f"Successfully Count Cleared  ✅")
        except:
            await bot.send_message(
                chat_id=update.chat.id,
                text="⚠️ Your Count is not on the server",
                reply_to_message_id=update.id,
            )
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
            await bot.send_message(
                chat_id=update.chat.id,
                text="Successfully Server Cleared  ✅",
                reply_to_message_id=update.id,
            )
            logger.info(f"Successfully Server Cleared  ✅")
            await asyncio.sleep(1)
        except:
            await bot.send_message(
                chat_id=update.chat.id,
                text="⚠️ Your process is not on the server",
                reply_to_message_id=update.id,
            )
        await dbab.delete()
        return
    except:
        await dbab.edit("⚠️ You have nothing in the Server")
        return


# --- Users count in server
##########################################
@Client.on_message(
    filters.private
    & filters.command(["process_view", "pv"])
    & filters.user(Config.AUTH_USERS)
)
async def proces_print_files(bot, update):
    REFRESS_BUTTON = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Refresh", callback_data="prview")]]
    )
    try:
        await update.reply_text(
            text=f"Currently Using : **{len(COUNT)}** Users\n\n**Users are**  👇\n\n`{COUNT}`\n\n**Force Users are : {len(FORCE_USE)}** 👇\n\n`{FORCE_USE}`\n\n",
            reply_markup=REFRESS_BUTTON,
            reply_to_message_id=update.id,
        )
    except Exception:
        pass
    logger.info(
        f"(/process_view) Command /process_view Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_callback_query(filters.regex("^prview"))
async def prviews_(bot, update):
    reply_msg = update.message.reply_to_message
    updates_text = f"Processing...."
    try:
        await update.answer(updates_text)
    except:
        pass
    try:
        REFRES_BUTTON = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data="tprview")]]
        )
        await update.message.edit(
            text=f"Currently Using : **{len(COUNT)}** Users\n\n**Users are**  👇\n\n`{COUNT}`\n\n**Force Users are : {len(FORCE_USE)}** 👇\n\n`{FORCE_USE}`\n\n",
            reply_markup=REFRES_BUTTON,
        )
    except:
        try:
            await update.message.delete()
        except:
            pass
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="Try Again /process_view",
            reply_to_message_id=reply_msg.id,
        )
        return


@Client.on_callback_query(filters.regex("^tprview"))
async def tprviewnn_(bot, update):
    reply_msg = update.message.reply_to_message
    updates_text = f"Processing...."
    try:
        await update.answer(updates_text)
    except:
        pass
    try:
        REFRESI_BUTTON = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data="prview")]]
        )
        await update.message.edit(
            text=f"Currently Using : **{len(COUNT)}** Users\n\n**Users are**  👇\n\n`{COUNT}`\n\n**Force Users are : {len(FORCE_USE)}** 👇\n\n`{FORCE_USE}`\n\n",
            reply_markup=REFRESI_BUTTON,
        )
    except:
        try:
            await update.message.delete()
        except:
            pass
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="Try Again /process_view",
            reply_to_message_id=reply_msg.id,
        )
        return


##########################################
@Client.on_message(filters.private & filters.command("process"))
async def proces_files(bot, update):
    REFRESS_BUTTON = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Refresh", callback_data="refress_pro")]]
    )

    users_d = "User"
    if len(COUNT) == 0:
        users_d = "User"
    if len(COUNT) == 1:
        users_d = "User"
    else:
        users_d = "Users"

    try:
        await update.reply_text(
            text=f"Currently Using : **{len(COUNT)}** {users_d}",
            reply_markup=REFRESS_BUTTON,
            reply_to_message_id=update.id,
        )
    except Exception:
        pass
    logger.info(
        f"(/process) Command /process Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_callback_query(filters.regex("^refress_pro"))
async def refress_count_(bot, update):
    reply_msg = update.message.reply_to_message

    users_d = "User"
    if len(COUNT) == 0:
        users_d = "User"
    if len(COUNT) == 1:
        users_d = "User"
    else:
        users_d = "Users"

    alert_text = f"Currently Using : {len(COUNT)} {users_d}"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    try:
        REFRES_BUTTON = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data="refres_pri")]]
        )
        await update.message.edit(
            text=f"Currently Using : **{len(COUNT)}** {users_d}",
            reply_markup=REFRES_BUTTON,
        )
    except:
        try:
            await update.message.delete()
        except:
            pass
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="Try Again /process",
            reply_to_message_id=reply_msg.id,
        )
        return


@Client.on_callback_query(filters.regex("^refres_pri"))
async def refresi_count_(bot, update):
    reply_msg = update.message.reply_to_message

    users_d = "User"
    if len(COUNT) == 0:
        users_d = "User"
    if len(COUNT) == 1:
        users_d = "User"
    else:
        users_d = "Users"

    alert_text = f"Currently Using : {len(COUNT)} {users_d}"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    try:
        REFRESI_BUTTON = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data="refress_pro")]]
        )
        await update.message.edit(
            text=f"Currently Using : **{len(COUNT)}** {users_d}",
            reply_markup=REFRESI_BUTTON,
        )
    except:
        try:
            await update.message.delete()
        except:
            pass
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="Try Again /process",
            reply_to_message_id=reply_msg.id,
        )
        return


# --------------------------------------------#
@Client.on_callback_query()
async def cb_buttonn(bot, update):
    reply_msg = update.message.reply_to_message

    if update.data == "force_no":
        try:
            await update.message.edit(
                "**Ok, I won't go for Force Use**\n\nIt's better than ask for help in @Helps_Group"
            )
        except:
            pass

    elif update.data == "clear_both":
        try:
            dbab = await update.message.edit(text="__Trying To Clear Server...__")
            await asyncio.sleep(0.6)
            try:
                COUNT.remove(update.from_user.id)
                await bot.send_message(
                    chat_id=update.message.chat.id,
                    text="Successfully Count Cleared  ✅",
                    reply_to_message_id=reply_msg.id,
                )
                logger.info(f"Successfully Count Cleared  ✅")
            except:
                await bot.send_message(
                    chat_id=update.message.chat.id,
                    text="⚠️ Your Count is not on the server",
                    reply_to_message_id=reply_msg.id,
                )
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}")
                await bot.send_message(
                    chat_id=update.message.chat.id,
                    text="Successfully Server Cleared  ✅",
                    reply_to_message_id=reply_msg.id,
                )
                logger.info(f"Successfully Server Cleared  ✅")
            except:
                await bot.send_message(
                    chat_id=update.message.chat.id,
                    text="⚠️ Your process is not on the server",
                    reply_to_message_id=reply_msg.id,
                )
            await dbab.delete()
            return
        except:
            try:
                await update.message.edit("⚠️ You have nothing in the Server")
                return await update.answer(
                    "⚠️ You have nothing in the Server", show_alert=True
                )
            except:
                pass

    elif update.data == "clear_files":
        try:
            await update.message.edit(text="__Trying To Cancel....__")
            await asyncio.sleep(0.6)
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}")
            await update.message.edit("Successfully Cleared  ✅")
            logger.info(f"Successfully Cleared  ✅")
        except:
            try:
                await update.message.edit("⚠️ There is nothing to clear")
                return await update.answer(
                    "⚠️ There is nothing to clear", show_alert=True
                )
            except:
                pass

    elif update.data == "clear_count":
        try:
            await update.message.edit(text="__Trying To Clear Count....__")
            COUNT.remove(update.from_user.id)
            await asyncio.sleep(0.6)
            await update.message.edit("Successfully Count Cleared  ✅")
            logger.info(f"Successfully Count Cleared  ✅")
        except:
            try:
                await update.message.edit("⚠️ There is nothing to clear")
                return await update.answer(
                    "⚠️ There is nothing to clear", show_alert=True
                )
            except:
                pass

    elif update.data == "all_count":
        try:
            await update.message.edit(text="__Trying To Clear List Count....__")
            COUNT.clear()
            await asyncio.sleep(0.6)
            await update.message.edit("List Count Cleared  ✅")
            logger.info(f"List Count Cleared  ✅")
        except:
            try:
                await update.message.edit("⚠️ There is nothing to clear")
                return await update.answer(
                    "⚠️ There is nothing to clear", show_alert=True
                )
            except:
                pass

    elif update.data == "both_no":
        await update.message.edit("**Ok, I won't clear both (Count & Server)**")

    elif update.data == "all_no":
        await update.message.edit("**Ok, I won't clear List Count**")

    elif update.data == "clear_no":
        await update.message.edit("**Ok, I won't clear count**")

    elif update.data == "cancel_no":
        await update.message.edit("**Ok, I won't delete your files**")

    elif "closec" in update.data:
        try:
            await update.message.edit_text(text="Closing....")
            await asyncio.sleep(0.3)
            await update.message.edit_text(text="Settings Closed  ✅")
        except:
            pass

    else:
        raise ContinuePropagation


##########################################
################ UseLess #################

# --- Count clear


@Client.on_message(
    filters.private & filters.command("count") & filters.user(Config.AUTH_USERS)
)
async def count_cl(c, m):
    logger.info(
        f"🧒 Command /count Used by {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
    )
    if len(m.command) == 1:
        await m.reply_text(
            "⚠️ Give user_id with command",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        COUNT.remove(user_id)
        await m.reply_text(
            f"Successfully Count removed ✅",
            quote=True,
            reply_to_message_id=m.id,
        )
        return
    except Exception as e:
        await m.reply_text(
            f"**Error :** {e}",
            quote=True,
        )


# ---- Server clear


@Client.on_message(
    filters.private & filters.command("clear") & filters.user(Config.AUTH_USERS)
)
async def clear_cl(c, m):
    logger.info(
        f"🧒 Command /clear Used by {m.from_user.first_name} {str(m.from_user.id)} @{m.from_user.username}"
    )
    if len(m.command) == 1:
        await m.reply_text(
            "⚠️ Give user_id with command",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
        await m.reply_text(
            f"Successfully Cleared ✅",
            quote=True,
            reply_to_message_id=m.id,
        )
        return
    except Exception:
        await m.reply_text(
            f"⚠️ There is nothing to clear",
            quote=True,
            reply_to_message_id=m.id,
        )


# ---- List Count Clear


@Client.on_message(
    filters.private & filters.command("list_count") & filters.user(Config.AUTH_USERS)
)
async def clear_all_list_(bot, update):
    await update.reply_text(
        text="**Do you want to clear List Count from my server ?**",
        reply_markup=Diksha_.COUNT_BUTTONS,
        reply_to_message_id=update.id,
    )
    update.from_user.mention
    logger.info(
        f"(/list_count) Command /list_count Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


# ----- 6 cmds


@Client.on_message(filters.private & filters.command("clear_both6"))
async def clear_both_f(bot, update):
    await update.reply_text(
        text="**Do you want to Clear both ( Count and Server ) from my server ?**",
        reply_markup=Diksha_.BOTH_BUTTONS,
        reply_to_message_id=update.id,
    )
    logger.info(
        f"(/clear_both) Command /clear_both Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_message(filters.private & filters.command("clear6"))
async def clear_files(bot, update):
    await update.reply_text(
        text="**Do you want to delete your files from my server ?**",
        reply_markup=Diksha_.CANCEL_BUTTONS,
    )
    update.from_user.mention
    logger.info(
        f"(/clear) Command /clear Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )


@Client.on_message(filters.private & filters.command("count6"))
async def clear_count_(bot, update):
    await update.reply_text(
        text="**Do you want to clear count from my server ?**",
        reply_markup=Diksha_.CHITRANJAN_BUTTONS,
        reply_to_message_id=update.id,
    )
    update.from_user.mention
    logger.info(
        f"(/count) Command /count Used by {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
