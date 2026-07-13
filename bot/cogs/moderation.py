"""Auto moderation, warnings, timeouts and logging."""
from __future__ import annotations

from datetime import timedelta
import re
import time

import discord
from discord import app_commands
from discord.ext import commands

from database.models import Warning
from database.session import session_scope
from services.repository import get_setting, log_event

INVITE_RE = re.compile(r"discord(?:\.gg|\.com/invite)/", re.I)
URL_RE = re.compile(r"https?://", re.I)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot; self.messages: dict[tuple[int, int], list[float]] = {}

    async def punish(self, message: discord.Message, reason: str) -> None:
        await message.delete()
        log_event(message.guild.id, "automod", reason, target_id=message.author.id)
        with session_scope() as s: s.add(Warning(guild_id=str(message.guild.id), user_id=str(message.author.id), moderator_id=str(self.bot.user.id), reason=reason))
        if isinstance(message.author, discord.Member):
            try: await message.author.timeout(timedelta(minutes=5), reason=reason)
            except discord.Forbidden: pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot: return
        log_event(message.guild.id, "message", message.content[:500], target_id=message.author.id)
        cfg = get_setting(message.guild.id, "automod", {"enabled": True, "bad_words": []})
        if not cfg.get("enabled", True): return
        now = time.time(); key = (message.guild.id, message.author.id)
        self.messages.setdefault(key, []).append(now); self.messages[key] = [t for t in self.messages[key] if now - t < 8]
        if len(self.messages[key]) > 6: return await self.punish(message, "Spam detection")
        content = message.content
        if cfg.get("block_links") and URL_RE.search(content): return await self.punish(message, "Link protection")
        if cfg.get("block_invites", True) and INVITE_RE.search(content): return await self.punish(message, "Invite link protection")
        if len(message.mentions) >= int(cfg.get("max_mentions", 5)): return await self.punish(message, "Mass mention protection")
        letters = [c for c in content if c.isalpha()]
        if len(letters) > 12 and sum(c.isupper() for c in letters) / len(letters) > .75: return await self.punish(message, "Caps lock filter")
        if any(w.lower() in content.lower() for w in cfg.get("bad_words", [])): return await self.punish(message, "Bad word filter")

    @app_commands.command(description="Warn a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str) -> None:
        with session_scope() as s: s.add(Warning(guild_id=str(interaction.guild_id), user_id=str(member.id), moderator_id=str(interaction.user.id), reason=reason))
        log_event(interaction.guild_id, "warn", reason, actor_id=interaction.user.id, target_id=member.id)
        await interaction.response.send_message(f"Warned {member.mention}: {reason}", ephemeral=True)

    @app_commands.command(description="Temporarily timeout a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided") -> None:
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        log_event(interaction.guild_id, "timeout", reason, actor_id=interaction.user.id, target_id=member.id)
        await interaction.response.send_message(f"Timed out {member.mention} for {minutes} minutes.", ephemeral=True)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Moderation(bot))
