"""Reusable database repositories and export helpers."""
from __future__ import annotations

import csv
import io
from typing import Any

import orjson
from sqlalchemy import select

from database.models import Backup, Log, Setting, Ticket, XP
from database.session import session_scope


def set_setting(guild_id: int | str, key: str, value: Any) -> None:
    payload = orjson.dumps(value).decode() if not isinstance(value, str) else value
    with session_scope() as session:
        row = session.scalar(select(Setting).where(Setting.guild_id == str(guild_id), Setting.key == key))
        if row:
            row.value = payload
        else:
            session.add(Setting(guild_id=str(guild_id), key=key, value=payload))


def get_setting(guild_id: int | str, key: str, default: Any = None) -> Any:
    with session_scope() as session:
        row = session.scalar(select(Setting).where(Setting.guild_id == str(guild_id), Setting.key == key))
        if not row:
            return default
        try:
            return orjson.loads(row.value)
        except orjson.JSONDecodeError:
            return row.value


def log_event(guild_id: int | str, event: str, details: str = "", actor_id: int | str | None = None, target_id: int | str | None = None) -> None:
    with session_scope() as session:
        session.add(Log(guild_id=str(guild_id), event=event, details=details, actor_id=str(actor_id) if actor_id else None, target_id=str(target_id) if target_id else None))


def add_xp(guild_id: int | str, user_id: int | str, amount: int) -> tuple[int, int, bool]:
    with session_scope() as session:
        row = session.scalar(select(XP).where(XP.guild_id == str(guild_id), XP.user_id == str(user_id)))
        if not row:
            row = XP(guild_id=str(guild_id), user_id=str(user_id), xp=0, level=0)
            session.add(row)
        old = row.level
        row.xp += amount
        row.level = int((row.xp / 100) ** 0.5)
        return row.xp, row.level, row.level > old


def leaderboard(guild_id: int | str, limit: int = 10) -> list[XP]:
    with session_scope() as session:
        return list(session.scalars(select(XP).where(XP.guild_id == str(guild_id)).order_by(XP.xp.desc()).limit(limit)))


def export_table(model: type, fmt: str = "json") -> str:
    with session_scope() as session:
        rows = [r.__dict__ for r in session.scalars(select(model)).all()]
    cleaned = [{k: str(v) for k, v in row.items() if not k.startswith("_")} for row in rows]
    if fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cleaned[0].keys() if cleaned else ["empty"])
        writer.writeheader(); writer.writerows(cleaned)
        return output.getvalue()
    return orjson.dumps(cleaned, option=orjson.OPT_INDENT_2).decode()


def save_backup(guild_id: int | str, name: str, payload: dict[str, Any]) -> int:
    with session_scope() as session:
        backup = Backup(guild_id=str(guild_id), name=name, payload=orjson.dumps(payload).decode())
        session.add(backup); session.flush()
        return backup.id
