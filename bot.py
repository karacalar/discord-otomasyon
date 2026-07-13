"""Application entrypoint. Starts both dashboard and Discord bot."""
from __future__ import annotations

import threading

from bot.client import run_bot
from dashboard.app import create_app
from utils.config import CONFIG
from utils.logging import setup_logging


def main() -> None:
    setup_logging()
    app = create_app()
    thread = threading.Thread(target=lambda: app.run(host=CONFIG.get("dashboard_host", "0.0.0.0"), port=int(CONFIG.get("dashboard_port", 5000)), use_reloader=False), daemon=True)
    thread.start()
    run_bot()


if __name__ == "__main__":
    main()
