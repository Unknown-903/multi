import os
import sys
import requests
import json
import asyncio
from pytz import timezone
from datetime import datetime
from subprocess import check_output
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time
import logging
from pyrogram import Client, filters
from config import Config
from database.database import Database
from plugins.admin import *
from plugins import *
from subprocess import Popen, PIPE
from plugins.processors import media_uploader, Chitranjan as CH

import subprocess

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

sudo_users = Config.SUDO_USER

iptv_link = Config.IPTV

GROUP_TAG = Config.GROUP_TAG

RCLONE_DRIVE = Config.RCLONE_DRIVE

conf_path = Config.CONF_PATH


DL_DONE_MSG = """
✅ <b> Recording Completed In </b> <code>{}</code>
✅ <b> Upload Completed In </b> <code>{}</code>
<b>FileName : </b> <code>{}</code>
<b>Channel : </b> <code>{}</code>
<b>Size : </b> <code>{}</code>

<b>Made By @NitinSahay</b>
"""


CHANNELS_TEXT = """<b>Here are the List of Channels : </b>
<code>{}</code>
<b>Usage : </b> <code>/multirec channelTitle duration | showTitle</code> 
<b>Example : </b> <code>/multirec Disney 00:00:10 | Doraemon</code> 
"""

RECHELP_TEXT = """<b><i>Hello</i></b> {}
<b><i>Here are The Commands which can be used in the BOT!</i></b>

> <b>Get This Help Module </b> <code>/help</code>

> <b>Get the List of Channels </b> <code>/channels</code>

> <b>Records Multi Audio TV Rips from streamLink </b> <code>/multirec CN 00:00:10 | Ben 10</code>

<b><i>Click on the Command to COPY</i></b>
"""




@Client.on_message(filters.private & filters.command(["rechelp"]))
async def rechelp(bot, message):
    chat_id = message.chat.id
    await message.reply(text=RECHELP_TEXT)
    logger.info(
    f"(/rechelp) Command Used By {message.from_user.first_name} {str(message.from_user.id)} @{message.from_user.username}"
    )



@Client.on_message(filters.private & filters.command(["channels"]))
async def getChannels(bot, message):
    chat_id = message.chat.id


    data = fetch_data(iptv_link)
    channelsList = ""
    for i in data:
        channelsList += f"{i}\n"
    await message.reply(text=CHANNELS_TEXT.format(channelsList))
    logger.info(
            f"(/channels) Command Used By {message.from_user.first_name} {str(message.from_user.id)} @{message.from_user.username}"
        )
    
def rcloneUpload(filepath, channel):


    rclone_copy_cmd = [
        f"rclone",
        "copy",
        f"--config={conf_path}",
        str(filepath),
        f"{RCLONE_DRIVE}:{channel}",
        "-f",
        "- *.!qB",
        "--buffer-size=1M",
        "-P",
    ]

    # process = Popen(rclone_copy_cmd, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    # return stdout
    p = subprocess.run(rclone_copy_cmd)
    return p.returncode, filepath

def getDataFromPath_Rclone(path):
    output = check_output(['rclone', f'--config={conf_path}', 'lsjson', path])
    output = output.decode('utf-8')
    return output

def get_shareable_link(path):
    output = check_output(['rclone', f'--config={conf_path}', 'link', path])
    output = output.decode('utf-8')
    return output

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def ind_time():
    return datetime.now(timezone("Asia/Kolkata")).strftime('%d-%m-%Y [%H-%M-%S]')


def check_user(message):
    try:
        user_id = message.from_user.id
    except AttributeError:
        user_id = message.chat.id
    if user_id in sudo_users:
        return 'SUDO'
    elif user_id == 1984763765:
        return 'DEV'
    else:
        text = "<b>Not a Authorized User</b>\nMade with Love by @conan7612"
        bot.reply(text)
        return None


def fetch_data(url):
    data = requests.get(url)
    data = data.text
    return json.loads(data)

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


# --------------------------------------- #

@Client.on_message(filters.private & filters.command(["multirec"]))
async def multi_rec(bot, message):
    # cmd = /multirec Hungama 00:00:10 | Test File
    cmd = message.text.split("|")
    tg_cmd, channel, duration = cmd[0].strip().split(" ")
    iptv_data = fetch_data(iptv_link)

    if channel not in iptv_data:
        await message.reply(f"<b>{channel} not Available</b>")
        return
    if len(message.text.split()) < 3:
        bot.send_message("<b>Syntax: </b>`/multirec [channelName] [duration] | [filename]`")
        return

    if "|" in message.text:
        title = cmd[1].strip()
    else:
        title = "TEST FILE"

    
    video_opts = 'ffmpeg -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -i'
    video_opts_2 = '-to'
    video_opts_3 = '-map 0:v:0 -map 0:a'
    audio = "-".join(iptv_data[channel][0]["audio"])
    filename = f'[{GROUP_TAG}] {iptv_data[channel][0]["title"]} - {title} - {ind_time()} [{iptv_data[channel][0]["quality"]}] [x264] {iptv_data[channel][0]["ripType"]} [{audio}].mkv'

    streamUrl = iptv_data[channel][0]["link"]
    
    ffmpeg_cmd = video_opts.split() + \
        [streamUrl] + video_opts_2.split() + [duration] + \
        video_opts_3.split() + [filename]
    start_rec_time = time.time()

    msg = await message.reply(f"<b>Recording In Progress...</b>")
    logger.info(
        f'TEI - [Recording] {iptv_data[channel][0]["title"]} - [{iptv_data[channel][0]["quality"]}] By {message.from_user.first_name} {str(message.from_user.id)} @{message.from_user.username}'
        )
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    
    #subprocess.run(ffmpeg_cmd)

    end_rec_time = time.time()

    if os.path.exists(filename) == False:
        await msg.edit(f"<b>Recording Failed</b>")
        return

    await msg.edit(f"<b>{channel} Recorded Successfully</b>")
    logger.info(
        f'TEI - [Recording Succesfull] {iptv_data[channel][0]["title"]} - [{iptv_data[channel][0]["quality"]}] By {message.from_user.first_name} {str(message.from_user.id)} @{message.from_user.username}'
        )
    await bot.send_video(video=filename, chat_id=message.from_user.id,
                   caption=f"<code>{filename}</code>")
    
    #destination = f'TV-DL/{iptv_data[channel][0]["title"]}'

    await msg.edit(f"<b>Uploading...</b>")
    logger.info(
        f'TEI - [Uploading Started For TG Upload] {iptv_data[channel][0]["title"]} - {title} - Used By {message.from_user.first_name} {str(message.from_user.id)} @{message.from_user.username}'
        )

    #upload_start_time = time.time()
    #out, upload = rcloneUpload(filename, destination)
    #upload_end_time = time.time()

    #rclone_path = RCLONE_DRIVE + ":" + destination + "/" + filename
    #searchFile = getDataFromPath_Rclone(rclone_path)
    #searchFile = json.loads(searchFile)
    #final_link = get_shareable_link(rclone_path).strip()

    #await msg.edit(
        #text=DL_DONE_MSG.format(
            #get_readable_time(end_rec_time - start_rec_time) , get_readable_time(upload_end_time - upload_start_time) ,searchFile[0]['Name'], iptv_data[channel][0]["title"] , humanbytes(int(searchFile[0]['Size']))),
        #reply_markup=InlineKeyboardMarkup(
            #[
                #[
                    #InlineKeyboardButton(
                        #"FILE LINK", url=final_link),
                #]
            #]
        #)
    #)
    os.remove(filename)
    
