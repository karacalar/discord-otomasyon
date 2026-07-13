# Discord Server Manager Ultimate

A production-ready Python 3.12 Discord management bot using discord.py 2.x, SQLite, SQLAlchemy and a responsive Flask/Bootstrap dashboard.

## Features
- Slash commands only with embeds, buttons, select-ready views and modals.
- Welcome/DM welcome/autorole/goodbye/member join logs.
- Auto moderation: spam, links, invites, mentions, caps, bad words, warnings and temporary timeouts.
- Logging: messages, roles, channels, nicknames, voice, bans, timeouts and member lifecycle events.
- Tickets: button panel, claim, close, reopen and HTML transcript download.
- Reaction roles and button roles.
- XP, levels and leaderboard.
- Giveaways with auto winner selection and reroll.
- Embed builder modal, saved embeds and send command.
- Backups for roles/categories/channels with role restore.
- Server statistics and utility commands.
- Dashboard pages for overview, settings, tickets, logs, automod, reaction roles, embeds, giveaways, backups and statistics.
- JSON/CSV exports for logs, tickets and statistics.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp config.example.json config/config.json
```

## Configuration
Edit `config/config.json` or use environment variables:
- `BOT_TOKEN`
- `DASHBOARD_PORT`
- `SECRET_KEY`
- `DATABASE_URL`
- `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`

## Dashboard Setup
Create an OAuth2 application in the Discord Developer Portal, add the redirect URI from config, then start the app and open `http://localhost:5000`.

## Bot Setup
Enable Server Members Intent and Message Content Intent. Invite the bot with `bot` and `applications.commands` scopes plus required moderation/manage permissions.

## Running
```bash
python bot.py
```
The command starts both the Flask dashboard and Discord bot.

## Commands
`/ping`, `/avatar`, `/userinfo`, `/serverinfo`, `/roleinfo`, `/channelinfo`, `/emojiinfo`, `/welcome_config`, `/warn`, `/timeout`, `/ticket_panel`, `/button_role`, `/reaction_role`, `/leaderboard`, `/giveaway_create`, `/giveaway_reroll`, `/embed_builder`, `/embed_send`, `/backup_create`, `/backup_restore_roles`, `/stats`.

## Screenshots Placeholder
Add screenshots to `assets/screenshots/` and reference them here for commercial presentations.

## FAQ
**Does it use prefix commands?** No, slash commands only; prefix remains in config for legacy compatibility.

**Can I run dashboard without OAuth?** If OAuth credentials are unset, local admin mode is enabled for development.

## Troubleshooting
- Missing slash commands: reinvite with `applications.commands` and restart.
- Permission errors: move the bot role above managed roles and grant Manage Roles/Channels/Messages.
- Database errors: delete development `database/bot.db` and restart to recreate schema.
