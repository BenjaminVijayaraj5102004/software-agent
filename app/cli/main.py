import sys
import os
import shutil

try:
    import asyncpg
    import typer
except ImportError:
    uv_path = shutil.which("uv")
    if uv_path and os.environ.get("ANTMAN_RELAUNCH") != "1":
        os.environ["ANTMAN_RELAUNCH"] = "1"
        os.execv(uv_path, [uv_path, "run", "python", "-m", "app.cli.main"] + sys.argv[1:])
    else:
        print("\n❌ Required dependencies missing in this environment. Please launch using: uv run python -m app.cli.main\n")
        sys.exit(1)

import asyncio
from typing import Optional, List
from rich.console import Console
from .ui import print_banner
from .auth import register_cmd, login_cmd, me_cmd

from .conversation import (
    create_conversation_cmd,
    list_conversations_cmd,
    get_conversation_cmd,
    delete_conversation_cmd,
    chat_cmd,
    get_conversation_history_cmd,
)
from .github_cli import (
    user_info_cmd,
    search_repos_cmd,
    search_code_cmd,
    get_file_cmd,
)
from .interactive import run_interactive_mode

console = Console()

app = typer.Typer(
    name="ant-man",
    help="ANT-MAN CODE — Multi-Agent AI System",
    add_completion=False,
    no_args_is_help=False,
)

auth_app = typer.Typer(help="Authentication and user profile management")
conv_app = typer.Typer(help="Conversation and chat history management")
github_app = typer.Typer(help="GitHub integration commands")

app.add_typer(auth_app, name="auth")
app.add_typer(conv_app, name="conversation")
app.add_typer(conv_app, name="conv")
app.add_typer(github_app, name="github")


# --- AUTH COMMANDS ---
@auth_app.command("register")
def register(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="User password"),
    name: str = typer.Option(None, "--name", "-n", help="Display name (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Register a new user account."""
    asyncio.run(register_cmd(email, password, name, json_output=json_output))


@auth_app.command("login")
def login(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="User password"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Login and acquire a JWT access token."""
    asyncio.run(login_cmd(email, password, json_output=json_output))


@auth_app.command("me")
def me(
    token: str = typer.Option(None, "--token", "-t", help="JWT Access Token (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """View current user profile."""
    asyncio.run(me_cmd(token, json_output=json_output))


# --- CONVERSATION COMMANDS ---
@conv_app.command("list")
def list_conversations(
    token: str = typer.Option(None, "--token", "-t", help="JWT Access Token (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """List all active conversations for the authenticated user."""
    asyncio.run(list_conversations_cmd(token, json_output=json_output))


@conv_app.command("get")
def get_conversation(
    id: str = typer.Option(..., "--id", "-i", help="Conversation UUID or index #"),
    token: str = typer.Option(None, "--token", "-t", help="JWT Access Token (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Get conversation details by UUID or index."""
    asyncio.run(get_conversation_cmd(id, token, json_output=json_output))


@conv_app.command("history")
def conversation_history(
    id: str = typer.Option(None, "--id", "-i", help="Conversation UUID or index # (optional)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Message limit"),
    token: str = typer.Option(None, "--token", "-t", help="JWT Access Token (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """View ChatGPT-style conversation transcript history."""
    asyncio.run(get_conversation_history_cmd(id, token, limit=limit, json_output=json_output))


@conv_app.command("chat")
def chat(
    id: str = typer.Option(..., "--id", "-i", help="Conversation UUID or index #"),
    message: str = typer.Option(..., "--message", "-m", help="User input message"),
    token: str = typer.Option(None, "--token", "-t", help="JWT Access Token (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Send a prompt message to the AI agent."""
    asyncio.run(chat_cmd(id, message, token, json_output=json_output))


# --- GITHUB COMMANDS ---
@github_app.command("user")
def github_user(
    token: str = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Get authenticated GitHub user info."""
    user_info_cmd(token, json_output=json_output)


@github_app.command("repos")
def github_repos(
    query: str = typer.Option(..., "--query", "-q", help="Search query string"),
    limit: int = typer.Option(10, "--limit", "-l", help="Result limit"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Search GitHub repositories."""
    search_repos_cmd(query, token, limit, json_output=json_output)


@github_app.command("code")
def github_code(
    query: str = typer.Option(..., "--query", "-q", help="Search query string"),
    limit: int = typer.Option(10, "--limit", "-l", help="Result limit"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Search code across GitHub."""
    search_code_cmd(query, token, limit, json_output=json_output)


@github_app.command("file")
def github_file(
    owner: str = typer.Option(..., "--owner", help="Repository owner"),
    repo: str = typer.Option(..., "--repo", help="Repository name"),
    path: str = typer.Option(..., "--path", help="File path"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Fetch file content from GitHub repository."""
    get_file_cmd(owner, repo, path, token, json_output=json_output)


# --- INTERACTIVE & ROOT CALLBACK ---
@app.command("interactive")
def interactive():
    """Start interactive ANT-MAN REPL Shell."""
    asyncio.run(run_interactive_mode())


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Default entrypoint: start interactive shell if no subcommand specified."""
    if ctx.invoked_subcommand is None:
        asyncio.run(run_interactive_mode())


def main():
    app()


if __name__ == "__main__":
    main()
