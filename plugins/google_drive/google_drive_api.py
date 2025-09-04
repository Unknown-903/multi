import glob
import json
import logging
import os
import re
import math
import time
import pickle 
import urllib.parse as urlparse
from mimetypes import guess_type
from urllib.error import HTTPError
from urllib.parse import parse_qs

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client.client import FlowExchangeError, OAuth2WebServerFlow
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

G_DRIVE_CLIENT_ID = "202264815644.apps.googleusercontent.com"
G_DRIVE_CLIENT_SECRET = "X4Z3ca8xfWDb1Voo-F9a7ZxJ"
OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
DOWNLOAD_LOCATION = "./downloads/"

drive_folder_name = "MultiUsageBot"
flow = None

@Client.on_message(filters.private & filters.command(["login"]))
async def _auths(client, message):
    user_id = message.from_user.id
    ss = "Please follow these steps to Login 👇"
    aa = "1. Open the given **Authorization URL** \n2. Sign in with your Google Drive account."
    bb = "3. Copy generated code and send like this 👉 /verify copied_code"
    gdrive = await db.get_gdrive_status(user_id)
    if gdrive["is_verified"]:
        token = gdrive["token"]
        token = pickle.loads(token)
        token.refresh(Http())
        token = pickle.dumps(token)
        await db.gdrive_user(user_id, token)
        await message.reply_text(f"Already Logged in Your Google Drive Account.\n\nIf you want to log in another account, Then first /logout And /login", quote=True)
    else:
        logger.info(f"⚠️ First authenticate Gdrive")
        global flow
        try:
            flow = OAuth2WebServerFlow(
                G_DRIVE_CLIENT_ID,
                G_DRIVE_CLIENT_SECRET,
                OAUTH_SCOPE,
                redirect_uri=REDIRECT_URI,
            )
            auth_url = flow.step1_get_authorize_url()  
            AUTHENTICATE = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Authorization URL", url=auth_url),
                    ],
                    [InlineKeyboardButton("Cancel", callback_data="cancel_query")],
                ]
            )   
            await message.reply_text(
                text=f"{ss}\n\n{aa}\n{bb}",
                reply_markup=AUTHENTICATE,
                quote=True,
            )
        except Exception as e:
            await message.reply_text(f"**⚠️ Error:** `{e}`", quote=True)


@Client.on_message(
    filters.private & filters.command(["logout"])
)
async def _revoke(client, message):
    user_id = message.from_user.id
    gdrive = await db.get_gdrive_status(user_id)
    if gdrive["is_verified"]:
        pass
    else:
        await message.reply_text(f"⚠️ You haven't logged in yet.\n\n👉 So, please /login first", quote=True)
        return

    try:
        await db.remove_gdrive(user_id)
        logger.info(f"Log out successfully: {user_id}")
        await message.reply_text("Successfully Logged out ✅", quote=True)
    except Exception as e:
        await message.reply_text(f"**⚠️ Error:** `{e}`", quote=True)


@Client.on_message(filters.private & filters.command(["verify"]))
async def _token(client, message):
    user_id = message.from_user.id
    INVALID_CODE = "**Invalid Code**\n\nThe Code You Have Sent Is Invalid Or Already Used Before. Generate New One By The Authorization URL"
    if len(message.command) == 1:
        return 
    tokens = " ".join(message.command[1:])
    tokenv = tokens.split()[-1]
    token_length = len(tokenv)
    if token_length == 62 and tokenv[1] == "/":
        creds = None
        global flow
        if flow:
            try:
                user_id = message.from_user.id
                stepsils = " ".join(message.command[1:])
                sent_message = await message.reply_text("**Processing....**", quote=True)
                creds = flow.step2_exchange(stepsils)
                token = pickle.dumps(creds)
                await db.gdrive_user(user_id, token)
                logger.info(f"Successfully Logged in: {user_id}")
                await sent_message.edit("Successfully Logged In ✅")
                flow = None
                parents_id = await db.get_parent(user_id)
                gdrive = GoogleDrive(user_id, creds)
                if parents_id is None:
                    file_id = gdrive.createRemoteFolder(drive_folder_name)
                    await db.set_parent(user_id, parent_id=file_id)
                    logger.info(f"Folder 📁 Created ✅ ")

                else:
                    try:
                        files_list = gdrive.getFilesByFolderId(parents_id)
                    except Exception as a:
                        logger.info(f"⚠️ Folder id Error: {a}")

                    if not files_list:
                        logger.info(f"⚠️ Files not found from Folder id")
                        file_id = gdrive.createRemoteFolder(drive_folder_name)
                        await db.set_parent(user_id, parent_id=file_id)
                        logger.info(f"Folder 📁 updated ")

            except FlowExchangeError:
                await sent_message.edit(INVALID_CODE)
            except Exception as e:
                await sent_message.edit(f"⚠️ **Error:** `{e}`")
    
        else:
            await message.reply_text("⚠️ **Invalid code**\nGenerate new Authorisation Code by using /login Command", quote=True)

async def Google_Drive_Upload(client, message, files=None, mimetype=None):
    user_id = message.from_user.id
    gdrivez = await db.get_gdrive_status(user_id)
    if gdrivez["is_verified"]:
        token = gdrivez["token"]
        token = pickle.loads(token)
    else:
        messages = f"⚠️ You haven't logged in yet.\n\n👉 So, please /login first"
        return messages

    parents_id = await db.get_parent(user_id)
    gdrive = GoogleDrive(user_id, token)
    if parents_id is None:
        file_id = gdrive.createRemoteFolder(drive_folder_name)
        await db.set_parent(user_id, parent_id=file_id)
        logger.info(f"Folder 📁 Created ✅ ")

    else:
        try:
            files_list = gdrive.getFilesByFolderId(parents_id)
        except Exception as a:
            logger.info(f"⚠️ Folder id Error: {a}")

        if not files_list:
            logger.info(f"⚠️ Files not found from Folder id")
            file_id = gdrive.createRemoteFolder(drive_folder_name)
            await db.set_parent(user_id, parent_id=file_id)
            logger.info(f"Folder 📁 updated ")

    parent_id = await db.get_parent(user_id)
    successful, msg = GoogleDrive(user_id, token, parent_id).upload_file(files, mimetype)
    return successful, msg

'''
return example:
        successful, msg = await Google_Drive_Upload(client, message, file_path, file.mime_type)
        if successful:
            await sent_message.edit(f"Successfully Uploaded to Gdrive ✅\n\n**Link:** {msg}")
        else:
            await sent_message.edit(f"{msg}")
'''
# ---------------
@Client.on_message(filters.private & filters.command(["setfolder"]))
async def _set_parent(client, message):
    user_id = message.from_user.id
    gdrivez = await db.get_gdrive_status(user_id)
    if gdrivez["is_verified"]:
        token = gdrivez["token"]
        token = pickle.loads(token)
    else:
        await message.reply_text(f"⚠️ You haven't logged in yet.\n\n👉 So, please /login first", quote=True)
        return
    if len(message.command) > 1:
        link = message.command[1]
        if not "clear" in link:
            sent_message = await message.reply_text("**Processing....**")
            gdrive = GoogleDrive(user_id, token)
            try:
                result, file_id = gdrive.checkFolderLink(link)
                if result:
                    await db.set_parent(user_id, parent_id=file_id)
                    logger.info(f"SetParent:{user_id}: {file_id}")
                    await sent_message.edit("✅ Successfully Linked Custom Folder")
                    
                else:
                    await sent_message.edit(file_id)
            except IndexError:
                await sent_message.edit("⚠️ Invalid folder link\n\n👉 Please provide a Correct Folder Link in format /setfolder (drive folder link)")
        else:
            await db.set_parent(user_id, parent_id=None)
            cm = f"🗑️**Custom Folder ID Cleared Successfuly.**\n\n➩ Use /setfolder (Folder Link) To Set a folder."
            await message.reply_text(cm, quote=True)
    else:
        CURRENT_FOLDER = "**Your Current Folder ID - `{}`**\n\n➩ Use /setfolder (Folder link) To Change It."
        await message.reply_text(
            CURRENT_FOLDER.format(
                await db.get_parent(user_id),
            ),
            quote=True,
        )


#----------------- Engine ----------------#
class GoogleDrive:
    def __init__(self, user_id, token, parents_id=None):
        self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__G_DRIVE_BASE_DOWNLOAD_URL = (
            "https://drive.google.com/uc?id={}&export=download"
        )
        self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = (
            "https://drive.google.com/drive/folders/{}"
        )
        self.__service = self.authorize(token)
        self.__parent_id = parents_id

    def getIdFromUrl(self, link: str):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex, link)
            if res is None:
                raise IndexError("GDrive ID not found.")
            return res.group(5)
        parsed = urlparse.urlparse(link)
        return parse_qs(parsed.query)["id"][0]

    def getFilesByFolderId(self, folder_id):
        page_token = None
        q = f"'{folder_id}' in parents"
        files = []
        while True:
            response = (
                self.__service.files()
                .list(
                    supportsTeamDrives=True,
                    includeTeamDriveItems=True,
                    q=q,
                    spaces="drive",
                    pageSize=200,
                    fields="nextPageToken, files(id, name, mimeType,size)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                files.append(file)
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        return files
   
    def create_directory(self, directory_name):
        file_metadata = {
            "name": directory_name,
            "mimeType": self.__G_DRIVE_DIR_MIME_TYPE,
        }
        file_metadata["parents"] = [self.__parent_id]
        file = (
            self.__service.files()
            .create(supportsTeamDrives=True, body=file_metadata)
            .execute()
        )
        file_id = file.get("id")
        return file_id

    def createRemoteFolder(self, folderName, parentID = None):
        body = {
          'name': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [parentID]
        root_folder = ( 
            self.__service.files()
            .create(supportsTeamDrives=True, body = body)
            .execute()
        )
        file_id = root_folder.get("id")
        return file_id

    def upload_file(self, file_path, mimeType=None):
        mime_type = mimeType if mimeType else guess_type(file_path)[0]
        mime_type = mime_type if mime_type else "text/plain"
        media_body = MediaFileUpload(
            file_path, mimetype=mime_type, chunksize=150 * 1024 * 1024, resumable=True
        )
        filename = os.path.basename(file_path)
        body = {
            "name": filename,
            "description": "",
            "mimeType": mime_type,
        }
        body["parents"] = [self.__parent_id]
        try:
            uploaded_file = (
                self.__service.files()
                .create(
                    body=body,
                    media_body=media_body,
                    fields="id",
                    supportsTeamDrives=True,
                )
                .execute()
            )
            file_id = uploaded_file.get("id")
            logger.info(f"Successfully Uploaded to Gdrive ✅ {file_path}")
            drive_link = self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file_id)
            return True, drive_link

        except HttpError as err:
            if err.resp.get("content-type", "").startswith("application/json"):
                reason = (
                    json.loads(err.content).get("error").get("errors")[0].get("reason")
                )
                if reason == "userRateLimitExceeded" or reason == "dailyLimitExceeded":
                    messages = "🤔 It seems, Reached User Limit. You can try Again"
                    return False, messages
 
                else:
                    logger.info(f"Error : {reason}")
                    messages = f"**⚠️ Unknown Error Occured** !!!\n\nPlease try again"
                    return False, messages 

        except Exception as e:
            messages = f"⚠️ **Error:** `{e}`"
            return False, messages

    def checkFolderLink(self, link: str):
        try:
            file_id = self.getIdFromUrl(link)
        except (IndexError, KeyError):
            raise IndexError
        try:
            file = (
                self.__service.files()
                .get(supportsAllDrives=True, fileId=file_id, fields="mimeType")
                .execute()
            )
        except HttpError as err:
            if err.resp.get("content-type", "").startswith("application/json"):
                reason = (
                    json.loads(err.content).get("error").get("errors")[0].get("reason")
                )
                if "notFound" in reason:
                    file_nfound = "⚠️ **File/Folder Not Found.**\nFile id - {} Not Found. Make Sure It's Exists And Accessible by the logged account"
                    return False, file_nfound.format(file_id)
                else:
                    err_text = f"⚠️ **Error:** `{str(err).replace('>', '').replace('<', '')}`"                  
                    return False, err_text
                        
        if str(file.get("mimeType")) == self.__G_DRIVE_DIR_MIME_TYPE:
            return True, file_id
        else:
            invalid_folder = "⚠️ Your provided folder link is invalid"
            return False, invalid_folder

    def authorize(self, creds):
        return build("drive", "v3", credentials=creds, cache_discovery=False)
