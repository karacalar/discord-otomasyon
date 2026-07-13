"""Welcome, goodbye, join log and autorole system."""
from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
from services.repository import get_setting, set_setting, log_event

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        cfg = get_setting(member.guild.id, "welcome", {})
        log_event(member.guild.id, "member_join", target_id=member.id)
        if rid := cfg.get("autorole_id"):
            role = member.guild.get_role(int(rid))
            if role: await member.add_roles(role, reason="Auto role")
        embed = discord.Embed(title=cfg.get("title", "Welcome!"), description=cfg.get("message", "Welcome {member} to {server}!").format(member=member.mention, server=member.guild.name), color=discord.Color.blurple())
        if cid := cfg.get("channel_id"):
            channel = member.guild.get_channel(int(cid))
            if isinstance(channel, discord.TextChannel): await channel.send(embed=embed)
        if cfg.get("dm_message"):
            try: await member.send(cfg["dm_message"].format(member=member.name, server=member.guild.name))
            except discord.Forbidden: pass
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        cfg = get_setting(member.guild.id, "welcome", {})
        if cid := cfg.get("goodbye_channel_id") or cfg.get("channel_id"):
            channel = member.guild.get_channel(int(cid))
            if isinstance(channel, discord.TextChannel): await channel.send(embed=discord.Embed(title="Goodbye", description=f"{member} left {member.guild.name}."))
    @app_commands.command(description="Configure welcome channel and text.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_config(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, autorole: discord.Role | None = None) -> None:
        set_setting(interaction.guild_id, "welcome", {"channel_id": channel.id, "message": message, "autorole_id": autorole.id if autorole else None})
        await interaction.response.send_message("Welcome system configured.", ephemeral=True)
async def setup(bot: commands.Bot) -> None: await bot.add_cog(Welcome(bot))
