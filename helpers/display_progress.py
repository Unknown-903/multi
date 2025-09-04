import asyncio
import logging
import math
import time

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from pyrogram.errors.exceptions import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from plugins.audio import CANCEL_PROCESS


class Progress:
    def __init__(self, from_user, client, mess: Message):
        self._from_user = from_user
        self._client = client
        self._mess = mess
        self._cancelled = False

    @property
    def is_cancelled(self):
        chat_id = self._mess.chat.id
        mes_id = self._mess.id
        if CANCEL_PROCESS[chat_id] and mes_id in CANCEL_PROCESS[chat_id]:
            self._cancelled = True
        return self._cancelled

    async def progress_for_pyrogram(self, current, total, ud_type, start):
        chat_id = self._mess.chat.id
        mes_id = self._mess.id
        from_user = self._from_user
        now = time.time()
        diff = now - start
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Cancel",
                        callback_data=(
                            f"progcancel/{chat_id}/{mes_id}/{from_user}"
                        ).encode("UTF-8"),
                    )
                ]
            ]
        )
        if self.is_cancelled:
            logger.info("Process Cancelled ✅ ")
            try:
                await self._mess.edit(f"**Process Cancelled ✅**")
            except:
                pass
            await self._client.stop_transmission()

        if round(diff % float(5)) == 0 or current == total:
            # if round(current / total * 100, 0) % 5 == 0:
            percentage = current * 100 / total
            speed = current / diff
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = time_to_completion

            elapsed_time = TimeFormatter(milliseconds=elapsed_time)
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

            time_to_complete = round(((total - current) / speed)) * 1000
            time_to_complete = TimeFormatter(time_to_complete)

            progress = "\n[{0}{1}] \n\n**➩ Percentage :** {2}%\n\n".format(
                "".join(["●" for i in range(math.floor(percentage / 5))]),
                "".join(["○" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            tmp = (
                progress
                + "➩ {0} **Of** {1}\n\n**➩ Speed :** {2}/s\n\n**➩ Time Left :** {3}\n\n".format(
                    humanbytes(current),
                    humanbytes(total),
                    humanbytes(speed),
                    time_to_complete,
                    estimated_total_time if estimated_total_time != "" else "0 s",
                )
            )
            try:
                if not self._mess.photo:
                    try:
                        await self._mess.edit_text(
                            text="{}\n {}".format(ud_type, tmp),
                            reply_markup=reply_markup,
                        )
                    except MessageNotModified:
                        pass
                    except FloodWait as fw:
                        logger.warning(f"{fw}")
                        await asyncio.sleep(fw.x)
                    except Exception as err:
                        logger.info(err)

                else:
                    try:
                        await self._mess.edit_caption(
                            caption="{}\n {}".format(ud_type, tmp)
                        )
                    except MessageNotModified:
                        pass
                    except FloodWait as fw:
                        logger.warning(f"{fw}")
                        await asyncio.sleep(fw.x)
                    except Exception as err:
                        logger.info(err)
            except Exception as er:
                logger.info(er)


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
