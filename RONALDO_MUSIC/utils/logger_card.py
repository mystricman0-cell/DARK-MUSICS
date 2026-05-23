import asyncio
import config
from RONALDO_MUSIC.misc import db

_logger_msgs = {}
_updater_running = False


def _fmt(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _progress_bar(played: int, total: int, length: int = 16) -> str:
    if total <= 0:
        return "▱" * length
    frac = min(played / total, 1.0)
    filled = int(frac * length)
    return "▰" * filled + "▱" * (length - filled)


def _build_card(title: str, user: str, group: str, orig_id: int, stype: str, played: int, total: int) -> str:
    bar = _progress_bar(played, total)
    pct = int(min(played / total, 1.0) * 100) if total > 0 else 0
    dur_str = f"{_fmt(played)} / {_fmt(total)}" if total > 0 else "🔴 Live Stream"
    emoji = "🎬" if stype == "VIDEO" else "🎵"
    return (
        f"╔═══〔 {emoji} <b>𝗡𝗢𝗪 𝗣𝗟𝗔𝗬𝗜𝗡𝗚</b> 〕═══╗\n\n"
        f"📌 <b>Song    :</b> {title}\n"
        f"👤 <b>Req by  :</b> {user}\n"
        f"🏠 <b>Group   :</b> {group}\n"
        f"🆔 <b>Chat ID :</b> <code>{orig_id}</code>\n"
        f"🎧 <b>Type    :</b> {stype}\n\n"
        f"⏳ <b>Progress</b>\n"
        f"▶ <code>{bar}</code> {pct}%\n"
        f"   ⏱ <b>{dur_str}</b>\n\n"
        f"╚══════════════════════════╝"
    )


async def _progress_updater():
    global _updater_running
    while True:
        await asyncio.sleep(4)
        for vc_chat_id in list(_logger_msgs.keys()):
            try:
                playing = db.get(vc_chat_id)
                if not playing:
                    _logger_msgs.pop(vc_chat_id, None)
                    continue
                played = int(playing[0].get("played", 0))
                info = _logger_msgs[vc_chat_id]
                total = info["total"]
                new_text = _build_card(
                    info["title"], info["user"], info["group"],
                    info["orig_id"], info["stype"], played, total,
                )
                try:
                    await info["msg"].edit_text(new_text)
                except Exception:
                    pass
            except Exception:
                continue


async def send_logger_card(
    vc_chat_id: int,
    original_chat_id: int,
    title: str,
    user: str,
    stype: str = "AUDIO",
):
    global _updater_running
    from RONALDO_MUSIC import app
    try:
        chat = await app.get_chat(original_chat_id)
        group_name = getattr(chat, "title", None) or "Private"
    except Exception:
        group_name = str(original_chat_id)
    try:
        playing = db.get(vc_chat_id)
        total = int(playing[0].get("seconds", 0)) if playing else 0
    except Exception:
        total = 0
    try:
        text = _build_card(title, user, group_name, original_chat_id, stype, 0, total)
        msg = await app.send_message(config.LOGGER_ID, text)
        _logger_msgs[vc_chat_id] = {
            "msg": msg,
            "total": total,
            "title": title,
            "user": user,
            "stype": stype,
            "group": group_name,
            "orig_id": original_chat_id,
        }
        if not _updater_running:
            _updater_running = True
            asyncio.create_task(_progress_updater())
    except Exception:
        pass


def remove_logger_card(vc_chat_id: int):
    _logger_msgs.pop(vc_chat_id, None)
