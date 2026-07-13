"""Button and reaction role panels."""
from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands

class RoleButton(discord.ui.Button):
    def __init__(self, role_id: int, label: str) -> None: super().__init__(label=label, style=discord.ButtonStyle.primary); self.role_id = role_id
    async def callback(self, interaction: discord.Interaction) -> None:
        role = interaction.guild.get_role(self.role_id) if interaction.guild else None
        if not role or not isinstance(interaction.user, discord.Member): return await interaction.response.send_message("Role unavailable.", ephemeral=True)
        if role in interaction.user.roles: await interaction.user.remove_roles(role); msg = f"Removed {role.name}."
        else: await interaction.user.add_roles(role); msg = f"Added {role.name}."
        await interaction.response.send_message(msg, ephemeral=True)

class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot
    @app_commands.command(description="Create a button role panel.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def button_role(self, interaction: discord.Interaction, role: discord.Role, title: str = "Role Panel") -> None:
        view = discord.ui.View(timeout=None); view.add_item(RoleButton(role.id, role.name))
        await interaction.response.send_message(embed=discord.Embed(title=title, description="Click to toggle the role."), view=view)
    @app_commands.command(description="Create a classic reaction role message.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reaction_role(self, interaction: discord.Interaction, role: discord.Role, emoji: str) -> None:
        await interaction.response.send_message(embed=discord.Embed(title="Reaction Role", description=f"React with {emoji} for {role.mention}"))
        msg = await interaction.original_response(); await msg.add_reaction(emoji)
async def setup(bot: commands.Bot) -> None: await bot.add_cog(ReactionRoles(bot))
