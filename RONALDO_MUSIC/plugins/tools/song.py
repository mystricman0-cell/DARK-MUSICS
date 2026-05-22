import os
import asyncio

import requests
import yt_dlp
from pyrogram import filters
from youtube_search import YoutubeSearch
from RONALDO_MUSIC import app

from config import SUPPORT_CHAT, BANNED_USERS


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


@app.on_message(filters.command(["song", "music"]) & ~BANNED_USERS)
async def song(client, message):
    try:
        await message.delete()
    except Exception:
        pass

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)

    if not query.strip():
        return await message.reply("**» sᴏɴɢ ɴᴀᴍᴇ ᴅᴏ ʙᴀʙʏ!**")

    m = await message.reply("**» sᴇᴀʀᴄʜɪɴɢ, ᴩʟᴇᴀsᴇ ᴡᴀɪᴛ...**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        views = results[0]["views"]
    except Exception as e:
        await m.edit(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴀᴛ ʟɪᴋʜᴀ ʜᴏ!"
        )
        return

    await m.edit("» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...\n\nᴩʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=False))
            audio_file = ydl.prepare_filename(info_dict)
            await loop.run_in_executor(None, lambda: ydl.process_info(info_dict))

        rep = (
            f"**ᴛɪᴛʟᴇ :** {title[:25]}\n"
            f"**ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}`\n"
            f"**ᴠɪᴇᴡs :** `{views}`\n"
            f"**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ »** {chutiya}"
        )
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        await message.reply_audio(
            audio_file,
            caption=rep,
            performer=app.name,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        await m.delete()
    except Exception as e:
        await m.edit(
            f"**» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴇʀʀᴏʀ, ʀᴇᴩᴏʀᴛ ᴀᴛ » [sᴜᴩᴩᴏʀᴛ](t.me/{SUPPORT_CHAT}) 💕**\n\n**ᴇʀʀᴏʀ :** {e}"
        )

    for f in [locals().get("audio_file"), locals().get("thumb_name")]:
        if f:
            try:
                os.remove(f)
            except Exception:
                pass
