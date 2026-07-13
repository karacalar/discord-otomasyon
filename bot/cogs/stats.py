"""Server statistics commands."""
from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @app_commands.command(description="Show server statistics.")
    async def stats(self, interaction: discord.Interaction) -> None:
        g = interaction.guild
        online = sum(1 for m in g.members if m.status != discord.Status.offline)
        voice = sum(len(c.members) for c in g.voice_channels)
        bots = sum(1 for m in g.members if m.bot)
        embed = discord.Embed(title="Server Statistics").add_field(name="Members", value=g.member_count).add_field(name="Bots", value=bots).add_field(name="Online", value=online).add_field(name="Boosts", value=g.premium_subscription_count).add_field(name="Voice Users", value=voice)
        await interaction.response.send_message(embed=embed)
async def setup(bot: commands.Bot) -> None: await bot.add_cog(Stats(bot))
