from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import Database
from plugins.settings import OpenSettings, audios_settings

db = Database()


@Client.on_callback_query(filters.regex("^othumb"))
async def othumb_(bot, update):
    othumb = await db.get_othumb(update.from_user.id)
    if othumb is True:
        await db.set_othumb(update.from_user.id, othumb=False)
        alert_text = f"🖼️ Thumbnail Off ❌\n\n👉 From Now Your Output Video will be Without thumbnail"
    elif othumb is False:
        await db.set_othumb(update.from_user.id, othumb=True)
        alert_text = f"🖼️ Thumbnail ON ✅ \n\n👉 From Now your Output Video will have Thumbnail\n\n👉 For Custom Thumbnail send an image to save"

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^auto_rename"))
async def auto_rename_(bot, update):
    auto_rename = await db.get_auto_rename(update.from_user.id)
    if auto_rename is True:
        await db.set_auto_rename(update.from_user.id, auto_rename=False)
        alert_text = f"❌ Auto Rename Deactivated"
    elif auto_rename is False:
        await db.set_auto_rename(update.from_user.id, auto_rename=True)
        alert_text = f"✅ Auto Rename Activated\n\nWhen you will send file to Bot. Then Bot will ask you custom file name"

    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^upload_as"))
async def upload_as_(bot, update):
    upload_as = await db.get_upload_as(update.from_user.id)
    if upload_as is True:
        await db.set_upload_as(update.from_user.id, upload_as=False)
        alert_text = f"🔊 Upload as Document Activated\n\nFrom Now bot will send you Audio files in Document 📂"
    elif upload_as is False:
        await db.set_upload_as(update.from_user.id, upload_as=True)
        alert_text = f"🔊 Upload as Audio Activated\n\nFrom Now bot will send you Audio files in Stream 🔊"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^asvideos"))
async def asvideos_(bot, update):
    asvideos = await db.get_asvideos(update.from_user.id)
    if asvideos is True:
        await db.set_asvideos(update.from_user.id, asvideos=False)
        alert_text = f"🎥 Upload as Document Activated\n\nFrom Now bot will send files in Document 📂 form"
    elif asvideos is False:
        await db.set_asvideos(update.from_user.id, asvideos=True)
        alert_text = f"🎥 Upload as Video Activated\n\nFrom Now bot will send files in Video 🎥 form"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await OpenSettings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^comqualitdb"))
async def audio_quality_(bot, update):
    audio_quality = await db.get_audio_quality(update.from_user.id)
    QUALITY_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("0", callback_data="qualityis+0"),
                InlineKeyboardButton("1", callback_data="qualityis+1"),
            ],
            [
                InlineKeyboardButton("2", callback_data="qualityis+2"),
                InlineKeyboardButton("3", callback_data="qualityis+3"),
            ],
            [
                InlineKeyboardButton("4", callback_data="qualityis+4"),
                InlineKeyboardButton("5", callback_data="qualityis+5"),
            ],
            [
                InlineKeyboardButton("6", callback_data="qualityis+6"),
                InlineKeyboardButton("7", callback_data="qualityis+7"),
            ],
            [
                InlineKeyboardButton("8", callback_data="qualityis+8"),
                InlineKeyboardButton("9", callback_data="qualityis+9"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="acmhellp"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Compress Range : **{audio_quality}**  ✅\n\n✶ Now select the Range",
            reply_markup=QUALITY_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Compressing Range List"

    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^acmhellp"))
async def auddio_qualithelp_(bot, update):
    audio_quality = await db.get_audio_quality(update.from_user.id)
    BCSI_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="comqualitdb"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Compress Range : **{audio_quality}** in DB"
            f"\n\n0 ➛ __For (220-260) kbps__"
            f"\n\n1 ➛ __For (190-250) kbps__"
            f"\n\n2 ➛ __For (170-210) kbps__"
            f"\n\n3 ➛ __For (150-195) kbps__"
            f"\n\n4 ➛ __For (140-185) kbps__"
            f"\n\n5 ➛ __For (120-150) kbps__"
            f"\n\n6 ➛ __For (100-130) kbps__"
            f"\n\n7 ➛ __For (080-120) kbps__"
            f"\n\n8 ➛ __For (070-105) kbps__"
            f"\n\n9 ➛ __For (045-085) kbps__"
            f"\n\n✶ Default Compress Range is **5**"
            f"\n\nHence Low value = Good Quality. And High value = Low Quality"
            f"\n\n**Note :** This function only works in 🔊 **Compress Audio**",
            reply_markup=BCSI_BUTTONS,
        )
    except:
        pass
    alert_text = f"Help 🤔"

    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^qualityis"))
async def audio_qual_(bot, update):
    audio_quality = await db.get_audio_quality(update.from_user.id)
    _, audio_quality = update.data.split("+")
    audio_quality = audio_quality
    await db.set_audio_quality(update.from_user.id, audio_quality)
    alert_text = f"🔊 Compress Audio Range : {audio_quality} ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^speeddbaud"))
async def audio_speed_(bot, update):
    audio_speed = await db.get_audio_speed(update.from_user.id)
    KEY_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("50", callback_data="speedis+50"),
                InlineKeyboardButton("60", callback_data="speedis+60"),
            ],
            [
                InlineKeyboardButton("70", callback_data="speedis+70"),
                InlineKeyboardButton("80", callback_data="speedis+80"),
            ],
            [
                InlineKeyboardButton("90", callback_data="speedis+90"),
                InlineKeyboardButton("100", callback_data="speedis+100"),
            ],
            [
                InlineKeyboardButton("110", callback_data="speedis+110"),
                InlineKeyboardButton("120", callback_data="speedis+120"),
            ],
            [
                InlineKeyboardButton("130", callback_data="speedis+130"),
                InlineKeyboardButton("140", callback_data="speedis+140"),
            ],
            [
                InlineKeyboardButton("150", callback_data="speedis+150"),
                InlineKeyboardButton("160", callback_data="speedis+160"),
            ],
            [
                InlineKeyboardButton("170", callback_data="speedis+170"),
                InlineKeyboardButton("180", callback_data="speedis+180"),
            ],
            [
                InlineKeyboardButton("190", callback_data="speedis+190"),
                InlineKeyboardButton("200", callback_data="speedis+200"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="pspedhelp"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Speed Percentage : **{audio_speed}%**  ✅\n\n✶ Now select the speed %",
            reply_markup=KEY_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Speed % List"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^speedis"))
async def auddio_speedl_(bot, update):
    audio_speed = await db.get_audio_speed(update.from_user.id)
    _, audio_speed = update.data.split("+")
    audio_speed = audio_speed
    await db.set_audio_speed(update.from_user.id, audio_speed)
    alert_text = f"🔊 Audio Speed : {audio_speed}% ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^pspedhelp"))
async def auddio_speedhelp_(bot, update):
    audio_speed = await db.get_audio_speed(update.from_user.id)
    BCS_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="speeddbaud"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Speed : **{audio_speed}%**  ✅ in Database"
            f"\n\n50% ➛ __It can slow down to half the original speed__"
            f"\n\n100% ➛ __It's Default. (Original speed of audio)__"
            f"\n\n200% ➛ __For double speed of the original audio__"
            f"\n\n✶ **Hint :-** __90% Speed is Generally Used in Slowed & Reverb Mixed Songs__"
            f"\n\n**Note :** This function works in 🎵 **Speed Change**, 🎼 Music Equalizer And 🎵 Slowed & Reverb",
            reply_markup=BCS_BUTTONS,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass


# ---------- Main Quality of Audio ------------#
# List Of Quality
# 8, 16, 24, 32, 40, 48, 64, 80, 96, 112, 128, 160, 192, 224, 256, or 320


@Client.on_callback_query(filters.regex("^mainqualitycb"))
async def qlitymain_audio(bot, update):
    mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    QLTYMAIN_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("8", callback_data="main_quala+8"),
                InlineKeyboardButton("16", callback_data="main_quala+16"),
            ],
            [
                InlineKeyboardButton("24", callback_data="main_quala+24"),
                InlineKeyboardButton("32", callback_data="main_quala+32"),
            ],
            [
                InlineKeyboardButton("40", callback_data="main_quala+40"),
                InlineKeyboardButton("48", callback_data="main_quala+48"),
            ],
            [
                InlineKeyboardButton("64", callback_data="main_quala+64"),
                InlineKeyboardButton("80", callback_data="main_quala+80"),
            ],
            [
                InlineKeyboardButton("96", callback_data="main_quala+96"),
                InlineKeyboardButton("112", callback_data="main_quala+112"),
            ],
            [
                InlineKeyboardButton("128", callback_data="main_quala+128"),
                InlineKeyboardButton("160", callback_data="main_quala+160"),
            ],
            [
                InlineKeyboardButton("192", callback_data="main_quala+192"),
                InlineKeyboardButton("224", callback_data="main_quala+224"),
            ],
            [
                InlineKeyboardButton("256", callback_data="main_quala+256"),
                InlineKeyboardButton("320", callback_data="main_quala+320"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="mainqaltihelp"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Quality in kbps : **{mainquality_audio} kbps**  ✅\n\n✶ Now select the Quality in kbps",
            reply_markup=QLTYMAIN_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Quality List in kbps"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^main_quala"))
async def main_qualioa_(bot, update):
    mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    _, mainquality_audio = update.data.split("+")
    mainquality_audio = mainquality_audio
    await db.set_mainquality_a(update.from_user.id, mainquality_audio)
    alert_text = f"🔊 Audio Quality : {mainquality_audio}kbps ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^mainqaltihelp"))
async def main_qualahelp_(bot, update):
    mainquality_audio = await db.get_mainquality_a(update.from_user.id)
    CMAINQLT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="mainqualitycb"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Quality : **{mainquality_audio} kbps**  ✅ in Database"
            f"\n\n8 - 48 kbps ➛ __Worst Quality__"
            f"\n\n64 - 96 kbps ➛ __Low Quality__"
            f"\n\n96 - 192 kbps ➛ __Decent Quality__"
            f"\n\n224 - 320 kbps ➛ __Good Quality__"
            f"\n\n320 kbps ➛ __Excellent Quality__"
            f"\n\n✶ 128 kbps is selected for daily use of audio."
            f"\n\nIf you want High Quality Audio then select higher value"
            f"\n\n**Note :** __**Audio Quality Setting**__ works in 🎵 Convert Audio (mp3,opus etc.), Trimmer, Merger, Speed Changer, Volume Changer, Bass Booster, Treble Booster, Music Equalizer etc. So It's very Important.",
            reply_markup=CMAINQLT_BUTTONS,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass


# -------------- Audio volume ----------------#


@Client.on_callback_query(filters.regex("^volumectrl"))
async def volumectrl_i(bot, update):
    audio_vol = await db.get_audio_vol(update.from_user.id)
    KEY_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("10", callback_data="volctrl+10"),
                InlineKeyboardButton("20", callback_data="volctrl+20"),
            ],
            [
                InlineKeyboardButton("30", callback_data="volctrl+30"),
                InlineKeyboardButton("40", callback_data="volctrl+40"),
            ],
            [
                InlineKeyboardButton("50", callback_data="volctrl+50"),
                InlineKeyboardButton("60", callback_data="volctrl+60"),
            ],
            [
                InlineKeyboardButton("70", callback_data="volctrl+70"),
                InlineKeyboardButton("80", callback_data="volctrl+80"),
            ],
            [
                InlineKeyboardButton("90", callback_data="volctrl+90"),
                InlineKeyboardButton("100", callback_data="volctrl+100"),
            ],
            [
                InlineKeyboardButton("110", callback_data="volctrl+110"),
                InlineKeyboardButton("120", callback_data="volctrl+120"),
            ],
            [
                InlineKeyboardButton("130", callback_data="volctrl+130"),
                InlineKeyboardButton("140", callback_data="volctrl+140"),
            ],
            [
                InlineKeyboardButton("150", callback_data="volctrl+150"),
                InlineKeyboardButton("160", callback_data="volctrl+160"),
            ],
            [
                InlineKeyboardButton("170", callback_data="volctrl+170"),
                InlineKeyboardButton("180", callback_data="volctrl+180"),
            ],
            [
                InlineKeyboardButton("190", callback_data="volctrl+190"),
                InlineKeyboardButton("200", callback_data="volctrl+200"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="vohelp"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Volume Percentage : **{audio_vol}%**  ✅\n\n✶ Now select the Volume %",
            reply_markup=KEY_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Volume % List"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^volctrl"))
async def aud_volctrl_(bot, update):
    audio_vol = await db.get_audio_vol(update.from_user.id)
    _, audio_vol = update.data.split("+")
    audio_vol = audio_vol
    await db.set_audio_vol(update.from_user.id, audio_vol)
    alert_text = f"🔊 Audio Volume % : {audio_vol}% ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^vohelp"))
async def _volhelp(bot, update):
    audio_vol = await db.get_audio_vol(update.from_user.id)
    BCS_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="volumectrl"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Volume : **{audio_vol}%**  ✅ in Database"
            f"\n\n50% ➛ __For Half volume__"
            f"\n\n100% ➛ __It's Default. (Original volume of audio)__"
            f"\n\n200% ➛ __For double volume__"
            f"\n\n**Note :** __This function works in 🔊** Volume Change** & 🎼 **Music Equalizer**__\n\nThis function helps in Video & Audio merger. If you need low volume audio.",
            reply_markup=BCS_BUTTONS,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass


# ---------- Audio Bass Booster ---------------#


@Client.on_callback_query(filters.regex("^bassctrl"))
async def bassboos(bot, update):
    bassaudio = await db.get_bassaudio(update.from_user.id)
    BASS_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("-20", callback_data="bassbo+-20"),
                InlineKeyboardButton("-19", callback_data="bassbo+-19"),
                InlineKeyboardButton("-18", callback_data="bassbo+-18"),
                InlineKeyboardButton("-17", callback_data="bassbo+-17"),
            ],
            [
                InlineKeyboardButton("-16", callback_data="bassbo+-16"),
                InlineKeyboardButton("-15", callback_data="bassbo+-15"),
                InlineKeyboardButton("-14", callback_data="bassbo+-14"),
                InlineKeyboardButton("-13", callback_data="bassbo+-13"),
            ],
            [
                InlineKeyboardButton("-12", callback_data="bassbo+-12"),
                InlineKeyboardButton("-11", callback_data="bassbo+-11"),
                InlineKeyboardButton("-10", callback_data="bassbo+-10"),
                InlineKeyboardButton("-9", callback_data="bassbo+-9"),
            ],
            [
                InlineKeyboardButton("-8", callback_data="bassbo+-8"),
                InlineKeyboardButton("-7", callback_data="bassbo+-7"),
                InlineKeyboardButton("-6", callback_data="bassbo+-6"),
                InlineKeyboardButton("-5", callback_data="bassbo+-5"),
            ],
            [
                InlineKeyboardButton("-4", callback_data="bassbo+-4"),
                InlineKeyboardButton("-3", callback_data="bassbo+-3"),
                InlineKeyboardButton("-2", callback_data="bassbo+-2"),
                InlineKeyboardButton("-1", callback_data="bassbo+-1"),
            ],
            [
                InlineKeyboardButton("0", callback_data="bassbo+0"),
            ],
            [
                InlineKeyboardButton("1", callback_data="bassbo+1"),
                InlineKeyboardButton("2", callback_data="bassbo+2"),
                InlineKeyboardButton("3", callback_data="bassbo+3"),
                InlineKeyboardButton("4", callback_data="bassbo+4"),
            ],
            [
                InlineKeyboardButton("5", callback_data="bassbo+5"),
                InlineKeyboardButton("6", callback_data="bassbo+6"),
                InlineKeyboardButton("7", callback_data="bassbo+7"),
                InlineKeyboardButton("8", callback_data="bassbo+8"),
            ],
            [
                InlineKeyboardButton("9", callback_data="bassbo+9"),
                InlineKeyboardButton("10", callback_data="bassbo+10"),
                InlineKeyboardButton("11", callback_data="bassbo+11"),
                InlineKeyboardButton("12", callback_data="bassbo+12"),
            ],
            [
                InlineKeyboardButton("13", callback_data="bassbo+13"),
                InlineKeyboardButton("14", callback_data="bassbo+14"),
                InlineKeyboardButton("15", callback_data="bassbo+15"),
                InlineKeyboardButton("16", callback_data="bassbo+16"),
            ],
            [
                InlineKeyboardButton("17", callback_data="bassbo+17"),
                InlineKeyboardButton("18", callback_data="bassbo+18"),
                InlineKeyboardButton("19", callback_data="bassbo+19"),
                InlineKeyboardButton("20", callback_data="bassbo+20"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="bass_help"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Bass Range : **{bassaudio}** ✅ in DB\n\n✶ Now select the Bass Range",
            reply_markup=BASS_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Bass Range List"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^bassbo"))
async def basscltr(bot, update):
    bassaudio = await db.get_bassaudio(update.from_user.id)
    _, bassaudio = update.data.split("+")
    bassaudio = bassaudio
    await db.set_bassaudio(update.from_user.id, bassaudio)
    alert_text = f"🔊 Audio Bass Range : {bassaudio} ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^bass_help"))
async def _bass_help(bot, update):
    bassaudio = await db.get_bassaudio(update.from_user.id)
    BASS_HELP = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="bassctrl"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Bass Range : **{bassaudio}**  ✅ in Database"
            f"\n\n-20 ➛ __Remove Bass__"
            f"\n\n0 ➛ __It's Default. (Original bass of audio)__"
            f"\n\n20 ➛ __For Highest Bass, Sound is worst__"
            f"\n\n👉 First test (1-20) Bass Range with small sizes audio, Then use"
            f"\n\n👉 __I use Range (5-14), for Hindi songs.__"
            f"\n\n**Note :** __This function works in 🔊** Bass Booster** & 🎼 **Music Equalizer**__\n\nYou can feel Sound on earphone Or Bass related speakers",
            reply_markup=BASS_HELP,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass


# ---------- Audio Treble Booster -------------#


@Client.on_callback_query(filters.regex("^treblectrl"))
async def trebleboos(bot, update):
    trebleaudio = await db.get_trebleaudio(update.from_user.id)
    TREBLE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("-20", callback_data="treblebo+-20"),
                InlineKeyboardButton("-19", callback_data="treblebo+-19"),
                InlineKeyboardButton("-18", callback_data="treblebo+-18"),
                InlineKeyboardButton("-17", callback_data="treblebo+-17"),
            ],
            [
                InlineKeyboardButton("-16", callback_data="treblebo+-16"),
                InlineKeyboardButton("-15", callback_data="treblebo+-15"),
                InlineKeyboardButton("-14", callback_data="treblebo+-14"),
                InlineKeyboardButton("-13", callback_data="treblebo+-13"),
            ],
            [
                InlineKeyboardButton("-12", callback_data="treblebo+-12"),
                InlineKeyboardButton("-11", callback_data="treblebo+-11"),
                InlineKeyboardButton("-10", callback_data="treblebo+-10"),
                InlineKeyboardButton("-9", callback_data="treblebo+-9"),
            ],
            [
                InlineKeyboardButton("-8", callback_data="treblebo+-8"),
                InlineKeyboardButton("-7", callback_data="treblebo+-7"),
                InlineKeyboardButton("-6", callback_data="treblebo+-6"),
                InlineKeyboardButton("-5", callback_data="treblebo+-5"),
            ],
            [
                InlineKeyboardButton("-4", callback_data="treblebo+-4"),
                InlineKeyboardButton("-3", callback_data="treblebo+-3"),
                InlineKeyboardButton("-2", callback_data="treblebo+-2"),
                InlineKeyboardButton("-1", callback_data="treblebo+-1"),
            ],
            [
                InlineKeyboardButton("0", callback_data="treblebo+0"),
            ],
            [
                InlineKeyboardButton("1", callback_data="treblebo+1"),
                InlineKeyboardButton("2", callback_data="treblebo+2"),
                InlineKeyboardButton("3", callback_data="treblebo+3"),
                InlineKeyboardButton("4", callback_data="treblebo+4"),
            ],
            [
                InlineKeyboardButton("5", callback_data="treblebo+5"),
                InlineKeyboardButton("6", callback_data="treblebo+6"),
                InlineKeyboardButton("7", callback_data="treblebo+7"),
                InlineKeyboardButton("8", callback_data="treblebo+8"),
            ],
            [
                InlineKeyboardButton("9", callback_data="treblebo+9"),
                InlineKeyboardButton("10", callback_data="treblebo+10"),
                InlineKeyboardButton("11", callback_data="treblebo+11"),
                InlineKeyboardButton("12", callback_data="treblebo+12"),
            ],
            [
                InlineKeyboardButton("13", callback_data="treblebo+13"),
                InlineKeyboardButton("14", callback_data="treblebo+14"),
                InlineKeyboardButton("15", callback_data="treblebo+15"),
                InlineKeyboardButton("16", callback_data="treblebo+16"),
            ],
            [
                InlineKeyboardButton("17", callback_data="treblebo+17"),
                InlineKeyboardButton("18", callback_data="treblebo+18"),
                InlineKeyboardButton("19", callback_data="treblebo+19"),
                InlineKeyboardButton("20", callback_data="treblebo+20"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="treble_help"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Treble Range : **{trebleaudio}** ✅ in DB\n\n✶ Now select the Treble Range",
            reply_markup=TREBLE_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Treble Range List"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^treblebo"))
async def treblescltr(bot, update):
    trebleaudio = await db.get_trebleaudio(update.from_user.id)
    _, trebleaudio = update.data.split("+")
    trebleaudio = trebleaudio
    await db.set_trebleaudio(update.from_user.id, trebleaudio)
    alert_text = f"🔊 Music Treble Range : {trebleaudio} ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^treble_help"))
async def _treble_help(bot, update):
    trebleaudio = await db.get_trebleaudio(update.from_user.id)
    TREBLE_HELP = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="treblectrl"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Treble Range : **{trebleaudio}**  ✅ in Database"
            f"\n\n-20 ➛ __Remove Treble__"
            f"\n\n0 ➛ __It's Default. (Original Treble of audio)__"
            f"\n\n20 ➛ __For Highest Treble__"
            f"\n\n👉 First test (1-20) Treble Range with small sizes audio, Then use"
            f"\n\n👉 __I use Range (5-20), for Hindi songs.__"
            f"\n\n**Note :** __This function works in 🔊** Treble Booster** & 🎼 **Music Equalizer**__",
            reply_markup=TREBLE_HELP,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass


# -------------- Audio Reverb ----------------#


@Client.on_callback_query(filters.regex("^areverb"))
async def areverb_(bot, update):
    audio_reverb = await db.get_audio_reverb(update.from_user.id)
    KEY_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("0", callback_data="reverbs+0"),
            ],
            [
                InlineKeyboardButton("10", callback_data="reverbs+10"),
                InlineKeyboardButton("20", callback_data="reverbs+20"),
            ],
            [
                InlineKeyboardButton("30", callback_data="reverbs+30"),
                InlineKeyboardButton("40", callback_data="reverbs+40"),
            ],
            [
                InlineKeyboardButton("50", callback_data="reverbs+50"),
                InlineKeyboardButton("60", callback_data="reverbs+60"),
            ],
            [
                InlineKeyboardButton("70", callback_data="reverbs+70"),
                InlineKeyboardButton("80", callback_data="reverbs+80"),
            ],
            [
                InlineKeyboardButton("90", callback_data="reverbs+90"),
                InlineKeyboardButton("100", callback_data="reverbs+100"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="audSetting"),
                InlineKeyboardButton("🤔 Help", callback_data="rever_help"),
            ],
        ]
    )
    try:
        await update.message.edit(
            f"Audio Reverb Percentage : **{audio_reverb}**  ✅\n\n✶ Now select the Reverb %",
            reply_markup=KEY_BUTTONS,
        )
    except:
        pass
    alert_text = f"Opening Audio Reverb % List"
    try:
        await update.answer(alert_text)
    except:
        pass


@Client.on_callback_query(filters.regex("^reverbs"))
async def reverbs_(bot, update):
    audio_reverb = await db.get_audio_reverb(update.from_user.id)
    _, audio_reverb = update.data.split("+")
    audio_reverb = audio_reverb
    await db.set_audio_reverb(update.from_user.id, audio_reverb)
    alert_text = f"🔊 Audio Reverb % : {audio_reverb}% ✅"
    try:
        await update.answer(alert_text, show_alert=True)
    except:
        pass
    await audios_settings(update.message, user_id=update.from_user.id)


@Client.on_callback_query(filters.regex("^rever_help"))
async def volct_help_(bot, update):
    audio_reverb = await db.get_audio_reverb(update.from_user.id)
    BCS_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="areverb"),
            ]
        ]
    )
    try:
        await update.message.edit(
            f"Audio Reverb : **{audio_reverb}%**  ✅ in Database"
            f"\n\n0% ➛ __For No Reverb Effect__"
            f"\n\n10-60% ➛ __Reverb is UseAble in Audios__"
            f"\n\n🙂 I use for Slowed & Reverb Settings : Speed = 90%, Treble = -4, Bass = 0, Reverb = 50, These values varie according to songs sound."
            f"\n\nYou can make Slowed & Reverb Songs same like YouTube songs"
            f"\n\n**Note :** **__This function Only works in 🎵 Slowed & Reverb __**",
            reply_markup=BCS_BUTTONS,
        )
    except:
        pass
    alert_text = f"Help 🤔"
    try:
        await update.answer(alert_text)
    except:
        pass
