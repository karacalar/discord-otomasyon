"""Flask web dashboard with Discord OAuth2 login."""
from __future__ import annotations

import secrets
from typing import Any

import requests
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from sqlalchemy import func, select

from database.models import Backup, Giveaway, Log, Setting, Ticket, User, XP
from database.session import init_db, session_scope
from services.repository import export_table, get_setting, set_setting
from utils.config import CONFIG

login_manager = LoginManager(); login_manager.login_view = "login"

class DashboardUser(UserMixin):
    def __init__(self, discord_id: str, username: str) -> None: self.id = discord_id; self.username = username

@login_manager.user_loader
def load_user(user_id: str) -> DashboardUser | None:
    with session_scope() as s:
        row = s.scalar(select(User).where(User.discord_id == user_id))
        return DashboardUser(row.discord_id, row.username) if row else None

def counts() -> dict[str, int]:
    with session_scope() as s:
        return {"tickets": s.scalar(select(func.count(Ticket.id))) or 0, "logs": s.scalar(select(func.count(Log.id))) or 0, "giveaways": s.scalar(select(func.count(Giveaway.id))) or 0, "xp": s.scalar(select(func.count(XP.id))) or 0}

def create_app() -> Flask:
    init_db(); app = Flask(__name__); app.secret_key = CONFIG.get("secret_key", secrets.token_hex(32)); login_manager.init_app(app)
    @app.route("/")
    def index() -> str: return render_template("index.html", counts=counts())
    @app.route("/login")
    def login() -> Response:
        client_id = CONFIG.get("discord_client_id")
        if not client_id or client_id == "YOUR_CLIENT_ID":
            with session_scope() as s:
                user = s.scalar(select(User).where(User.discord_id == "local-admin")) or User(discord_id="local-admin", username="Local Admin")
                s.add(user)
            login_user(DashboardUser("local-admin", "Local Admin")); return redirect(url_for("overview"))
        session["oauth_state"] = secrets.token_urlsafe(16)
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={CONFIG['discord_redirect_uri']}&response_type=code&scope=identify%20guilds&state={session['oauth_state']}")
    @app.route("/oauth/callback")
    def oauth_callback() -> Response:
        if request.args.get("state") != session.get("oauth_state"): return redirect(url_for("login"))
        data = {"client_id": CONFIG["discord_client_id"], "client_secret": CONFIG["discord_client_secret"], "grant_type": "authorization_code", "code": request.args["code"], "redirect_uri": CONFIG["discord_redirect_uri"]}
        token = requests.post("https://discord.com/api/oauth2/token", data=data, timeout=10).json()
        profile = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {token['access_token']}"}, timeout=10).json()
        with session_scope() as s:
            user = s.scalar(select(User).where(User.discord_id == profile["id"])) or User(discord_id=profile["id"], username=profile["username"])
            user.username = profile["username"]; user.access_token = token["access_token"]; s.add(user)
        login_user(DashboardUser(profile["id"], profile["username"])); return redirect(url_for("overview"))
    @app.route("/logout")
    def logout() -> Response: logout_user(); return redirect(url_for("index"))
    @app.route("/dashboard")
    @login_required
    def overview() -> str: return render_template("dashboard.html", page="Overview", counts=counts())
    @app.route("/dashboard/<page>", methods=["GET", "POST"])
    @login_required
    def dashboard_page(page: str) -> str | Response:
        guild_id = request.values.get("guild_id", "global")
        if request.method == "POST":
            set_setting(guild_id, page, request.form.to_dict(flat=True)); flash("Settings saved.")
            return redirect(url_for("dashboard_page", page=page, guild_id=guild_id))
        with session_scope() as s:
            logs = list(s.scalars(select(Log).order_by(Log.created_at.desc()).limit(100)))
            tickets = list(s.scalars(select(Ticket).order_by(Ticket.created_at.desc()).limit(50)))
        return render_template("page.html", page=page.title(), settings=get_setting(guild_id, page, {}), logs=logs, tickets=tickets, counts=counts())
    @app.route("/export/<table>/<fmt>")
    @login_required
    def export(table: str, fmt: str) -> Response:
        models: dict[str, Any] = {"logs": Log, "tickets": Ticket, "statistics": XP}
        data = export_table(models.get(table, Log), fmt)
        return Response(data, mimetype="text/csv" if fmt == "csv" else "application/json", headers={"Content-Disposition": f"attachment; filename={table}.{fmt}"})
    return app
