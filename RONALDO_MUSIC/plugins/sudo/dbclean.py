import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from RONALDO_MUSIC import app
from RONALDO_MUSIC.core.mongo import mongodb
from RONALDO_MUSIC.utils.mongo import afkdb, coupledb, filtersdb, nightmodedb, notesdb
from config import BANNED_USERS, OWNER_IDS


def _owners():
    return filters.user(OWNER_IDS)


async def _count_col(col) -> int:
    try:
        return await col.count_documents({})
    except Exception:
        return 0


async def _do_clean():
    results = {}

    afkdb_col = mongodb["afk"] if hasattr(mongodb, "__getitem__") else afkdb
    authdb = mongodb.adminauth
    authuserdb = mongodb.authuser
    assdb = mongodb.assistants
    countdb = mongodb.upcount
    connectdb = mongodb.connect
    langdb = mongodb.language
    playmodedb = mongodb.playmode
    playtypedb = mongodb.playtypedb
    skipdb = mongodb.skipmode
    playlistdb = mongodb.playlist

    deleted = {}

    try:
        before = await _count_col(afkdb)
        r = await afkdb.delete_many({})
        deleted["AFK entries"] = r.deleted_count
    except Exception:
        deleted["AFK entries"] = 0

    try:
        before = await _count_col(playlistdb)
        r = await playlistdb.delete_many({"notes": {}})
        deleted["Empty playlists"] = r.deleted_count
    except Exception:
        deleted["Empty playlists"] = 0

    try:
        r = await countdb.delete_many({"mode": {"$lte": 0}})
        deleted["Stale upvote configs"] = r.deleted_count
    except Exception:
        deleted["Stale upvote configs"] = 0

    try:
        r = await nightmodedb.delete_many({"mode": {"$exists": False}})
        deleted["Bad nightmode docs"] = r.deleted_count
    except Exception:
        deleted["Bad nightmode docs"] = 0

    try:
        r = await filtersdb.delete_many({"filters": {}})
        deleted["Empty filter docs"] = r.deleted_count
    except Exception:
        deleted["Empty filter docs"] = 0

    try:
        r = await notesdb.delete_many({"notes": {}})
        deleted["Empty note docs"] = r.deleted_count
    except Exception:
        deleted["Empty note docs"] = 0

    try:
        r = await coupledb.delete_many({"couple": {}})
        deleted["Empty couple docs"] = r.deleted_count
    except Exception:
        deleted["Empty couple docs"] = 0

    try:
        r = await playmodedb.delete_many({"mode": {"$in": [None, ""]}})
        deleted["Broken playmode docs"] = r.deleted_count
    except Exception:
        deleted["Broken playmode docs"] = 0

    try:
        r = await playtypedb.delete_many({"mode": {"$in": [None, ""]}})
        deleted["Broken playtype docs"] = r.deleted_count
    except Exception:
        deleted["Broken playtype docs"] = 0

    try:
        r = await langdb.delete_many({"lang": {"$in": [None, ""]}})
        deleted["Broken language docs"] = r.deleted_count
    except Exception:
        deleted["Broken language docs"] = 0

    return deleted


def _build_clean_card(deleted: dict, requester: str) -> str:
    total = sum(deleted.values())
    lines = ""
    for k, v in deleted.items():
        icon = "🟢" if v > 0 else "⚪"
        lines += f"  {icon} <b>{k}:</b> <code>{v}</code>\n"
    return (
        f"╔══〔 🧹 <b>𝗠𝗢𝗡𝗚𝗢 𝗗𝗕 𝗖𝗟𝗘𝗔𝗡𝗘𝗗</b> 〕══╗\n\n"
        f"{lines}\n"
        f"🗑 <b>Total Removed :</b> <code>{total}</code> documents\n"
        f"👤 <b>Cleaned by :</b> {requester}\n"
        f"💾 <b>Status :</b> MongoDB is now optimised ✅\n\n"
        f"╚════════════════════════════╝"
    )


@app.on_message(
    filters.command(["dbclean", "cleandb", "mongoclean", "dbflush"], prefixes=["/", "!", "."])
    & _owners()
    & ~BANNED_USERS
)
async def db_clean_cmd(client, message: Message):
    msg = await message.reply_text(
        "🔄 <b>Scanning MongoDB for junk data...</b>\n"
        "<i>Please wait, this may take a few seconds.</i>"
    )
    try:
        deleted = await asyncio.wait_for(_do_clean(), timeout=30)
        card = _build_clean_card(deleted, message.from_user.mention)
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Done", callback_data="close_dbclean")]]
        )
        await msg.edit_text(card, reply_markup=button)
    except asyncio.TimeoutError:
        await msg.edit_text("⚠️ Cleanup timed out. MongoDB may be slow. Try again.")
    except Exception as e:
        await msg.edit_text(f"❌ Error during cleanup:\n<code>{e}</code>")


@app.on_callback_query(filters.regex("^close_dbclean$"))
async def close_dbclean_cb(client, callback_query):
    try:
        await callback_query.message.delete()
    except Exception:
        await callback_query.answer("Done!", show_alert=False)
