import asyncio
import json
import os
import urllib.request
import urllib.error

from pyrogram import filters
from pyrogram.enums import ChatAction

import config
from RONALDO_MUSIC import app

BANNED_USERS = config.BANNED_USERS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

_AI_ENDPOINTS = [
    {
        "url": "https://text.pollinations.ai/openai",
        "build": lambda prompt: json.dumps({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Answer clearly and concisely."},
                {"role": "user", "content": prompt},
            ],
            "model": "openai",
            "seed": 42,
        }).encode(),
        "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        "parse": lambda data: data["choices"][0]["message"]["content"].strip(),
    },
    {
        "url": "https://api.openai.com/v1/chat/completions",
        "build": lambda prompt: json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7,
        }).encode(),
        "headers": {
            "Authorization": f"Bearer {OPENAI_API_KEY}" if OPENAI_API_KEY else "",
            "Content-Type": "application/json",
            "User-Agent": "RONALDO-MUSIC-BOT",
        },
        "parse": lambda data: data["choices"][0]["message"]["content"].strip(),
        "requires_key": True,
    },
]


async def ask_ai(prompt: str) -> str:
    loop = asyncio.get_running_loop()

    endpoints = [e for e in _AI_ENDPOINTS if not e.get("requires_key") or OPENAI_API_KEY]

    for ep in endpoints:
        try:
            def _fetch(ep=ep):
                req = urllib.request.Request(
                    ep["url"],
                    data=ep["build"](prompt),
                    headers=ep["headers"],
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=25) as r:
                    data = json.loads(r.read().decode())
                return ep["parse"](data)

            result = await asyncio.wait_for(loop.run_in_executor(None, _fetch), timeout=28)
            if result:
                return result
        except Exception:
            continue

    raise Exception("All AI endpoints failed. Try again later.")


@app.on_message(filters.command(["chatgpt", "ai", "ask", "gemini", "gpt"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "🤖 **ChatGPT AI**\n\n"
            "**Usage:** `/ai your question here`\n\n"
            "**Examples:**\n"
            "`/ai write a poem about music`\n"
            "`/ai explain black holes simply`\n"
            "`/ai translate hello to Hindi`"
        )

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    thinking = await message.reply_text("🤖 **AI is thinking...**")

    try:
        result = await ask_ai(user_input)
        if len(result) > 4096:
            result = result[:4090] + "\n..."
        await thinking.edit_text(f"🤖 **AI Response:**\n\n{result}")
    except Exception as e:
        await thinking.edit_text(
            "⚠️ **AI unavailable right now.**\n\nPlease try again in a moment."
        )


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ᴀɪ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ
/chatgpt [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/ask [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/gpt [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai
/gemini [ǫᴜᴇʀʏ] - sᴀᴍᴇ ᴀs /ai"""
