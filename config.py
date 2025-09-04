import logging
import os
from aiohttp import ClientSession
logger = logging.getLogger(__name__)

aiohttpsession = ClientSession()
class Latests(object):
    IMPROVER = (
        os.environ.get("IMPROVER", "-1001720609021")
        if os.environ.get("IMPROVER", "-1001720609021")
        else None
    )


class Config(object):
    WORKERS = int(os.environ.get("WORKERS", "10"))  # 7 workers = 10 commands at once
    SLEEP_THRESHOLD = int(os.environ.get("SLEEP_THRESHOLD", "120"))  # 1 minte
    PROCESS_TIMEOUT = int("600")  # in seconds
    VERIFIED_USERS = [
        int(i)
        for i in os.environ.get("VERIFIED_USERS", "1620169470").split(
            " "
        )  # 5385744540 for one year
    ]
    # NUMBER = 14  # Numbers Count to control users
    NUMBER = int(os.environ.get("NUMBER", 14))

    # NUMBERS = 15  # Shows Number to users, So always put +1
    NUMBERS = int(os.environ.get("NUMBERS", 15))

    DATABASE_URL = os.environ.get("DATABASE_URL")
    MAX_PROCESSES_PER_USER = int(os.environ.get("MAX_PROCESSES_PER_USER", 2))
    AUTH_USERS = [
        int(i) for i in os.environ.get("AUTH_USERS", "1620169470").split(" ")
    ]
    SLOW_SPEED_DELAY = int(os.environ.get("SLOW_SPEED_DELAY", 1))
    TIMEOUT = int(os.environ.get("TIMEOUT", 60 * 30))
    DEBUG = bool(os.environ.get("DEBUG"))
    WORKER_COUNT = int(os.environ.get("WORKER_COUNT", 5))
    FORCE_SUBS_TWO = (
        os.environ.get("FORCE_SUBS_TWO", "TellyBotzz")  # TheNiceBots Helps_Group
        if os.environ.get("FORCE_SUBS_TWO", "TellyBotzz")  # TheNiceBots
        else None
    )
    FORCE_SUBS = (
        os.environ.get("FORCE_SUBS", "TellyBotzz")  # TheNiceBots Helps_Group
        if os.environ.get("FORCE_SUBS", "TellyBotzz")  # TheNiceBots
        else None
    )
    # FORCE_SUBS = "TheNiceBots"  # "TheNiceBots"
    PAID_SUBS = (
        os.environ.get("PAID_SUBS", "")  # paid private channel id -1001611730682
        if os.environ.get("PAID_SUBS", "")  # paid private channel id
        else None
    )
    # PAID_SUBS = "-1001377793056" # paid channel id    PAID_SUBS = ""
    PAID_SUBS_URL = "https://t.me/TellyBotzz"

    if Latests.IMPROVER is not None:
        LOG_CHANNEL = int(Latests.IMPROVER)
    else:
        LOG_CHANNEL = None

    BANNED_USER = (
        [int(i) for i in os.environ.get("BANNED_USER", "").split(" ")]
        if os.environ.get("BANNED_USER", "")
        else None
    )
    LOGGED_USER = []

    try:
        TIME_GAP = (
            int(os.environ.get("TIME_GAP", "30"))
            if os.environ.get("TIME_GAP", "30")
            else None
        )
    except:
        TIME_GAP = None
        logger.warning("Give The Timegap In Seconds. Dont Use Letters")
    TIME_GAP_STORE = {}

    DOWNLOAD_LOCATION = "./DOWNLOADS"
    DOWNLOAD_PATH = "./DOWNLOADS"
    PROCESS_MAX_TIMEOUT = 3600

    MAX_VIDEOS = int(os.environ.get("MAX_VIDEOS", 200))
    PMAX_LENGTH = int(os.environ.get("PMAX_LENGTH", 20))  # Max playlist length
    MAX_COM_SIZE = int(
        os.environ.get("MAX_COM_SIZE", 52428800000000)
    )  # Video Max Compress Size (50 * 1024 * 1024 = 50 MB = 52428800 Bytes )
    MAX_COM_DURATION = int(
        os.environ.get("MAX_COM_DURATION", 108000)
    )  # Max Video compress duration in seconds
    SPOTIFY_PLAYLIST = os.environ.get("SPOTIFY_PLAYLIST", "YES")
    GDRIVE_FOLDER_UPLOAD = os.environ.get("GDRIVE_FOLDER_UPLOAD", "YES")

    MEDIA_FUNCTIONS = os.environ.get("MEDIA_FUNCTIONS", "YES")  # y
    URL_FUNCTIONS = os.environ.get("URL_FUNCTIONS", "YES")

    ONLY_SPOTIFY_DOWNLOADER = os.environ.get("ONLY_SPOTIFY_DOWNLOADER", "NO")
    ONLY_URL_UPLOADER = os.environ.get("ONLY_URL_UPLOADER", "NO")
    ONLY_YT_PLAYLIST_UPLOAD = os.environ.get("ONLY_YT_PLAYLIST_UPLOAD", "NO")  # n
    ONLY_UNI_START_TEXT = os.environ.get(
        "ONLY_UNI_START_TEXT", "YES"
    )  # it's for start/help texts. It will NO for url/playlist uploader
    BITLY_KEY = [
        "ece4c420f32b4f977b9b68bee620ef4c16fb79c2",
        "711fd58f7c83834528956257cac3294d98a4a738",
        "79faedc136c03de6202480e3476b37e195347360",
        "f5981ade3b0e3cf080077c4424fff57ceb950a5a",
        "a045a70febe88cb7c0271ed410e55da5fe648c17",
        "3d356348cdee686841450728e2762bd3debaf985",
        "200efcf75057ae5947899358dc29ab1c0458b830",
        "23780168c83e7565cce25e5ad16300cb4074a346",
        "7cd0c97c1b5777722660dd0bb0ef4bd91b4db0d6",
        "2d1b78a262745f3d61b718708656f5c7f38cdaa3",
        "a847f901f7f52c52f27f29c0298cdd0c3f312a4d",
    ]

    API_ID = int("10412514")
    API_HASH = "4d55a7064ad72adcfa8944f505453a8c"
    
    IPTV = "https://te-iptvlinks.netlify.app/iptv.json"
    GROUP_TAG = "Conan76"
    RCLONE_DRIVE = "MOHANISH_MEGA"
    CONF_PATH = "rclone.conf"
    SUDO_USER = [1620169470]

    HEROKU_API_KEY = "ced9b073-8bb7-4532-a58c-83c59ed7eb83"
    CMBOT_TOKEN = os.environ.get(
        "CMBOT_TOKEN", "6080378828:AAHbPaIjcMYElGDH_xay2cItuKbCpxB3bj8"
    )
    BOT_TOKEN = CMBOT_TOKEN
    SESSION_NAME = os.environ.get("SESSION_NAME", "NkMultiUsageBot")
    MANGOS = "mongodb+srv://sahaynitin2006:54xUl2DdnXQPntZx@cluster0.s8nwow5.mongodb.net/?retryWrites=true&w=majority"
    MANGODB_URL = os.environ.get("MANGODB_URL", MANGOS)
    AUTH_CHATS = os.environ.get("AUTH_CHATS", "")
    PREMIUM_STORE = int(os.environ.get("PREMIUM_STORE", "-1001796896298"))
    SESSION_STRING = os.environ.get(
        "SESSION_STRING",
        "BQCe4eIAlZuIwT0XXOxvG8ad27VM3DhvZXszbbUoH1J1RZoZoN9fYB5fw16lR173xt0f5Kqrxa6Ofaw28yyf2tSYLM0DF4Mj9_n1XR3BkQCpV-F_ICTCtj3cHGutfd6uNQtFpbG_ds22wvxYLsIlOclzGl8Qv2ey3Xqgv09JQPNfifc6vXmC6g1q_4JGMQ4d-ZBd50QwtjNPhqO2Qy5cChx-SUWtK0TyOwlBN4e27ILRkvOw7X-nX8596v5E5luM-jIOpvoTZXzG8CCBKUEvrnsRCr4Jnf_VXwLTGn_ACQJE4VES-HOpOxmIn4KdpDKF2AQZlN_vaC26oRdSzNnm2O-hhthBugAAAABgkdL-AA",
    )
    PAID_BOT = os.environ.get("PAID_BOT", "YES")
    OWNER_ID = os.environ.get("OWNER_ID", "1620169470")
    TIME_GAP1 = {}
    TIME_GAP2 = {}
    timegap_message = {}
    PROCESS_MAX_TIMEOUT = 3600
    RESTART_TIME = []
    TG_MAX_FILE_SIZE = 3980000000
