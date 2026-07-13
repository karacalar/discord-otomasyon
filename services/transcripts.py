"""Ticket transcript generation."""
from __future__ import annotations

import html

import discord


async def build_transcript(channel: discord.TextChannel) -> str:
    """Build an HTML transcript for a text channel."""
    parts = ["<html><head><meta charset='utf-8'><title>Transcript</title>", "<style>body{font-family:Arial}.msg{border-bottom:1px solid #ddd;padding:8px}</style></head><body>"]
    async for msg in channel.history(limit=None, oldest_first=True):
        author = html.escape(str(msg.author))
        content = html.escape(msg.content)
        parts.append(f"<div class='msg'><b>{author}</b> <small>{msg.created_at}</small><p>{content}</p></div>")
    parts.append("</body></html>")
    return "".join(parts)
