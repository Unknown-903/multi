import logging
import os
import math
import time
import shutil
from collections import defaultdict

from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

COUNT = []

CANCEL_PROCESS = defaultdict(lambda: [])


async def time_gap_remove(bot, update):
    download_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}"
    if not os.path.isdir(download_path):
        try:
            del Config.TIME_GAP_STORE[update.from_user.id]
        except Exception as e:
            logger.info(
                f"⚠️ Error in Removing TimeGap: {e} By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )


async def msg_edit(msg_id, texts):
    try:
        await msg_id.edit(texts)
    except:
        pass


async def dmsg_edit(msg_id, texts):
    edited_msg = None
    try:
        edited_msg = await msg_id.edit(texts)
    except:
        pass
    return edited_msg


async def clear_server(user_id, one=None, two=None, three=None, four=None):
    directory = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    if user_id in COUNT:
        try:
            COUNT.remove(user_id)
        except:
            pass
    if os.path.isdir(directory):
        try:
            shutil.rmtree(directory)
        except:
            pass
    if one is not None:
        if os.path.exists(one):
            try:
                os.remove(one)
            except:
                pass
    if two is not None:
        if os.path.exists(two):
            try:
                os.remove(two)
            except:
                pass
    if three is not None:
        if os.path.exists(three):
            try:
                os.remove(three)
            except:
                pass
    if four is not None:
        if os.path.exists(four):
            try:
                os.remove(four)
            except:
                pass


async def clear_server_two(
    first, second=None, third=None, fourth=None, fifth=None, sixth=None
):
    try:
        os.remove(first)
    except:
        pass
    try:
        os.remove(second)
    except:
        pass
    try:
        os.remove(third)
    except:
        pass
    try:
        os.remove(fourth)
    except:
        pass
    try:
        os.remove(fifth)
    except:
        pass
    try:
        os.remove(sixth)
    except:
        pass


async def delete_msg(one, two=None, three=None, four=None, five=None):
    try:
        await one.delete()
    except:
        pass
    try:
        await two.delete()
    except:
        pass
    try:
        await three.delete()
    except:
        pass
    try:
        await four.delete()
    except:
        pass
    try:
        await five.delete()
    except:
        pass


async def pl_server_clear(user_id, output_folder=None, fileserver=None):
    try:
        COUNT.remove(user_id)
    except:
        pass
    try:
        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
    except:
        pass
    try:
        shutil.rmtree(output_folder)
    except:
        pass
    try:
        os.rmdir(output_folder)
    except:
        pass
    try:
        os.remove(fileserver)
    except:
        pass


def media_file_id(m):
    media = (
        m.audio
        or m.document
        or m.photo
        or m.video
        or m.animation
        or m.voice
        or m.video_note
    )

    if media and media.file_id:
        return media.file_id
    else:
        return None


def remove_unwanted(string):
    return (
        string.replace('"', "")
        .replace(":", " ")
        .replace(";", " ")
        .replace("?", " ")
        .replace("&", " ")
        .replace(",", " ")
        .replace("*", " ")
        .replace("-", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("/", " ")
        .replace("!", " ")
        .replace("~", " ")
        .replace("`", " ")
        .replace("|", " ")
        .replace("•", " ")
        .replace("√", " ")
        .replace("π", " ")
        .replace("'", " ")
        .replace("}", " ")
        .replace("{", " ")
        .replace("=", " ")
        .replace("°", " ")
        .replace("^", " ")
        .replace("©", " ")
        .replace("®", " ")
        .replace("™", " ")
        .replace("✓", " ")
        .replace("[", " ")
        .replace("]", " ")
        .replace("<", " ")
        .replace(">", " ")
    )


async def paid_service_subs(bot, update):
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("FEATURES", callback_data="function"),
                InlineKeyboardButton("Instructions", callback_data="instruct"),
            ],
            # [InlineKeyboardButton("Buy Now", url=f"{Config.PAID_SUBS_URL}")],
        ]
    )
    if Config.PAID_SUBS:
        try:
            chat = await bot.get_chat_member(
                chat_id=(
                    int(Config.PAID_SUBS)
                    if Config.PAID_SUBS.startswith("-100")
                    else Config.PAID_SUBS
                ),
                user_id=update.from_user.id,
            )
            # logger.info(f"❌ Channel Status: {chat.status}")
            chat_stats = chat.status
            if f"{chat_stats}" == "ChatMemberStatus.BANNED":
                await bot.delete_messages(
                    chat_id=update.chat.id, message_ids=update.id, revoke=True
                )
                await bot.send_sticker(
                    chat_id=update.chat.id,
                    sticker="CAACAgUAAxkBAAESX79jQ3ttwFFl-924jiNO24a4BA_xrgACnAUAApRgGFaLa4T0ra8TrioE",
                )
                await update.reply(
                    "**⚠️ You're Kicked from Subscription Channel❗**\n\nFor help go to @DKBOTZSUPPORT"
                )
                return 9

        except UserNotParticipant:
            await update.reply_text(
                text="Only paid users can use me. For more information Click on **Instructions** Button",
                reply_markup=SUB_BUTTONS,
                disable_web_page_preview=True,
                quote=True,
            )
            return 9
        except Exception as e:
            await update.reply_text(
                text=f"⚠️ **Error** : {e}\n\nReport it in @DKBOTZSUPPORT"
            )
            return 9


async def force_sub(bot, update):
    if Config.FORCE_SUBS:
        try:
            chat = await bot.get_chat_member(Config.FORCE_SUBS, update.from_user.id)
            # logger.info(f"❌ Channel Status: {chat.status}")
            chat_stats = chat.status
            if f"{chat_stats}" == "ChatMemberStatus.BANNED":
                await bot.delete_messages(
                    chat_id=update.chat.id, message_ids=update.id, revoke=True
                )
                await bot.send_sticker(
                    chat_id=update.chat.id,
                    sticker="CAACAgUAAxkBAAESX79jQ3ttwFFl-924jiNO24a4BA_xrgACnAUAApRgGFaLa4T0ra8TrioE",
                )
                await update.reply(
                    "**⚠️ You're Kicked from My Channel❗**\n\nFor help go to @DKBOTZSUPPORT"
                )
                return 9

        except UserNotParticipant:
            button = [
                [
                    InlineKeyboardButton(
                        "Join Now", url=f"https://t.me/{Config.FORCE_SUBS}"
                    )
                ]
            ]
            markup = InlineKeyboardMarkup(button)
            await update.reply_text(
                text="**Due to Overload Only My Channel Subscribers Can Use\n\nSo, first Join Channel By Clicking Below Button 👇**",
                reply_markup=markup,
                quote=True,
            )
            return 9
        except Exception as e:
            await update.reply_text(
                text=f"⚠️ **Error** : {e}\n\nReport it in @DKBOTZSUPPORT"
            )
            return 9


async def force_sub_two(bot, update):
    if Config.FORCE_SUBS_TWO:
        try:
            chat = await bot.get_chat_member(Config.FORCE_SUBS_TWO, update.from_user.id)
            # logger.info(f"❌ Channel Status: {chat.status}")
            chat_stats = chat.status
            if f"{chat_stats}" == "ChatMemberStatus.BANNED":
                await bot.delete_messages(
                    chat_id=update.chat.id, message_ids=update.id, revoke=True
                )
                await bot.send_sticker(
                    chat_id=update.chat.id,
                    sticker="CAACAgUAAxkBAAESX79jQ3ttwFFl-924jiNO24a4BA_xrgACnAUAApRgGFaLa4T0ra8TrioE",
                )
                await update.reply(
                    "**⚠️ You're Kicked from My Channel❗**\n\nFor help go to @DKBOTZSUPPORT"
                )
                return 9

        except UserNotParticipant:
            button = [
                [
                    InlineKeyboardButton(
                        "Join Now", url=f"https://t.me/{Config.FORCE_SUBS_TWO}"
                    )
                ]
            ]
            markup = InlineKeyboardMarkup(button)
            await update.reply_text(
                text="**Due to Overload Only My Channel Subscribers Can Use\n\nSo, first Join Channel By Clicking Below Button 👇**",
                reply_markup=markup,
                quote=True,
            )
            return 9
        except Exception as e:
            await update.reply_text(
                text=f"⚠️ **Error** : {e}\n\nReport it in @DKBOTZSUPPORT"
            )
            return 9


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + "B"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


CAPTCHA = [
    "AgYK93",
    "96hQYi",
    "ert163",
    "592640",
    "AgYKo3",
    "A6hQYi",
    "erP163",
    "KF2640",
    "MiYK93",
    "OwhQYi",
    "T0t163",
    "U82640",
    "26YKo3",
    "Z6hQYi",
    "RrP163",
    "MF2640",
    "AgYKBr",
    "96hQVo",
    "ert16R",
    "592Ab7",
    "AgY48A",
    "A6h79M",
    "erPgyK",
    "KF2Uyk",
    "MiYak9",
    "OwhQpy",
    "T0t8Iu",
    "U82gyo",
    "26YAuo",
    "Z6hpoY",
    "RrP78g",
    "MF2Ay9",
    "MkYK93",
    "4kEQYi",
    "u5l163",
    "4Ru640",
    "Ak6Ko3",
    "EkPQYi",
    "AyT163",
    "QT6640",
    "O5uK93",
    "CT9QYi",
    "6iA163",
    "T79640",
    "ABcKo3",
    "ZtqQYi",
    "9Qt163",
    "Ty1640",
    "IL6KBr",
    "N58QVo",
    "0Oy16R",
    "7tKAb7",
    "Sd548A",
    "74V79M",
    "EKigyK",
    "IS8Uyk",
    "Mo5ak9",
    "96hQpy",
    "Lhf8Iu",
    "AuTgyo",
    "Pt9Auo",
    "D6epoY",
    "Y5n78g",
    "BbbAy9",
    "AaYK93",
    "AahQYi",
    "Bbt163",
    "Bb2640",
    "CcYKo3",
    "DdhQYi",
    "EeP163",
    "Ff2640",
    "FfYK93",
    "EehQYi",
    "Fft163",
    "Gg2640",
    "HhYKo3",
    "IihQYi",
    "JjP163",
    "Kk2640",
    "LlYKBr",
    "MmhQVo",
    "Mmt16R",
    "Ll2Ab7",
    "NnY48A",
    "Ooh79M",
    "PpPgyK",
    "Qq2Uyk",
    "QqYak9",
    "PphQpy",
    "Rrt8Iu",
    "Rr2gyo",
    "SsYAuo",
    "SshpoY",
    "TtP78g",
    "Tt2Ay9",
    "UuYK93",
    "UuEQYi",
    "Vvl163",
    "Vvu640",
    "Ww6Ko3",
    "XxPQYi",
    "YyT163",
    "Zz6640",
    "AsuK93",
    "Po9QYi",
    "IoA163",
    "Ui9640",
    "LkcKo3",
    "YuqQYi",
    "Rtt163",
    "Er1640",
    "Mn6KBr",
    "Kj8QVo",
    "Yuy16R",
    "RtKAb7",
    "Fg548A",
    "ErV79M",
    "WeigyK",
    "Qw8Uyk",
    "As5ak9",
    "ZxhQpy",
    "Bvf8Iu",
    "GhTgyo",
    "Hg9Auo",
    "KjepoY",
    "Rtn78g",
    "WebAy9",
]


class Sarita:
    INVALID_LINKS = [
        "https://youtu.be/N",
        "https://youtu.be/O",
        "https://youtu.be/P",
        "https://youtu.be/Q",
        "https://youtu.be/R",
        "https://youtu.be/S",
        "https://youtu.be/T",
        "https://youtu.be/U",
        "https://youtu.be/V",
        "https://youtu.be/W",
        "https://youtu.be/X",
        "https://youtu.be/Y",
        "https://youtu.be/Z",
        "https://youtu.be/A",
        "https://youtu.be/B",
        "https://youtu.be/C",
        "https://youtu.be/D",
        "https://youtu.be/E",
        "https://youtu.be/F",
        "https://youtu.be/G",
        "https://youtu.be/H",
        "https://youtu.be/I",
        "https://youtu.be/J",
        "https://youtu.be/K",
        "https://youtu.be/L",
        "https://youtu.be/M",
        "https://youtu.be/1",
        "https://youtu.be/2",
        "https://youtu.be/3",
        "https://youtu.be/4",
        "https://youtu.be/5",
        "https://youtu.be/6",
        "https://youtu.be/7",
        "https://youtu.be/8",
        "https://youtu.be/9",
        "https://youtu.be/0",
        "https://youtu",
        "https://youtu.",
        "https://youtu.be",
        "https://youtu.be/",
        "https://youtu.b",
        "https://youtu.be/",
        "https://youtu.com/",
        "https://youtube.com/",
        "https://youtube.com",
        "https://youtube.co",
        "https://youtube.c",
        "https://youtu.c",
        "https://youtu.co",
        "https://youtu.be/a",
        "https://youtu.be/b",
        "https://youtu.be/c",
        "https://youtu.be/d",
        "https://youtu.be/e",
        "https://youtu.be/f",
        "https://youtu.be/g",
        "https://youtu.be/h",
        "https://youtu.be/i",
        "https://youtu.be/j",
        "https://youtu.be/k",
        "https://youtu.be/l",
        "https://youtu.be/m",
        "https://youtu.be/n",
        "https://youtu.be/o",
        "https://youtu.be/p",
        "https://youtu.be/q",
        "https://youtu.be/r",
        "https://youtu.be/s",
        "https://youtu.be/t",
        "https://youtu.be/u",
        "https://youtu.be/v",
        "https://youtu.be/w",
        "https://youtu.be/x",
        "https://youtu.be/y",
        "https://youtu.be/z",
    ]
