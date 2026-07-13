"""Audit and server event logging."""
from __future__ import annotations

import discord
from discord.ext import commands
from services.repository import log_event

class EventLogging(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @commands.Cog.listener()
    async def on_message_delete(self, m: discord.Message) -> None:
        if m.guild: log_event(m.guild.id, "message_delete", m.content[:500], target_id=m.author.id)
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.guild: log_event(before.guild.id, "message_edit", f"{before.content[:250]} -> {after.content[:250]}", target_id=before.author.id)
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.nick != after.nick: log_event(after.guild.id, "nickname_change", f"{before.nick} -> {after.nick}", target_id=after.id)
        if before.roles != after.roles: log_event(after.guild.id, "role_update", "Member roles changed", target_id=after.id)
        if before.timed_out_until != after.timed_out_until: log_event(after.guild.id, "timeout", str(after.timed_out_until), target_id=after.id)
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None: log_event(after.guild.id, "channel_update", f"{before.name} -> {after.name}", target_id=after.id)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        if before.channel != after.channel: log_event(member.guild.id, "voice_join" if after.channel else "voice_leave", str(after.channel or before.channel), target_id=member.id)
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None: log_event(guild.id, "ban", target_id=user.id)
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None: log_event(member.guild.id, "member_leave", target_id=member.id)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(EventLogging(bot))
