"""Utility slash commands."""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    @app_commands.command(description="Show bot latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=discord.Embed(title="Pong", description=f"{self.bot.latency*1000:.0f} ms", color=discord.Color.green()))

    @app_commands.command(description="Show a user's avatar.")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member | None = None) -> None:
        target = user or interaction.user
        await interaction.response.send_message(embed=discord.Embed(title=f"{target} avatar").set_image(url=target.display_avatar.url))

    @app_commands.command(description="Show user information.")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member | None = None) -> None:
        target = user or interaction.user
        embed = discord.Embed(title=str(target), color=target.color).add_field(name="ID", value=target.id).add_field(name="Created", value=target.created_at.date()).add_field(name="Joined", value=target.joined_at.date() if isinstance(target, discord.Member) and target.joined_at else "Unknown")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Show server information.")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if not guild: return await interaction.response.send_message("Guild only", ephemeral=True)
        embed = discord.Embed(title=guild.name).add_field(name="Members", value=guild.member_count).add_field(name="Boosts", value=guild.premium_subscription_count).add_field(name="Channels", value=len(guild.channels))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Show role information.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role) -> None:
        await interaction.response.send_message(embed=discord.Embed(title=role.name, color=role.color).add_field(name="Members", value=len(role.members)).add_field(name="ID", value=role.id))

    @app_commands.command(description="Show channel information.")
    async def channelinfo(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel) -> None:
        await interaction.response.send_message(embed=discord.Embed(title=channel.name).add_field(name="Type", value=channel.type).add_field(name="ID", value=channel.id))

    @app_commands.command(description="Show emoji information.")
    async def emojiinfo(self, interaction: discord.Interaction, emoji: str) -> None:
        await interaction.response.send_message(embed=discord.Embed(title="Emoji", description=emoji))


async def setup(bot: commands.Bot) -> None: await bot.add_cog(Utility(bot))
