import asyncio
import logging
import os
import random
import time

log = logging.getLogger(__name__)


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


class Ranjan:
    @staticmethod
    def is_valid_file(msg):
        if not msg.media:
            return False
        if msg.video:
            return True
        if (msg.document) and any(
            mime in msg.document.mime_type
            for mime in ["video", "application/octet-stream"]
        ):
            return True
        return False

    @staticmethod
    def is_url(text):
        return text.startswith("http")

    @staticmethod
    def humanbytes(size):
        # this code taken from SpEcHiDe Anydl repo
        if not size:
            return 0
        power = 2**10
        n = 0
        Dic_powerN = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1
        return str(round(size, 2)) + " " + Dic_powerN[n] + "B"

    @staticmethod
    def TimeFormatter(seconds: int) -> str:
        # this code taken from SpEcHiDe Anydl repo
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        formatted_txt = f"{days} days, " if days else ""
        formatted_txt += f"{hours} hrs, " if hours else ""
        formatted_txt += f"{minutes} min, " if minutes else ""
        formatted_txt += f"{seconds} sec, " if seconds else ""
        return formatted_txt[:-2]

    @staticmethod
    def get_random_start_at(seconds, dur=0):
        return random.randint(0, seconds - dur)

    @staticmethod
    async def run_subprocess(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()

    @staticmethod
    async def generate_thumbnail_file(file_path, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        thumb_file = os.path.join(output_folder, "thumb.jpg")
        ffmpeg_cmd = [
            "ffmpeg",
            "-ss",
            "0",
            "-i",
            file_path,
            "-vframes",
            "1",
            "-vf",
            "scale=320:-1",
            "-y",
            str(thumb_file),
        ]
        output = await Ranjan.run_subprocess(ffmpeg_cmd)
        log.debug(output)
        if not os.path.exists(thumb_file):
            return None
        return thumb_file

    @staticmethod
    async def get_media_info(file_link):
        ffprobe_cmd = [
            "ffprobe",
            "-i",
            file_link,
            "-v",
            "quiet",
            "-of",
            "json",
            "-show_streams",
            "-show_format",
            "-show_chapters",
            "-show_programs",
        ]
        data, err = await Ranjan.run_subprocess(ffprobe_cmd)
        return data

    @staticmethod
    async def get_dimentions(file_link):
        ffprobe_cmd = [
            "ffprobe",
            "-i",
            file_link,
            "-v",
            "error",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            "-select_streams",
            "v:0",
        ]

        output = await Ranjan.run_subprocess(ffprobe_cmd)
        log.debug(output)
        try:
            width, height = [int(i.strip()) for i in output[0].decode().split("x")]
        except Exception as e:
            log.debug(e, exc_info=True)
            width, height = 1280, 534
        return width, height

    @staticmethod
    async def get_duration(file_link):
        ffmpeg_dur_cmd = [
            "ffprobe",
            "-i",
            file_link,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0:s=x",
            "-select_streams",
            "v:0",
        ]
        out, err = await Ranjan.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return err.decode()
        duration = round(float(out))
        if duration:
            return duration
        return "No duration!"

    @staticmethod
    async def fix_subtitle_codec(file_link):
        fixable_codecs = ["mov_text"]

        ffmpeg_dur_cmd = [
            "ffprobe",
            "-i",
            file_link,
            "-v",
            "error",
            "-select_streams",
            "s",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
        ]

        out, err = await Ranjan.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return []

        fix_cmd = []
        codecs = [i.strip() for i in out.split("\n")]
        for indx, codec in enumerate(codecs):
            if any(fixable_codec in codec for fixable_codec in fixable_codecs):
                fix_cmd += [f"-c:s:{indx}", "srt"]

        return fix_cmd
