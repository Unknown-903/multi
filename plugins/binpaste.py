from requests import post
from plugins.http import post


async def spacebin(text):
    url = "https://spaceb.in/api/v1/documents/"
    res = post(url, data={"content": text, "extension": "txt"})
    return f"https://spaceb.in/{res.json()['payload']['id']}"

async def batbin(text):
    base = "https://batbin.me/"
    resp = await post(f"{base}api/v2/paste", data=text)
    code = resp["message"]
    return f"{base}{code}"
