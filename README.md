## V8 Advanced

#### sox will be in requirements & Dockerfile

### AVAILABLE COMMANDS 
<details><summary>Set Commands</summary>

```
start - Start
info - Check Your Details
upgrade - Upgrade Your Plan
search - Search YouTube Song
settings - Explore Your Settings
usettings - Useless Settings
show_thumb - Show Thumbnail
del_thumb - Delete Thumbnail
admin - All Admin Commands
```

</details>

### Deploy On Heroku

<details><summary>Deploy Now</summary>
</br>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Chitranjan6G/V8)

[![Deploy on Scalingo](https://cdn.scalingo.com/deploy/button.svg)](https://my.scalingo.com/deploy?source=https://github.com/Chitranjan6G/Video-Converter-V6)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/O9TCnX?referralCode=CLCOS-)

</details>

```
from pyromod import listen


version: "3.3"

services:
  chitranjan:
    build: .
    command: bash start.sh
    restart: on-failure
    ports:
      - "80:80"

version: "3.9"
services:
  worker:
    build: .
    environment:
      BOT_TOKEN: $BOT_TOKEN
      SESSION_NAME: $SESSION_NAME

_-------------------
Okteto

Procfile
web: python main.py

docker-compose.yml
version: "3.3"

services:
  chitranjan:
    build: .
    command: bash start.sh
    restart: on-failure
    ports:
      - "0.0.0.0"
_-----------------------

```

```
Duration Error Handle Best

    if isinstance(duration, str):
        await clear_server(user_id, saved_file_path)
        await bc.edit(f"⚠️ Sorry! I can't open this file")
        return


FROM ubuntu:latest 

RUN  apt-get update -y && \
     apt-get upgrade -y && \
     apt-get dist-upgrade -y && \
     apt-get -y autoremove && \
     apt-get clean

RUN apt-get install -y p7zip \
    p7zip-full \
    mediainfo \
    zip \
    rar \
    python3 \
    ffmpeg \
    python3-pip \
    p7zip-rar \
    sox \
    cabextract \
    file-roller \
    && rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD bash start.sh

```
```
--audio-quality 0 <- Specify ffmpeg/avconv audio quality,
insert a value between 0 (better) and 9 (worse) for VBR or a specific
bitrate like 128K (default 5).
Youtube streams for nonpremium users with variable bitrate up to 160kbps in opus format.
Opus format is newer than mp3 and has better compression than mp3
preserving the same quality. So 160kbps opus = ~ 256kbps mp3.  
When audio-quality is default (5 in 0-9 scale) mp3 bitrate
is limited to 160kbps which means that some sound quality is lost during compression.
When audio-quality is set to 0 mp3 goes up to 300kbps preserving original quality.

--audio-format mp3 <-  Specify audio format: "best", "aac", "flac", "mp3", "m4a",
"opus", "vorbis", or "wav"; "best" by default; No effect without -x (--extract-audio).
In this case we choose mp3.
Alternatively you could choose for example opus which
is oryginally provided by youtube and is newer and better than mp3
or flac which is loseless codec.
    
```

```
        if reply_msg.media:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get("duration").seconds
                bool = True

            else:
                try:
                    duration = await Ranjan.get_duration(file_path)
                    bool = True
                except Exception as e:
                    bool = False
                    await clear_server(update.from_user.id, file_path)
                    logger.info(e)
                    await msg_edit(bc, f"⚠️ **F Duration Error** : {e}")

        else:
            try:
                duration = await Ranjan.get_duration(file_path)
                bool = True
            except Exception as e:
                bool = False
                await clear_server(update.from_user.id, file_path)
                logger.info(e)
                await msg_edit(bc, f"⚠️ **F Duration Error** : {e}")

```
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/NkBots/Multi-Usage-Paid-Free-Feb27)
