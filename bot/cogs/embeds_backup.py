"""Embed builder and backup commands."""
from __future__ import annotations
import orjson
import discord
from discord import app_commands
from discord.ext import commands
from database.models import SavedEmbed
from database.session import session_scope
from services.backup import serialize_guild, restore_roles
from services.repository import save_backup

class EmbedModal(discord.ui.Modal, title="Embed Builder"):
    embed_title = discord.ui.TextInput(label="Title", max_length=256)
    description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=discord.Embed(title=str(self.embed_title), description=str(self.description), color=discord.Color.blurple()))

class EmbedBackup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @app_commands.command(description="Open embed builder modal.")
    async def embed_builder(self, interaction: discord.Interaction) -> None: await interaction.response.send_modal(EmbedModal())
    @app_commands.command(description="Create and save an embed.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed_send(self, interaction: discord.Interaction, title: str, description: str, save_as: str | None = None) -> None:
        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        if save_as:
            with session_scope() as s: s.add(SavedEmbed(guild_id=str(interaction.guild_id), name=save_as, payload=orjson.dumps(embed.to_dict()).decode()))
        await interaction.response.send_message(embed=embed)
    @app_commands.command(description="Backup roles, channels, categories and permissions.")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_create(self, interaction: discord.Interaction, name: str) -> None:
        payload = serialize_guild(interaction.guild); backup_id = save_backup(interaction.guild_id, name, payload)
        await interaction.response.send_message(f"Backup #{backup_id} saved.", ephemeral=True)
    @app_commands.command(description="Restore roles from a saved backup payload JSON.")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_restore_roles(self, interaction: discord.Interaction, backup_json: str) -> None:
        count = await restore_roles(interaction.guild, orjson.loads(backup_json))
        await interaction.response.send_message(f"Restored {count} roles.", ephemeral=True)
async def setup(bot: commands.Bot) -> None: await bot.add_cog(EmbedBackup(bot))
