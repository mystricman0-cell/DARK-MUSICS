import random
from pyrogram import filters
from RONALDO_MUSIC import app


def get_random_sticker():
    stickers = [
        "CAACAgQAAx0Ce9_hCAACaEVlwn7HeZhgwyVfKHc3WUGC_447IAACLgwAAkQwKVPtub8VAR018x4E",
        "CAACAgIAAx0Ce9_hCAACaEplwn7dvj7G0-a1v3wlbN281RMX2QACUgwAAligOUoi7DhLVTsNsh4E",
        "CAACAgIAAx0Ce9_hCAACaFBlwn8AAZNB9mOUvz5oAyM7CT-5pjAAAtEKAALa7NhLvbTGyDLbe1IeBA",
        "CAACAgUAAx0CcmOuMwACldVlwn9ZHHF2-S-CuMSYabwwtVGC3AACOAkAAoqR2VYDjyK6OOr_Px4E",
        "CAACAgIAAx0Ce9_hCAACaFVlwn-fG58GKoEmmZpVovxEj4PodAACfwwAAqozQUrt2xSTf5Ac4h4E",
    ]
    return random.choice(stickers)


def get_random_emoji():
    return random.choice(["😴", "😪", "💤"])


@app.on_message(filters.command(["gn", "goodnight"], prefixes=["/", "g", "G"]))
async def goodnight_command_handler(_, message):
    sender = message.from_user.mention
    send_sticker = random.choice([True, False])
    try:
        if send_sticker:
            sticker_id = get_random_sticker()
            await app.send_sticker(message.chat.id, sticker_id)
            await message.reply_text(f"**Goodnight, {sender}! Sleep tight. 🌙**")
        else:
            emoji = get_random_emoji()
            await message.reply_text(f"**Goodnight, {sender}! Sleep tight. {emoji}**")
    except Exception as e:
        await message.reply_text(f"Goodnight, {sender}! 🌙")
