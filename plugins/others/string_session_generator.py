import asyncio
from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    FloodWait,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

API_TEXT = """Hi {}
Now send your `API_ID` same as `APP_ID` to Start Generating Pyrogram String Session."""

HASH_TEXT = "Now send your `API_HASH`.\n\nPress /cancel to Cancel Process."
PHONE_NUMBER_TEXT = (
    "Now send your Telegram account's Phone number in International Format. \n"
    "Including Country code. Example: **+919876543210**\n\n"
    "Press /cancel To Cancel Process."
)


@Client.on_message(filters.private & filters.command(["string_session", "gss"]))
async def genStr(bot, msg: Message):
    chat = msg.chat
    api = await bot.ask(chat.id, API_TEXT.format(msg.from_user.mention))
    if await is_cancel(msg, api.text):
        return
    try:
        int(api.text)
    except Exception:
        await msg.reply("`API_ID` is Invalid.\nPress /string_session to Start again.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` is Invalid.\nPress /string_session to Start again.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(
            chat.id,
            f'`Is "{phone}" correct? (y/n):` \n\nSend: `y` (If Yes)\nSend: `n` (If No)',
        )
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(
            chat.id, f"**ERROR:** `{str(e)}`\nPress /string_session to Start again."
        )
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds")
        return
    except ApiIdInvalid:
        await msg.reply(
            "API ID and API Hash are Invalid.\n\nPress /string_session to Start again."
        )
        return
    except PhoneNumberInvalid:
        await msg.reply(
            "Your Phone Number is Invalid.\n\nPress /string_session to Start again."
        )
        return
    try:
        otp = await bot.ask(
            chat.id,
            (
                "An OTP is sent to your phone number, "
                "Please enter OTP in `1 2 3 4 5` format. __(Space between each numbers!)__ \n\n"
                "If Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\n"
                "Press /cancel to Cancel."
            ),
            timeout=300,
        )

    except TimeoutError:
        await msg.reply(
            "Time limit reached of 5 min.\nPress /string_session to Start again."
        )
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(
            phone, code.phone_code_hash, phone_code=" ".join(str(otp_code))
        )
    except PhoneCodeInvalid:
        await msg.reply("Invalid Code.\n\nPress /string_session to Start again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Code is Expired.\n\nPress /string_session to Start again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id,
                "Your account have Two-Step Verification.\nPlease enter your Password.\n\nPress /cancel to Cancel.",
                timeout=300,
            )
        except TimeoutError:
            await msg.reply(
                "`Time limit reached of 5 min.\n\nPress /string_session to Start again.`"
            )
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message(
            "me", f"#PYROGRAM #STRING_SESSION\n\n```{session_string}```"
        )
        await client.disconnect()
        text = "String Session Generated  ✅\nClick on Below Button."
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Show String Session",
                        url=f"tg://openmessage?user_id={chat.id}",
                    )
                ]
            ]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        return


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Cancelled.")
        return True
    return False
