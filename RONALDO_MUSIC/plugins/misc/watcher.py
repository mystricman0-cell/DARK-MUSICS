from pyrogram import filters
from pyrogram.types import Message

from RONALDO_MUSIC import app
from RONALDO_MUSIC.core.call import RONALDO

_GROUP_WELCOME = 20
_GROUP_CLOSE = 30


@app.on_message(filters.video_chat_started, group=_GROUP_WELCOME)
@app.on_message(filters.video_chat_ended, group=_GROUP_CLOSE)
async def vc_watcher(_, message: Message):
    await RONALDO.stop_stream_force(message.chat.id)
