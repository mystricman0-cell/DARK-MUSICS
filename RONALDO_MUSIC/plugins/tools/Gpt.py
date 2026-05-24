import asyncio
import json
import os
import urllib.parse
import urllib.request

from pyrogram import filters
from pyrogram.enums import ChatAction

import config
from RONALDO_MUSIC import app

BANNED_USERS = config.BANNED_USERS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def _ask_openai(prompt: str) -> str:
    """Use real OpenAI ChatGPT API if OPENAI_API_KEY is set."""
    loop = asyncio.get_running_loop()

    def _fetch():
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "RONALDO-MUSIC-BOT",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"].strip()

    return await loop.run_in_executor(None, _fetch)


async def _ask_pollinations(prompt: str) -> str:
    """Free ChatGPT-powered fallback — no API key needed."""
    loop = asyncio.get_running_loop()

    def _fetch():
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Answer clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            "model": "openai",
            "seed": 42,
        }).encode()
        req = urllib.request.Request(
            "https://text.pollinations.ai/openai",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"].strip()

    return await loop.run_in_executor(None, _fetch)


async def ask_ai(prompt: str) -> str:
    """Auto-select: real OpenAI if key set, else free pollinations fallback."""
    if OPENAI_API_KEY:
        return await _ask_openai(prompt)
    return await _ask_pollinations(prompt)


@app.on_message(filters.command(["chatgpt", "ai", "ask", "gemini"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "🤖 **ChatGPT AI**\n\n"
            "**Usage:** `/ai your question here`\n\n"
            "**Example:**\n`/ai write a simple website in HTML CSS JS`\n"
            "`/ai explain black holes in simple words`"
        )

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    thinking = await message.reply_text("🤖 **ChatGPT is thinking...**")

    try:
        result = await ask_ai(user_input)
        if not result:
            raise ValueError("Empty response from AI")
        if len(result) > 4096:
            result = result[:4090] + "\n..."
        await thinking.edit_text(f"🤖 **AI Response:**\n\n{result}")
    except Exception as e:
        await thinking.edit_text(
            f"⚠️ **AI request failed:** `{type(e).__name__}`\n\n"
            "Please try again in a moment."
        )


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ᴄʜᴀᴛɢᴘᴛ ᴀɪ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ
/chatgpt [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/ask [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/gemini [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai"""
