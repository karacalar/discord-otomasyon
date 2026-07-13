"""XP and level system."""
from __future__ import annotations
import random
import discord
from discord import app_commands
from discord.ext import commands
from services.repository import add_xp, leaderboard

class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild and not message.author.bot:
            _, level, up = add_xp(message.guild.id, message.author.id, random.randint(5, 12))
            if up: await message.channel.send(embed=discord.Embed(description=f"🎉 {message.author.mention} reached level {level}!"), delete_after=10)
    @app_commands.command(description="Show XP leaderboard.")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        rows = leaderboard(interaction.guild_id)
        text = "\n".join(f"{i+1}. <@{r.user_id}> — Level {r.level} ({r.xp} XP)" for i, r in enumerate(rows)) or "No XP yet."
        await interaction.response.send_message(embed=discord.Embed(title="Leaderboard", description=text))
async def setup(bot: commands.Bot) -> None: await bot.add_cog(Levels(bot))
