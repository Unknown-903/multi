import math

import heroku3
import requests
from pyrogram import Client, filters

from config import Config


@Client.on_message(
    filters.command(["dyno", "dyno_hours"]) & filters.user(Config.AUTH_USERS)
)
async def botstatus_(client, message):
    if Config.HEROKU_API_KEY:
        try:
            server = heroku3.from_key(Config.HEROKU_API_KEY)

            user_agent = (
                "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/80.0.3987.149 Mobile Safari/537.36"
            )
            accountid = server.account().id
            headers = {
                "User-Agent": user_agent,
                "Authorization": f"Bearer {Config.HEROKU_API_KEY}",
                "Accept": "application/vnd.heroku+json; version=3.account-quotas",
            }

            path = "/accounts/" + accountid + "/actions/get-quota"

            request = requests.get("https://api.heroku.com" + path, headers=headers)

            if request.status_code == 200:
                result = request.json()

                total_quota = result["account_quota"]
                quota_used = result["quota_used"]

                quota_left = total_quota - quota_used

                total = math.floor(total_quota / 3600)
                used = math.floor(quota_used / 3600)
                hours = math.floor(quota_left / 3600)
                math.floor(quota_left / 60 % 60)
                days = math.floor(hours / 24)

                usedperc = math.floor(quota_used / total_quota * 100)
                leftperc = math.floor(quota_left / total_quota * 100)

                quota_details = f"""

**Heroku Account Status :**

➩ Total **{total}** dyno hours

➩ __Dyno hours used in this month__ 
       ✶ **{used} hours**  ( {usedperc}% )

➩ __Dyno hours remaining in this month__ 
       ✶ **{hours} hours**  ( {leftperc}% )
       ✶ **Approximately {days} days**


"""
            else:
                quota_details = ""
        except:
            print("Check your Heroku API key")
            quota_details = ""
    else:
        quota_details = ""

    try:
        await message.reply_text(f"{quota_details}", quote=True, parse_mode="md")
    except:
        await message.reply_text("⚠️ Heroku API key is not Added")
