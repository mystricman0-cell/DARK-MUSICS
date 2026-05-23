import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from RONALDO_MUSIC import YouTube, app
from RONALDO_MUSIC.core.call import RONALDO
from RONALDO_MUSIC.misc import db
from RONALDO_MUSIC.utils.database import set_loop
from RONALDO_MUSIC.utils.decorators import AdminRightsCheck
from RONALDO_MUSIC.utils.inline import close_markup, stream_markup, telegram_markup
from RONALDO_MUSIC.utils.stream.autoclear import auto_clean
from RONALDO_MUSIC.utils.thumbnails import get_thumb
from config import BANNED_USERS


async def _send_closed_msg(chat_id, mention):
    try:
        msg = await app.send_message(
            chat_id,
            f"╔══════════════════╗\n"
            f"   🎵 ꜱᴛʀᴇᴀᴍ ᴄʟᴏꜱᴇᴅ\n"
            f"╚══════════════════╝\n\n"
            f"❌ <b>Closed by :</b> {mention}\n"
            f"🗑 <i>This message will self-destruct...</i>",
        )
        await asyncio.sleep(6)
        await msg.delete()
    except Exception:
        pass


async def _play_next_or_stop(chat_id, mention, message, _):
    check = db.get(chat_id)
    popped = None
    try:
        popped = check.pop(0)
        if popped:
            await auto_clean(popped)
    except Exception:
        pass

    check = db.get(chat_id)
    if not check:
        await RONALDO.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        asyncio.create_task(_send_closed_msg(chat_id, mention))
        return

    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    db[chat_id][0]["played"] = 0

    asyncio.create_task(_send_closed_msg(chat_id, mention))

    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return
        try:
            image = await YouTube.thumbnail(videoid, True)
        except Exception:
            image = None
        try:
            await RONALDO.skip_stream(chat_id, link, video=status, image=image)
        except Exception:
            return
        button = telegram_markup(_, chat_id)
        img = await get_thumb(videoid)
        run = await app.send_photo(
            chat_id,
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23], check[0]["dur"], user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
            has_spoiler=True,
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    elif "vid_" in queued:
        tmp = await app.send_message(chat_id, _["call_7"])
        try:
            file_path, direct = await YouTube.download(videoid, tmp, videoid=True, video=status)
        except Exception:
            try:
                file_path, direct = await YouTube.download(videoid, tmp, videoid=True, video=status)
            except Exception:
                await tmp.delete()
                return
        try:
            image = await YouTube.thumbnail(videoid, True)
        except Exception:
            image = None
        try:
            await RONALDO.skip_stream(chat_id, file_path, video=status, image=image)
        except Exception:
            await tmp.delete()
            return
        button = stream_markup(_, videoid, chat_id)
        img = await get_thumb(videoid)
        run = await app.send_photo(
            chat_id,
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23], check[0]["dur"], user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
            has_spoiler=True,
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
        await tmp.delete()
    elif "index_" in queued:
        try:
            await RONALDO.skip_stream(chat_id, videoid, video=status)
        except Exception:
            return
        button = telegram_markup(_, chat_id)
        run = await app.send_photo(
            chat_id,
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
            has_spoiler=True,
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    else:
        if videoid not in ("telegram", "soundcloud"):
            try:
                image = await YouTube.thumbnail(videoid, True)
            except Exception:
                image = None
        else:
            image = None
        try:
            await RONALDO.skip_stream(chat_id, queued, video=status, image=image)
        except Exception:
            return
        if videoid == "telegram":
            button = telegram_markup(_, chat_id)
            run = await app.send_photo(
                chat_id,
                photo=config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
                has_spoiler=True,
            )
        elif videoid == "soundcloud":
            button = telegram_markup(_, chat_id)
            run = await app.send_photo(
                chat_id,
                photo=config.SOUNCLOUD_IMG_URL,
                caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
                has_spoiler=True,
            )
        else:
            button = stream_markup(_, videoid, chat_id)
            img = await get_thumb(videoid)
            run = await app.send_photo(
                chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23], check[0]["dur"], user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
                has_spoiler=True,
            )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg" if videoid in ("telegram", "soundcloud") else "stream"


@app.on_message(
    filters.command(["end", "stop", "cend", "cstop"], prefixes=["/", "!", "."])
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    mention = message.from_user.mention
    await message.delete()
    await _play_next_or_stop(chat_id, mention, message, _)
