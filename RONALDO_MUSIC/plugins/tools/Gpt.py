import asyncio
import urllib.parse
import urllib.request

from pyrogram import filters
from pyrogram.enums import ChatAction

import config
from RONALDO_MUSIC import app

BANNED_USERS = config.BANNED_USERS


async def _ask_pollinations(prompt: str) -> str:
    """
    Free AI text endpoint — no API key required.
    https://text.pollinations.ai/{prompt}
    """
    encoded = urllib.parse.quote(prompt, safe="")
    url = f"https://text.pollinations.ai/{encoded}"

    loop = asyncio.get_running_loop()

    def _fetch():
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")

    result = await loop.run_in_executor(None, _fetch)
    return result.strip()


@app.on_message(filters.command(["chatgpt", "ai", "ask", "gemini"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "**Usage:** `/ai your question here`\n\n"
            "Example:\n`/ai write a simple website in HTML CSS JS`"
        )

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    thinking = await message.reply_text("🤖 **Thinking...**")

    try:
        result = await _ask_pollinations(user_input)
        if not result:
            raise ValueError("Empty response")
        await thinking.edit_text(result[:4096])
    except Exception as e:
        await thinking.edit_text(
            f"⚠️ AI request failed: `{type(e).__name__}: {e}`\n\n"
            "Please try again in a moment."
        )


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ AI
/chatgpt [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/ask [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/gemini [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai"""
