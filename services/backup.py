"""Discord guild backup and restore service."""
from __future__ import annotations

from typing import Any

import discord


def serialize_guild(guild: discord.Guild) -> dict[str, Any]:
    return {
        "roles": [{"name": r.name, "permissions": r.permissions.value, "color": r.color.value, "hoist": r.hoist, "mentionable": r.mentionable} for r in guild.roles if not r.is_default()],
        "categories": [{"name": c.name, "position": c.position} for c in guild.categories],
        "channels": [{"name": c.name, "type": str(c.type), "category": c.category.name if c.category else None, "position": c.position} for c in guild.channels],
    }


async def restore_roles(guild: discord.Guild, payload: dict[str, Any]) -> int:
    count = 0
    for role in payload.get("roles", []):
        if discord.utils.get(guild.roles, name=role["name"]):
            continue
        await guild.create_role(name=role["name"], permissions=discord.Permissions(role["permissions"]), color=discord.Color(role["color"]), hoist=role["hoist"], mentionable=role["mentionable"], reason="Backup restore")
        count += 1
    return count
