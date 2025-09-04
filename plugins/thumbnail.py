import logging

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import Database

db = Database()

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# @Client.on_message(filters.private & filters.photo & ~filters.edited)
async def photo_handleoor(bot, update):
    ab = await update.reply_text("Processing....", quote=True)
    await db.set_thumbnail(update.from_user.id, thumbnail=update.photo.file_id)
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Delete Thumbnail ❌", callback_data="deleteThumbnail"
                )
            ],
        ]
    )
    try:
        await ab.edit(
            text="Thumbnail Saved Successfully ✅"
        )  # reply_markup=reply_markup
        logger.info(
            f" Thumbnail Saved Successfully ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    except:
        pass


@Client.on_callback_query()
async def cb_handlers(bot, update):
    if "showThumbnail" in update.data:
        db_thumbnail = await db.get_thumbnail(update.from_user.id)
        if db_thumbnail is not None:
            #    await update.answer("**Processing....**", show_alert=True)
            await bot.send_photo(
                chat_id=update.message.chat.id,
                photo=db_thumbnail,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Delete Thumbnail ❌", callback_data="deleteThumbnail"
                            )
                        ]
                    ]
                ),
            )
            logger.info(
                f" Thumbnail viewed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        else:
            try:
                await update.message.edit("⚠️ Custom Thumbnail not Found")
                logger.info(
                    f" ⚠️ Custom Thumbnail not Found By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
                )
            except:
                pass
    elif "deleteThumbnail" in update.data:
        await db.set_thumbnail(update.from_user.id, thumbnail=None)
        try:
            await update.message.delete()
        except:
            pass
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"Custom Thumbnail Deleted ✅",
            reply_to_message_id=update.message.id,
        )
        #    await update.message.edit("Custom Thumbnail Deleted ✅")
        logger.info(
            f"Custom Thumbnail Deleted ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )

    else:
        raise ContinuePropagation


@Client.on_message(
    filters.private & filters.command(["show_thumbnail", "st", "show_thumb"])
)
async def showthumb_i(bot, update):
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    if db_thumbnail is not None:
        thumb_showbut = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Delete Thumbnail ❌", callback_data="deleteThumbnail"
                    )
                ]
            ]
        )
        try:
            await bot.send_photo(
                chat_id=update.chat.id,
                photo=db_thumbnail,
                reply_markup=thumb_showbut,
                reply_to_message_id=update.id,
            )
            logger.info(
                f" Thumbnail viewed ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
            )
        except:
            await update.reply(
                "⚠️ Custom Thumbnail Expired\n\nSo /delete_thumbnail And Send again",
                reply_to_message_id=update.id,
            )
    else:
        await update.reply(
            "⚠️ Custom Thumbnail not Found", reply_to_message_id=update.id
        )
        logger.info(
            f" ⚠️ No Custom Thumbnail Found By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )


@Client.on_message(
    filters.private & filters.command(["delete_thumbnail", "dt", "del_thumb"])
)
async def delthumb_i(bot, update):
    await db.set_thumbnail(update.from_user.id, thumbnail=None)
    await bot.send_message(
        chat_id=update.chat.id,
        text=f"Custom Thumbnail Deleted ✅",
        reply_to_message_id=update.id,
    )
    logger.info(
        f"Custom Thumbnail Deleted ✅ By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
    )
