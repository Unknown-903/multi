import datetime

import motor.motor_asyncio

from config import Config


class Singleton(type):
    __instances__ = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.__instances__[cls]


class Database(metaclass=Singleton):
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.MANGODB_URL)
        self.db = self._client[Config.SESSION_NAME]
        self.col = self.db.users
        self.cache = {}

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            last_used_on=datetime.date.today().isoformat(),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason="",
            ),
            auto_rename=False,
            upload_as=True,
            asvideos=True,
            trimming_proc=True,
            audio_quality=5,
            audio_speed=100,
            mainquality_audio=128,
            audio_vol=100,
            bassaudio=5,
            trebleaudio=5,
            thumbnail=None,
            yfilter="mp4",
            othumb=True,
            audio_reverb=30,
            mediasf=True,
            urlsf=True,
            botpass="NO",
            linkrdirect="https://t.me/TheNiceBots",
            paid_status=dict(
                is_paid=False,
                paid_duration=0,
                paid_on=datetime.datetime.now(),
                paid_username="",
                paid_reason="",
            ),
            gdrive=dict(
                is_verified=False,
                token="",
            ),
            parent_id=None,
            tgupload="2GB",
        )

    # ------------ Gdrive Function ------------#
    async def remove_gdrive(self, id):
        await self.get_user(id)
        gdrive = dict(
            is_verified=False,
            token="",
        )
        self.cache[id]["gdrive"] = gdrive
        await self.col.update_one({"id": id}, {"$set": {"gdrive": gdrive}})

    async def gdrive_user(self, user_id, token):
        await self.get_user(user_id)
        gdrive = dict(
            is_verified=True,
            token=token,
        )
        self.cache[user_id]["gdrive"] = gdrive
        await self.col.update_one({"id": user_id}, {"$set": {"gdrive": gdrive}})

    async def get_gdrive_status(self, id):
        default = dict(
            is_verified=False,
            token="",
        )
        user = await self.get_user(id)
        return user.get("gdrive", default)

    async def get_all_gdrive_users(self):
        gdrive_users = self.col.find({"gdrive.is_verified": True})
        return gdrive_users

    async def set_parent(self, id, parent_id):
        await self.col.update_one({"id": id}, {"$set": {"parent_id": parent_id}})

    async def get_parent(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("parent_id", None)

    # ------------ Paid Function ------------#
    async def remove_paid(self, id):
        await self.get_user(id)
        paid_status = dict(
            is_paid=False,
            paid_duration=0,
            paid_on=datetime.datetime.now(),
            paid_username="",
            paid_reason="",
        )
        self.cache[id]["paid_status"] = paid_status
        await self.col.update_one({"id": id}, {"$set": {"paid_status": paid_status}})

    async def paid_user(self, user_id, paid_username, paid_duration, paid_reason):
        await self.get_user(user_id)
        paid_status = dict(
            is_paid=True,
            paid_duration=paid_duration,
            paid_on=datetime.datetime.now(),
            paid_username=paid_username,
            paid_reason=paid_reason,
        )
        self.cache[user_id]["paid_status"] = paid_status
        await self.col.update_one(
            {"id": user_id}, {"$set": {"paid_status": paid_status}}
        )

    async def get_paid_status(self, id):
        default = dict(
            is_paid=False,
            paid_duration=0,
            paid_on=datetime.datetime.now(),
            paid_username="",
            paid_reason="",
        )
        user = await self.get_user(id)
        return user.get("paid_status", default)

    async def get_all_paid_users(self):
        paid_users = self.col.find({"paid_status.is_paid": True})
        return paid_users

    # ---------------------------------------#

    async def get_user(self, id):
        user = self.cache.get(id)
        if user is not None:
            return user

        user = await self.col.find_one({"id": int(id)})
        self.cache[id] = user
        return user

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.get_user(id)
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def update_last_used_on(self, id):
        self.cache[id]["last_used_on"] = datetime.date.today().isoformat()
        await self.col.update_one(
            {"id": id}, {"$set": {"last_used_on": datetime.date.today().isoformat()}}
        )

    async def remove_ban(self, id):
        await self.get_user(id)
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        self.cache[id]["ban_status"] = ban_status
        await self.col.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        await self.get_user(user_id)
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason,
        )
        self.cache[user_id]["ban_status"] = ban_status
        await self.col.update_one({"id": user_id}, {"$set": {"ban_status": ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        user = await self.get_user(id)
        return user.get("ban_status", default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({"ban_status.is_banned": True})
        return banned_users

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        user_id = int(user_id)
        if self.cache.get(user_id):
            self.cache.pop(user_id)
        await self.col.delete_many({"id": user_id})

    async def get_last_used_on(self, id):
        user = await self.get_user(id)
        return user.get("last_used_on", datetime.date.today().isoformat())

    async def set_auto_rename(self, id, auto_rename):
        await self.col.update_one({"id": id}, {"$set": {"auto_rename": auto_rename}})

    async def get_auto_rename(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("auto_rename", False)

    async def set_upload_as(self, id, upload_as):
        await self.col.update_one({"id": id}, {"$set": {"upload_as": upload_as}})

    async def get_upload_as(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("upload_as", True)

    async def set_asvideos(self, id, asvideos):
        await self.col.update_one({"id": id}, {"$set": {"asvideos": asvideos}})

    async def get_asvideos(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("asvideos", True)

    async def set_trimming_proc(self, id, trimming_proc):
        await self.col.update_one(
            {"id": id}, {"$set": {"trimming_proc": trimming_proc}}
        )

    async def get_trimming_proc(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("trimming_proc", True)

    async def set_audio_quality(self, id, audio_quality):
        self.cache[id]["audio_quality"] = audio_quality
        await self.col.update_one(
            {"id": id}, {"$set": {"audio_quality": audio_quality}}
        )

    async def get_audio_quality(self, id):
        user = await self.get_user(id)
        return user.get("audio_quality", 5)

    async def set_audio_speed(self, id, audio_speed):
        self.cache[id]["audio_speed"] = audio_speed
        await self.col.update_one({"id": id}, {"$set": {"audio_speed": audio_speed}})

    async def get_audio_speed(self, id):
        user = await self.get_user(id)
        return user.get("audio_speed", 100)

    async def set_mainquality_a(self, id, mainquality_audio):
        self.cache[id]["mainquality_audio"] = mainquality_audio
        await self.col.update_one(
            {"id": id}, {"$set": {"mainquality_audio": mainquality_audio}}
        )

    async def get_mainquality_a(self, id):
        user = await self.get_user(id)
        return user.get("mainquality_audio", 128)

    async def set_audio_vol(self, id, audio_vol):
        self.cache[id]["audio_vol"] = audio_vol
        await self.col.update_one({"id": id}, {"$set": {"audio_vol": audio_vol}})

    async def get_audio_vol(self, id):
        user = await self.get_user(id)
        return user.get("audio_vol", 100)

    async def set_bassaudio(self, id, bassaudio):
        self.cache[id]["bassaudio"] = bassaudio
        await self.col.update_one({"id": id}, {"$set": {"bassaudio": bassaudio}})

    async def get_bassaudio(self, id):
        user = await self.get_user(id)
        return user.get("bassaudio", 5)

    async def set_trebleaudio(self, id, trebleaudio):
        self.cache[id]["trebleaudio"] = trebleaudio
        await self.col.update_one({"id": id}, {"$set": {"trebleaudio": trebleaudio}})

    async def get_trebleaudio(self, id):
        user = await self.get_user(id)
        return user.get("trebleaudio", 5)

    async def set_thumbnail(self, id, thumbnail):
        await self.col.update_one({"id": id}, {"$set": {"thumbnail": thumbnail}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("thumbnail", None)

    async def set_yfilter(self, id, yfilter):
        self.cache[id]["yfilter"] = yfilter
        await self.col.update_one({"id": id}, {"$set": {"yfilter": yfilter}})

    async def get_yfilter(self, id):
        user = await self.get_user(id)
        return user.get("yfilter", "mp4")

    async def set_othumb(self, id, othumb):
        await self.col.update_one({"id": id}, {"$set": {"othumb": othumb}})

    async def get_othumb(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("othumb", True)

    async def set_audio_reverb(self, id, audio_reverb):
        self.cache[id]["audio_reverb"] = audio_reverb
        await self.col.update_one({"id": id}, {"$set": {"audio_reverb": audio_reverb}})

    async def get_audio_reverb(self, id):
        user = await self.get_user(id)
        return user.get("audio_reverb", 30)

    async def set_mediafunctions(self, id, mediasf):
        await self.col.update_one({"id": id}, {"$set": {"mediasf": mediasf}})

    async def get_mediafunctions(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("mediasf", True)

    async def set_urlfunctions(self, id, urlsf):
        await self.col.update_one({"id": id}, {"$set": {"urlsf": urlsf}})

    async def get_urlfunctions(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("urlsf", True)

    async def set_botpass(self, id, botpass):
        self.cache[id]["botpass"] = botpass
        await self.col.update_one({"id": id}, {"$set": {"botpass": botpass}})

    async def get_botpass(self, id):
        user = await self.get_user(id)
        return user.get("botpass", "NO")

    async def set_linkrdirect(self, id, linkrdirect):
        self.cache[id]["linkrdirect"] = linkrdirect
        await self.col.update_one({"id": id}, {"$set": {"linkrdirect": linkrdirect}})

    async def get_linkrdirect(self, id):
        user = await self.get_user(id)
        return user.get("linkrdirect", "https://t.me/TheNiceBots")

    async def set_tgpremium(self, id, tgupload):
        self.cache[id]["tgupload"] = tgupload
        await self.col.update_one({"id": id}, {"$set": {"tgupload": tgupload}})

    async def get_tgpremium(self, id):
        user = await self.get_user(id)
        return user.get("tgupload", "2GB")
