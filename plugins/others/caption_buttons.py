import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from config import Config
from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

LENGTH_OF_FILE_NAME = """⚠️ **Error **\n\nFile Caption Limit Allowed By Telegram is {alimit} Characters.\n\nThe Given File Name Has {num} Characters.\n\nPlease Short Your File Caption And Try Again !"""


@Client.on_callback_query(filters.regex("^baddcapbut"))
async def add_cap_but(bot, update):
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
    captionss = await bot.ask(
        chat_id=update.message.chat.id,
        text="✶ Send me **Caption** to be added\n\n👉 **Caption :** The Texts that are at the bottom of the File\n\n__✶ Or Send /cancel To Stop__",
        reply_markup=ForceReply(True),
        filters=filters.text,
        reply_to_message_id=reply_msg.id,
    )
    #  await captionss.delete()
    await captionss.request.delete()
    captions = captionss.text
    if captions.lower() == "/cancel":
        await update.message.reply_text(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        return

    if len(captions) > 1024:
        await update.message.reply_text(
            LENGTH_OF_FILE_NAME.format(alimit="1024", num=len(captions)),
            reply_to_message_id=reply_msg.id,
        )
        return

    NUMBER_BUTTONS = ReplyKeyboardMarkup(
        [["1", "2", "3"], ["4", "5"], ["Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        number_ask = await asyncio.wait_for(
            bot.ask(
                chat_id=update.message.chat.id,
                text="Select the Number Of Buttons\n\n__✶ **Click the Button of your choice**__ 👇",
                reply_markup=NUMBER_BUTTONS,
                filters=filters.text,
            ),
            300,
        )
        #   await number_ask.delete()
        await number_ask.request.delete()
        number_ask = number_ask.text
    except asyncio.TimeoutError:
        try:
            ccc = await update.message.reply(".", reply_markup=NUMBER_BUTTONS)
            await ccc.delete()
            await number_ask.request.delete()
        except:
            pass
        number_ask = "1"

    if number_ask == "1":
        number_asks = "1"
    elif number_ask == "2":
        number_asks = "2"
    elif number_ask == "3":
        number_asks = "3"
    elif number_ask == "4":
        number_asks = "4"
    elif number_ask == "5":
        number_asks = "5"
    elif number_ask == "More":
        number_asks = "More"
    elif number_ask == "Cancel":
        number_asks = "Cancel"
    else:
        number_asks = "Wrong"

    if number_asks == "Wrong":
        await update.message.reply_text(
            "⚠️ You didn't Choose option\n\nSo, Process Cancelled  ✅",
            reply_to_message_id=reply_msg.id,
        )
        return

    if number_asks == "Cancel":
        await update.message.reply_text(
            "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
        )
        return

    if number_asks == "1":
        chitranjan_diksha = await bot.ask(
            chat_id=update.message.chat.id,
            text="✶ Send me Button_Name and 🔗 Button_Url in This Format 👇\n\n`Button_Name,Button_Url` \n\n **Here is the example** 👇 👇\n\n`DKBOTZ,https://t.me/DKBOTZ`\n\n__✶ Or Send /cancel To Stop__",
            reply_markup=ForceReply(True),
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #   await chitranjan_diksha.delete()
        await chitranjan_diksha.request.delete()
        file_name = chitranjan_diksha.text
        if file_name.lower() == "/cancel":
            await update.message.reply_text(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        try:
            button_name, button_url = file_name.split(",")
            #  button_name, button_url = updated_data[1], updated_data[2]
            reply_markups = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=f"{button_name}", url=f"{button_url}")]]
            )
        except Exception as e:
            print(e)
            await update.message.reply(
                f"🧐 Please follow the specified format\n\n⚠️ **Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

    if number_asks == "2":
        chitranjan_diksha = await bot.ask(
            chat_id=update.message.chat.id,
            text="✶ Send me Button_Name and Button_Url in This Format 👇\n\n`Button_Name1,Button_Url1+Button_Name2,Button_Url2` \n\n **Here is the example** 👇 👇\n\n`Google,https://www.google.com+YouTube,https://www.youtube.com`\n\n__✶ Or Send /cancel To Stop__",
            reply_markup=ForceReply(True),
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #   await chitranjan_diksha.delete()
        await chitranjan_diksha.request.delete()
        file_name = chitranjan_diksha.text
        if file_name.lower() == "/cancel":
            await update.message.reply_text(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        try:
            typeone, typetwo = file_name.split("+")
            button_namea, button_urla = typeone.split(",")
            button_nameb, button_urlb = typetwo.split(",")
        except Exception as e:
            print(e)
            await update.message.reply(
                f"🧐 Please follow the specified format\n\n⚠️ **Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        reply_markups = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{button_namea}", url=f"{button_urla}"),
                    InlineKeyboardButton(f"{button_nameb}", url=f"{button_urlb}"),
                ],
            ]
        )

    if number_asks == "3":
        chitranjan_diksha = await bot.ask(
            chat_id=update.message.chat.id,
            text="✶ Send me Button_Name and Button_Url in This Format 👇\n\n`Button_Name1,Button_Url1+Button_Name2,Button_Url2+Button_Name2,Button_Url2` \n\n **Here is the example** 👇 👇\n\n`Google,https://www.google.com+YouTube,https://www.youtube.com+Telegram,https://t.me`\n\n__✶ Or Send /cancel To Stop__",
            reply_markup=ForceReply(True),
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #   await chitranjan_diksha.delete()
        await chitranjan_diksha.request.delete()
        file_name = chitranjan_diksha.text
        if file_name.lower() == "/cancel":
            await update.message.reply_text(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        try:
            typeone, typetwo, typethree = file_name.split("+")
            button_namea, button_urla = typeone.split(",")
            button_nameb, button_urlb = typetwo.split(",")
            button_namec, button_urlc = typethree.split(",")
        except Exception as e:
            print(e)
            await update.message.reply(
                f"🧐 Please follow the specified format\n\n⚠️ **Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        reply_markups = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{button_namea}", url=f"{button_urla}"),
                    InlineKeyboardButton(f"{button_nameb}", url=f"{button_urlb}"),
                ],
                [
                    InlineKeyboardButton(f"{button_namec}", url=f"{button_urlc}"),
                ],
            ]
        )

    if number_asks == "4":
        chitranjan_diksha = await bot.ask(
            chat_id=update.message.chat.id,
            text="✶ Send me Button_Name and Button_Url in This Format 👇\n\n`Button_Name1,Button_Url1+Button_Name2,Button_Url2+Button_Name3,Button_Url3+Button_Name4,Button_Url4` \n\n **Here is the example** 👇 👇\n\n`Google,https://www.google.com+YouTube,https://www.youtube.com+Telegram,https://t.me+Facebook,https://fb.com`\n\n__✶ Or Send /cancel To Stop__",
            reply_markup=ForceReply(True),
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #   await chitranjan_diksha.delete()
        await chitranjan_diksha.request.delete()
        file_name = chitranjan_diksha.text
        if file_name.lower() == "/cancel":
            await update.message.reply_text(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        try:
            typeone, typetwo, typethree, typefour = file_name.split("+")
            button_namea, button_urla = typeone.split(",")
            button_nameb, button_urlb = typetwo.split(",")
            button_namec, button_urlc = typethree.split(",")
            button_named, button_urld = typefour.split(",")
        except Exception as e:
            print(e)
            await update.message.reply(
                f"🧐 Please follow the specified format\n\n⚠️ **Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        reply_markups = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{button_namea}", url=f"{button_urla}"),
                    InlineKeyboardButton(f"{button_nameb}", url=f"{button_urlb}"),
                ],
                [
                    InlineKeyboardButton(f"{button_namec}", url=f"{button_urlc}"),
                    InlineKeyboardButton(f"{button_named}", url=f"{button_urld}"),
                ],
            ]
        )

    if number_asks == "5":
        chitranjan_diksha = await bot.ask(
            chat_id=update.message.chat.id,
            text="✶ Send me Button_Name and Button_Url in This Format 👇\n\n`Button_Name1,Button_Url1+Button_Name2,Button_Url2+Button_Name3,Button_Url3+Button_Name4,Button_Url4+Button_Name5,Button_Url5` \n\n **Here is the example** 👇 👇\n\n`Google,https://www.google.com+YouTube,https://www.youtube.com+Telegram,https://t.me+Facebook,https://fb.com+Twitter,https://www.twitter.com`\n\n__✶ Or Send /cancel To Stop__",
            reply_markup=ForceReply(True),
            filters=filters.text,
            reply_to_message_id=reply_msg.id,
        )
        #   await chitranjan_diksha.delete()
        await chitranjan_diksha.request.delete()
        file_name = chitranjan_diksha.text
        if file_name.lower() == "/cancel":
            await update.message.reply_text(
                "Process Cancelled  ✅", reply_to_message_id=reply_msg.id
            )
            return

        try:
            typeone, typetwo, typethree, typefour, typefive = file_name.split("+")
            button_namea, button_urla = typeone.split(",")
            button_nameb, button_urlb = typetwo.split(",")
            button_namec, button_urlc = typethree.split(",")
            button_named, button_urld = typefour.split(",")
            button_namee, button_urle = typefive.split(",")
        except Exception as e:
            print(e)
            await update.message.reply(
                f"🧐 Please follow the specified format\n\n⚠️ **Error :** {e}",
                reply_to_message_id=reply_msg.id,
            )
            return

        reply_markups = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{button_namea}", url=f"{button_urla}"),
                    InlineKeyboardButton(f"{button_nameb}", url=f"{button_urlb}"),
                ],
                [
                    InlineKeyboardButton(f"{button_namec}", url=f"{button_urlc}"),
                    InlineKeyboardButton(f"{button_named}", url=f"{button_urld}"),
                ],
                [
                    InlineKeyboardButton(f"{button_namee}", url=f"{button_urle}"),
                ],
            ]
        )

    if number_asks == "More":
        await update.message.reply_text(
            "It's in under developing.", reply_to_message_id=reply_msg.id
        )
        return

    try:
        await reply_msg.copy(
            update.message.chat.id, caption=captions, reply_markup=reply_markups
        )
        logger.info(
            f"Successfully Buttons Added ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )

        if Config.LOG_CHANNEL:
            cad = await reply_msg.copy(
                chat_id=Config.LOG_CHANNEL, reply_markup=reply_markups
            )
            await cad.reply_text(
                f"𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :\n\n🌷 **First Name :** `{update.from_user.first_name}`\n\n🌷 **User Id :** `{update.from_user.id}`\n\n🌷 **User Name :** `@{update.from_user.username}`\n\n🌷 Used Buttons Maker ✅"
            )
    except Exception as e:
        print(e)
        await update.message.reply(
            f"⚠️ **Error :** Occurred", reply_to_message_id=reply_msg.id
        )
        return
