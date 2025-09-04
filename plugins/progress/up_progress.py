import asyncio
import logging
import math
import time

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from pyrogram import Client, enums, filters
from pyrogram.errors.exceptions import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from plugins.audio import CANCEL_PROCESS, humanbytes, TimeFormatter 

UP_PROGRESS = {}

class UpProgress:
    def __init__(self, client, m, mess: Message):
        self._from_user = m.from_user.id
        self._client = client
        self._mess = mess
        self._cancelled = False
        self.m = m

    @property
    def is_cancelled(self):
        chat_id = self._mess.chat.id
        mes_id = self._mess.id

        if CANCEL_PROCESS[chat_id] and mes_id in CANCEL_PROCESS[chat_id]:
            self._cancelled = True
        return self._cancelled

    async def uploading_progress(self, current, total, ud_type, start):
        chat_id = self._mess.chat.id
        mes_id = self._mess.id
        from_user = self._from_user
        update = self.m
        reply_msg = update.message.reply_to_message

        now = time.time()
        diff = now - start
        if self.is_cancelled:
            logger.info("Process Cancelled ✅ ")
            try:
                await self._mess.edit(f"**Process Cancelled ✅**")
            except:
                pass
            await self._client.stop_transmission()
            
        if round(diff % float(1)) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = time_to_completion

            elapsed_time = TimeFormatter(milliseconds=elapsed_time)
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

            time_to_complete = round(((total - current) / speed)) * 1000
            time_to_complete = TimeFormatter(time_to_complete)
            progressbar = "[{0}{1}]".format(
                "".join(["■" for i in range(math.floor(percentage / 10))]),
                "".join(["□" for i in range(10 - math.floor(percentage / 10))]),
            )
            percent = round(percentage, 2)
            currents = humanbytes(current)
            totals = humanbytes(total)
            speeds = humanbytes(speed)
            time_to_com = time_to_complete
            process_name = ud_type
            user_ids = from_user
 
            UP_PROGRESS[f"{chat_id}_{mes_id}"] = {
                "processn": process_name,
                "progressb": progressbar,
                "percentage": percent,
                "current": currents,
                "total": totals,
                "speed": speeds,
                "timec": time_to_complete,
            }

@Client.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("siupload"))
)
async def siuploader(c, m):
    updated_data = m.data.split("/")
    chat_id, message_id = updated_data[1], updated_data[2]
    p_message = "{processn}\n\n{progressb} {percentage}%\n\n➩ {current} Of {total}\n\n➩ Speed : {speed}/s\n\n➩ Time Left : {timec}"
    try:
        await m.answer(
            text=p_message.format(
                **UP_PROGRESS[f"{chat_id}_{message_id}"]
            ),
            show_alert=True,
        )
    except Exception as e:
        print(f"⚠️ Ffmpeg Processing {e}")
        try:
            await c.answer_callback_query(
                callback_query_id=m.id,
                text=f"Processing....",
                show_alert=True,
                cache_time=0,
            )
        except:
            pass



'''
            try:
                await self._mess.edit(f"**Process Cancelled ✅**")
            except:
                pass

            try:
                await update.message.reply(
                    f"**Process Cancelled ✅**",
                    reply_to_message_id=reply_msg.id,
                )
            except:
                pass

'''
