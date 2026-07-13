"""Configuration loading utilities."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.json"
EXAMPLE_PATH = ROOT / "config.example.json"


def load_config() -> dict[str, Any]:
    """Load JSON configuration and environment overrides."""
    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    overrides = {
        "bot_token": os.getenv("BOT_TOKEN"),
        "dashboard_port": os.getenv("DASHBOARD_PORT"),
        "dashboard_host": os.getenv("DASHBOARD_HOST"),
        "secret_key": os.getenv("SECRET_KEY"),
        "database_url": os.getenv("DATABASE_URL"),
        "discord_client_id": os.getenv("DISCORD_CLIENT_ID"),
        "discord_client_secret": os.getenv("DISCORD_CLIENT_SECRET"),
        "discord_redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
    }
    for key, value in overrides.items():
        if value not in (None, ""):
            data[key] = int(value) if key == "dashboard_port" else value
    return data


CONFIG = load_config()
