"""Ticket system with components and transcripts."""
from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
from database.models import Ticket
from database.session import session_scope
from services.transcripts import build_transcript

class TicketView(discord.ui.View):
    def __init__(self) -> None: super().__init__(timeout=None)
    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, custom_id="ticket_open")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild = interaction.guild; member = interaction.user
        if not guild or not isinstance(member, discord.Member): return
        category = discord.utils.get(guild.categories, name="Tickets") or await guild.create_category("Tickets")
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), member: discord.PermissionOverwrite(view_channel=True, send_messages=True), guild.me: discord.PermissionOverwrite(view_channel=True)}
        channel = await guild.create_text_channel(f"ticket-{member.name}"[:90], category=category, overwrites=overwrites)
        with session_scope() as s: s.add(Ticket(guild_id=str(guild.id), channel_id=str(channel.id), owner_id=str(member.id)))
        await channel.send(member.mention, embed=discord.Embed(title="Support Ticket"), view=TicketManageView())
        await interaction.response.send_message(f"Created {channel.mention}", ephemeral=True)
class TicketManageView(discord.ui.View):
    def __init__(self) -> None: super().__init__(timeout=None)
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: await interaction.response.send_message(f"Claimed by {interaction.user.mention}")
    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if isinstance(interaction.channel, discord.TextChannel):
            html = await build_transcript(interaction.channel)
            await interaction.response.send_message("Ticket closed. Transcript attached.", file=discord.File(fp=__import__('io').BytesIO(html.encode()), filename="transcript.html"))
            await interaction.channel.edit(name=f"closed-{interaction.channel.name}"[:90])
    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.gray)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: await interaction.response.send_message("Ticket reopened.")
class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @app_commands.command(description="Send ticket panel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_panel(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=discord.Embed(title="Support", description="Open a ticket below."), view=TicketView())
async def setup(bot: commands.Bot) -> None: await bot.add_cog(Tickets(bot))
