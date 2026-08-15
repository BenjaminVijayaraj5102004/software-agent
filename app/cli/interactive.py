import asyncio
import json
from pathlib import Path
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

prompt_style = Style.from_dict({
    "completion-menu.completion": "bg:#2b2b2b #00ffff",
    "completion-menu.completion.current": "bg:#008080 #ffffff bold",
    "completion-menu.meta": "bg:#1e1e1e #aaaaaa",
    "completion-menu.meta.current": "bg:#008080 #ffffff bold",
    "scrollbar.background": "bg:#121212",
    "scrollbar.button": "bg:#444444",
})

from .ui import (
    console,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_session_status,
    print_help_menu,
    print_exit_summary,
)
from .auth import register_cmd, login_cmd, me_cmd
from .conversation import (
    create_conversation_cmd,
    list_conversations_cmd,
    get_conversation_cmd,
    delete_conversation_cmd,
    chat_cmd,
    get_conversation_history_cmd,
    resolve_conversation_id,
)

from .github_cli import user_info_cmd, search_repos_cmd, search_code_cmd, get_file_cmd
from ..db.database import SessionLocal
from ..repository.conversation_repo import ConversationRepository

conv_repo = ConversationRepository()

SESSION_FILE = Path(".antman_session.json")

SLASH_SERVICES = {
    "/help": "Display slash commands reference table",
    "/history": "View ChatGPT-style chat history transcript (/history [id/#])",
    "/new": "Start a new conversation thread (New Chat)",
    "/chats": "List all active conversations with index numbers",
    "/switch": "Switch active conversation by index # or UUID (/switch <#|id>)",
    "/resume": "Resume session by index # or Conversation UUID (/resume <#|id>)",
    "/conv list": "List all active conversations",
    "/conv select": "Select active conversation (/conv select <#|id>)",
    "/conv history": "View conversation history (/conv history [id/#])",
    "/auth login": "Login with user email & password",
    "/auth register": "Register a new user account",
    "/auth profile": "View current authenticated user profile",
    "/auth logout": "Clear active user session token",
    "/token": "Paste or set JWT Access Token directly",
    "/github user": "View authenticated GitHub user info",
    "/github repos": "Search GitHub repositories (/github repos <query>)",
    "/github code": "Search code across GitHub (/github code <query>)",
    "/github file": "Fetch repo file content (/github file <owner> <repo> <path>)",
    "/clear": "Clear terminal screen",
    "/exit": "Exit interactive session",
}


class SlashCommandCompleter(Completer):
    """Auto-completion completer for slash command services."""

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/") or text == "":
            for cmd, desc in SLASH_SERVICES.items():
                if cmd.lower().startswith(text.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=cmd,
                        display_meta=desc,
                    )


bindings = KeyBindings()


@bindings.add("down")
def _(event):
    """Trigger slash commands menu on Down arrow key."""
    buff = event.current_buffer
    if buff.complete_state:
        buff.complete_next()
    else:
        buff.start_completion(select_first=True)


def load_session() -> dict:
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_session(token: str | None, email: str | None, conv_id: str | None, conv_title: str | None = None):
    try:
        data = {
            "token": token,
            "email": email,
            "conversation_id": conv_id,
            "conversation_title": conv_title,
        }
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


async def run_interactive_mode():
    print_banner()

    saved_state = load_session()
    session_token = saved_state.get("token")
    session_user_email = saved_state.get("email")
    session_conversation_id = saved_state.get("conversation_id")
    session_conversation_title = saved_state.get("conversation_title")

    authenticated = False
    if session_token:
        me_res = await me_cmd(session_token, silent=True)
        if me_res.get("status") == "success":
            session_user_email = me_res["user"]["email"]
            authenticated = True
        else:
            session_token = None
            session_user_email = None

    if not authenticated:
        console.print("\n")
        console.print(Panel(
            "[bold cyan]🌐 ANT-MAN CODE — Authorized Developer Portal[/bold cyan]\n"
            "[white]Please log in to your account to enter your workspace.[/white]\n"
            "[dim white](If you are not registered, entering credentials will automatically redirect to registration)[/dim white]",
            title="🔐 Login Required",
            border_style="cyan"
        ))

        login_success = False
        while not login_success:
            try:
                email = Prompt.ask("\n👤 Email").strip()
                if not email:
                    continue

                password = Prompt.ask("🔑 Password", password=True).strip()
                if not password:
                    continue

                res = await login_cmd(email, password, silent=True)
                if res.get("status") == "success":
                    session_token = res["access_token"]
                    session_user_email = res["user"]["email"]
                    login_success = True
                    print_success(f"Login successful! Welcome back, [bold cyan]{session_user_email}[/bold cyan]!")
                else:
                    print_error(f"{res.get('detail', 'Login failed')}.")
                    console.print("\n[bold yellow]🔄 Redirecting to Account Registration Portal...[/bold yellow]")
                    console.print(Panel(
                        "[bold magenta]📝 New Account Registration[/bold magenta]\n"
                        f"[white]Setting up new user account for: [bold cyan]{email}[/bold cyan]",
                        title="✨ Registration",
                        border_style="magenta"
                    ))

                    reg_pass = Prompt.ask("🔑 Set Password for Registration", password=True).strip()
                    reg_name = Prompt.ask("📛 Display Name (optional)", default="").strip()

                    reg_res = await register_cmd(email, reg_pass, reg_name or None, silent=True)
                    if reg_res.get("status") == "success":
                        login_res = await login_cmd(email, reg_pass, silent=True)
                        if login_res.get("status") == "success":
                            session_token = login_res["access_token"]
                            session_user_email = login_res["user"]["email"]
                            login_success = True
                            print_success(f"Account registered & logged in successfully as [bold cyan]{session_user_email}[/bold cyan]!")
                        else:
                            print_error("Registration completed, but auto-login failed. Please try logging in.")
                    else:
                        print_error(f"Registration failed: {reg_res.get('detail')}")

            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Session cancelled. Exiting CLI.[/yellow]")
                return

    if session_conversation_id:
        check_conv = await get_conversation_cmd(session_conversation_id, session_token, silent=True)
        if check_conv.get("status") != "success":
            session_conversation_id = None
            session_conversation_title = None

    save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)

    console.print("\n")
    print_session_status(session_user_email, session_conversation_id, session_conversation_title)

    session = PromptSession(
        completer=SlashCommandCompleter(),
        key_bindings=bindings,
        style=prompt_style,
        complete_while_typing=True,
        mouse_support=True,
    )

    while True:
        try:
            prompt_label = HTML("\n<ansired><b>ant-man</b></ansired><ansicyan><b>&gt;</b></ansicyan> ")
            user_input = (await session.prompt_async(prompt_label)).strip()

            if not user_input:
                continue

            normalized_input = user_input
            lower_raw = user_input.lower().strip()
            if lower_raw in ["convo list", "conv list", "conversations list"]:
                normalized_input = "/conv list"
            elif lower_raw in ["convo select", "conv select"]:
                normalized_input = "/conv select"
            elif lower_raw in ["history", "view"]:
                normalized_input = "/history"
            elif lower_raw in ["chats"]:
                normalized_input = "/chats"
            elif lower_raw in ["cls", "clear"]:
                normalized_input = "/clear"
            elif lower_raw in ["exit", "quit"]:
                normalized_input = "/exit"

            # --- SLASH COMMAND ROUTER ---
            if normalized_input.startswith("/"):
                parts = normalized_input.split(maxsplit=2)
                cmd = parts[0].lower()
                arg1 = parts[1] if len(parts) > 1 else ""
                arg2 = parts[2] if len(parts) > 2 else ""

                if cmd in ["/exit", "/quit"]:
                    break

                elif cmd in ["/", "/help", "/services"]:
                    print_help_menu()

                elif cmd == "/clear":
                    console.clear()
                    print_banner()
                    print_session_status(session_user_email, session_conversation_id, session_conversation_title)

                elif cmd in ["/history", "/view"]:
                    target = arg1 or session_conversation_id
                    await get_conversation_history_cmd(target, session_token, json_output=False)

                elif cmd == "/new":
                    session_conversation_id = None
                    session_conversation_title = None
                    save_session(session_token, session_user_email, None, None)
                    print_success("Started a new conversation thread (New Chat). Next prompt will start a fresh chat session.")
                    print_session_status(session_user_email, session_conversation_id, session_conversation_title)



                elif cmd == "/chats":
                    await list_conversations_cmd(session_token, json_output=False)

                elif cmd in ["/switch", "/select", "/resume"]:
                    target_arg = arg1 or Prompt.ask("Enter Conversation UUID or index #")
                    if target_arg.strip():
                        res = await get_conversation_cmd(target_arg.strip(), session_token, silent=True)
                        if res.get("status") == "success":
                            session_conversation_id = res["conversation"]["id"]
                            session_conversation_title = res["conversation"]["title"]
                            save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                            print_success(f"Active conversation switched to: [bold cyan]{session_conversation_title}[/bold cyan] ({session_conversation_id})")
                            print_session_status(session_user_email, session_conversation_id, session_conversation_title)
                        else:
                            print_error(f"Could not switch conversation: {res.get('detail')}")

                elif cmd in ["/conv", "/conversations"]:
                    sub = arg1.lower()
                    if sub == "list":
                        await list_conversations_cmd(session_token, json_output=False)
                    elif sub == "select":
                        target_arg = arg2 or Prompt.ask("Enter Conversation UUID or index #")
                        if target_arg.strip():
                            res = await get_conversation_cmd(target_arg.strip(), session_token, silent=True)
                            if res.get("status") == "success":
                                session_conversation_id = res["conversation"]["id"]
                                session_conversation_title = res["conversation"]["title"]
                                save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                                print_success(f"Active conversation switched to: [bold cyan]{session_conversation_title}[/bold cyan] ({session_conversation_id})")
                                print_session_status(session_user_email, session_conversation_id, session_conversation_title)
                            else:
                                print_error(f"Could not select conversation: {res.get('detail')}")
                    elif sub == "history":
                        target_id = arg2 or session_conversation_id
                        await get_conversation_history_cmd(target_id, session_token, json_output=False)
                    else:
                        print_info("Conversation subcommands: /conv list, /conv select <#|id>, /conv history [id/#]")

                elif cmd == "/auth":
                    sub = arg1.lower()
                    if sub == "login":
                        email = arg2 or Prompt.ask("Enter user email")
                        password = Prompt.ask("Enter password", password=True)
                        res = await login_cmd(email, password, json_output=False)
                        if res.get("status") == "success":
                            session_token = res["access_token"]
                            session_user_email = res["user"]["email"]
                            save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                            print_session_status(session_user_email, session_conversation_id, session_conversation_title)

                    elif sub == "register":
                        email = arg2 or Prompt.ask("Enter user email")
                        password = Prompt.ask("Enter password", password=True)
                        name = Prompt.ask("Enter display name (optional)", default="")
                        await register_cmd(email, password, name or None, json_output=False)

                    elif sub in ["profile", "me"]:
                        if not session_token:
                            session_token = Prompt.ask("Enter JWT Access Token")
                        if session_token:
                            res = await me_cmd(session_token, json_output=False)
                            if res.get("status") == "success":
                                session_user_email = res["user"]["email"]
                                save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                                print_session_status(session_user_email, session_conversation_id, session_conversation_title)

                    elif sub == "logout":
                        session_token = None
                        session_user_email = None
                        session_conversation_id = None
                        session_conversation_title = None
                        save_session(None, None, None, None)
                        print_success("User logged out successfully.")
                        print_session_status(session_user_email, session_conversation_id, session_conversation_title)

                    else:
                        print_info("Auth subcommands: /auth login, /auth register, /auth profile, /auth logout")

                elif cmd == "/token":
                    token_val = arg1 or Prompt.ask("Paste your JWT Access Token")
                    if token_val.strip():
                        session_token = token_val.strip()
                        me_res = await me_cmd(session_token, silent=True)
                        if me_res.get("status") == "success":
                            session_user_email = me_res["user"]["email"]
                        save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                        print_success("JWT Access Token updated.")
                        print_session_status(session_user_email, session_conversation_id, session_conversation_title)



                elif cmd == "/github":
                    sub = arg1.lower()
                    if sub == "user":
                        user_info_cmd(json_output=False)
                    elif sub == "repos":
                        q = arg2 or Prompt.ask("Enter repository search query", default="FastAPI agent")
                        search_repos_cmd(q, json_output=False)
                    elif sub == "code":
                        q = arg2 or Prompt.ask("Enter code search query", default="create_deep_agent")
                        search_code_cmd(q, json_output=False)
                    elif sub == "file":
                        file_args = arg2.split() if arg2 else []
                        owner = file_args[0] if len(file_args) > 0 else Prompt.ask("Repo owner", default="fastapi")
                        repo = file_args[1] if len(file_args) > 1 else Prompt.ask("Repo name", default="fastapi")
                        path = file_args[2] if len(file_args) > 2 else Prompt.ask("File path", default="README.md")
                        get_file_cmd(owner, repo, path, json_output=False)
                    else:
                        print_info("GitHub subcommands: /github user, /github repos <query>, /github code <query>, /github file <owner> <repo> <path>")

                else:
                    print_error(f"Unknown slash command: {cmd}. Type [bold cyan]/help[/bold cyan] for available commands.")

            # --- DIRECT AGENT CHAT PROMPT ---
            else:
                if not session_conversation_id:
                    auto_title = user_input[:30] if len(user_input) > 30 else user_input
                    with console.status("[cyan]Creating new conversation session...[/cyan]", spinner="dots"):
                        res = await create_conversation_cmd(auto_title, session_token, silent=True)
                    if res.get("status") == "success":
                        session_conversation_id = res["conversation"]["id"]
                        session_conversation_title = res["conversation"]["title"]
                        print_success(f"Auto-created conversation: [bold cyan]{session_conversation_title}[/bold cyan] ({session_conversation_id})")
                        print_session_status(session_user_email, session_conversation_id, session_conversation_title)
                    else:
                        print_error(f"Could not create conversation: {res.get('detail')}")
                        continue

                save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
                await chat_cmd(session_conversation_id, user_input, session_token, json_output=False)

        except (KeyboardInterrupt, EOFError):
            break

    save_session(session_token, session_user_email, session_conversation_id, session_conversation_title)
    print_exit_summary(session_user_email, session_conversation_id, session_conversation_title)
