import time

from config import Config

MESSAGE_IG = {}
USER_IDS = {}


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " days, ") if days else "")
        + ((str(hours) + " hours, ") if hours else "")
        + ((str(minutes) + " minutes, ") if minutes else "")
        + ((str(seconds) + " seconds, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]


async def timegap_check(m):
    """Checking the time gap is completed or not 
    and checking the parallel process"""

    if m.from_user.id in Config.TIME_GAP_STORE:
        if int(time.time() - Config.TIME_GAP_STORE[m.from_user.id]) < Config.TIME_GAP:
            text = f"Please wait {TimeFormatter((int(Config.TIME_GAP_STORE[m.from_user.id]) + Config.TIME_GAP - int(time.time())) * 1000)}."
            await m.reply_text(
                text=text,
                
                quote=True
            )
            return True
        else:
            del Config.TIME_GAP_STORE[m.from_user.id]
            return False
    else:
        return False

