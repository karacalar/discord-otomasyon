"""Discord bot client."""
from __future__ import annotations

import logging
from pathlib import Path

import discord
from discord.ext import commands

from database.session import init_db
from utils.config import CONFIG

LOGGER = logging.getLogger(__name__)


class ServerManagerBot(commands.Bot):
    """Production Discord bot using slash commands."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True; intents.message_content = True; intents.guilds = True; intents.messages = True; intents.reactions = True; intents.voice_states = True; intents.moderation = True
        super().__init__(command_prefix=CONFIG.get("prefix", "!"), intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        init_db()
        for file in Path("bot/cogs").glob("*.py"):
            if file.name.startswith("_"):
                continue
            await self.load_extension(f"bot.cogs.{file.stem}")
        synced = await self.tree.sync()
        LOGGER.info("Synced %s slash commands", len(synced))

    async def on_ready(self) -> None:
        LOGGER.info("Logged in as %s", self.user)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="servers securely"))

    async def on_error(self, event_method: str, /, *args, **kwargs) -> None:
        LOGGER.exception("Unhandled Discord event error in %s", event_method)


def run_bot() -> None:
    token = CONFIG.get("bot_token")
    if not token or token == "YOUR_DISCORD_BOT_TOKEN":
        raise RuntimeError("Set bot_token in config/config.json or BOT_TOKEN environment variable.")
    ServerManagerBot().run(token, log_handler=None)
