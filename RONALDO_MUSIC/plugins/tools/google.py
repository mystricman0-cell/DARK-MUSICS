import logging

from googlesearch import search
from pyrogram import filters

from RONALDO_MUSIC import app
from config import BANNED_USERS


@app.on_message(filters.command(["google", "gle"]) & ~BANNED_USERS)
async def google_search(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("**Usage:** `/google lord ram`")
    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])
    b = await message.reply_text("🔍 **Searching on Google...**")
    try:
        results = list(search(user_input, num_results=5, advanced=True))
        if not results:
            return await b.edit("❌ No results found.")
        txt = f"🔎 **Search:** `{user_input}`\n\n**Results:**"
        for result in results:
            title = getattr(result, 'title', 'No Title')
            url = getattr(result, 'url', '#')
            desc = (getattr(result, 'description', '') or '')[:100]
            txt += f"\n\n[❍ {title}]({url})\n{desc}"
        await b.edit(txt, disable_web_page_preview=True)
    except Exception as e:
        logging.exception(e)
        await b.edit(f"❌ Search failed: `{type(e).__name__}`")


@app.on_message(filters.command(["app", "apps"]) & ~BANNED_USERS)
async def app_search(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/app Free Fire`")
    app_name = " ".join(message.command[1:])
    b = await message.reply_text("🔍 **Searching Play Store...**")
    try:
        results = list(search(f"{app_name} site:play.google.com", num_results=3, advanced=True))
        if not results:
            return await b.edit("❌ App not found on Play Store.")
        r = results[0]
        title = getattr(r, 'title', app_name)
        url = getattr(r, 'url', f"https://play.google.com/store/search?q={app_name}")
        desc = (getattr(r, 'description', '') or 'No description.')[:200]
        text = f"📱 **{title}**\n\n📝 {desc}\n\n🔗 [Open on Play Store]({url})"
        await b.edit(text, disable_web_page_preview=True)
    except Exception as e:
        await b.edit(f"❌ Search failed: `{type(e).__name__}`")


__MODULE__ = "Gᴏᴏɢʟᴇ"
__HELP__ = """/google [ǫᴜᴇʀʏ] - ᴛᴏ sᴇᴀʀᴄʜ ᴏɴ ɢᴏᴏɢʟᴇ ᴀɴᴅ ɢᴇᴛ ʀᴇsᴜʟᴛs
/app | /apps [ᴀᴘᴘ ɴᴀᴍᴇ] - ᴛᴏ ɢᴇᴛ ᴀᴘᴘ ɪɴғᴏ ғʀᴏᴍ ᴘʟᴀʏ sᴛᴏʀᴇ"""


