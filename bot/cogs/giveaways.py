"""Giveaway system."""
from __future__ import annotations
from datetime import datetime, timedelta
import random
import discord
from discord import app_commands
from discord.ext import commands, tasks
from database.models import Giveaway
from database.session import session_scope
from sqlalchemy import select

class Giveaways(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot; self.finish_giveaways.start()
    def cog_unload(self) -> None: self.finish_giveaways.cancel()
    @app_commands.command(description="Create a giveaway.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_create(self, interaction: discord.Interaction, prize: str, minutes: int, winners: int = 1) -> None:
        embed = discord.Embed(title="🎁 Giveaway", description=f"Prize: **{prize}**\nReact with 🎉 to enter!", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed); msg = await interaction.original_response(); await msg.add_reaction("🎉")
        with session_scope() as s: s.add(Giveaway(guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id), message_id=str(msg.id), prize=prize, winners=winners, ends_at=datetime.utcnow()+timedelta(minutes=minutes)))
    @app_commands.command(description="Reroll giveaway winner.")
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str) -> None:
        msg = await interaction.channel.fetch_message(int(message_id))
        users = [u async for u in msg.reactions[0].users() if not u.bot]
        await interaction.response.send_message(f"New winner: {random.choice(users).mention if users else 'none'}")
    @tasks.loop(seconds=60)
    async def finish_giveaways(self) -> None:
        with session_scope() as s: rows = list(s.scalars(select(Giveaway).where(Giveaway.ended == False, Giveaway.ends_at <= datetime.utcnow())))
        for row in rows:
            channel = self.bot.get_channel(int(row.channel_id))
            if not isinstance(channel, discord.TextChannel): continue
            msg = await channel.fetch_message(int(row.message_id)); users = [u async for u in msg.reactions[0].users() if not u.bot]
            winners = random.sample(users, min(row.winners, len(users))) if users else []
            await channel.send(f"Giveaway ended for **{row.prize}**. Winners: {', '.join(u.mention for u in winners) or 'none'}")
            with session_scope() as s: s.get(Giveaway, row.id).ended = True
async def setup(bot: commands.Bot) -> None: await bot.add_cog(Giveaways(bot))
