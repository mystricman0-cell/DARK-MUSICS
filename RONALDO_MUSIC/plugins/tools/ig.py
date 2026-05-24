import re
import aiohttp
from pyrogram import filters

from RONALDO_MUSIC import app
from config import LOGGER_ID, BANNED_USERS

_IG_APIS = [
    "https://insta-dl.hazex.workers.dev/?url={url}",
    "https://api.instagramdl.workers.dev/?url={url}",
]
_IG_RE = re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$")


async def _fetch_ig(url: str) -> dict | None:
    for api_tpl in _IG_APIS:
        api_url = api_tpl.format(url=url)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15)
            ) as session:
                async with session.get(api_url) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json(content_type=None)
                    if not data.get("error") and data.get("result"):
                        return data["result"]
        except Exception:
            continue
    return None


@app.on_message(filters.command(["ig", "instagram", "reel"]) & ~BANNED_USERS)
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "📸 **Instagram Reel Downloader**\n\n"
            "**Usage:** `/ig <instagram_reel_url>`"
        )
    url = message.text.split()[1]
    if not _IG_RE.match(url):
        return await message.reply_text(
            "❌ Invalid Instagram URL.\n\nProvide a valid Instagram post/reel link."
        )
    a = await message.reply_text("⬇️ **Downloading reel...**")
    try:
        result = await _fetch_ig(url)
        if not result:
            return await a.edit(
                "❌ **Failed to download reel.**\n\n"
                "Instagram may have restricted this reel or the URL is private."
            )
        video_url = result.get("url", "")
        duration = result.get("duration", "?")
        quality = result.get("quality", "?")
        ext = result.get("extension", "mp4")
        size = result.get("formattedSize", "?")
        caption = (
            f"✅ **Instagram Reel**\n\n"
            f"⏱ Duration: `{duration}`\n"
            f"📺 Quality: `{quality}`\n"
            f"📁 Type: `{ext}` | Size: `{size}`"
        )
        await a.delete()
        await message.reply_video(video_url, caption=caption)
    except Exception as e:
        try:
            await a.edit(f"❌ Error: `{type(e).__name__}: {e}`")
        except Exception:
            await message.reply_text(f"❌ Error: `{e}`")


MODULE = "Rᴇᴇʟ"
HELP = """
ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ:

• /ig [URL]: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
• /instagram [URL]: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
• /reel [URL]: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
"""
