import logging
import time
import nest_asyncio
from pyrogram import Client
import pyromod
from config import Config
from pyromod import listen
nest_asyncio.apply()

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


BOT = Client(
    name=Config.SESSION_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

if Config.SESSION_STRING:
    USERBOT = Client(
        "cmuserbot",
        session_string=Config.SESSION_STRING,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )
else:
    USERBOT = None

Start_Time = time.time()
