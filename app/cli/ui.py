import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.theme import Theme

# Ensure UTF-8 output encoding on Windows stdout if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Custom Theme for ANT-MAN CODE
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "antman": "bold red",
    "accent": "bold magenta",
})

console = Console(theme=custom_theme)

ANTMAN_BANNER = r"""[bold red]
   _   _  _ _____   __  ___  ___  _  _    ___ ___  ___  ___ 
  /_\ | \| |_   _| |  \/  |/ _ \| \| |  / __/ _ \|   \| __|
 / _ \| .` | | |   | |\/| | A | | .` | | (_| (_) | |) | _| 
/_/ \_\_|\_| |_|   |_|  |_|_|_|_|_|\_|  \___\___/|___/|___|
[/bold red]
[bold cyan]ANT-MAN CODE — Multi-Agent AI & GitHub Interface[/bold cyan]
"""


def print_banner():
    console.print(Panel(ANTMAN_BANNER, border_style="red", expand=False))


def print_success(message: str):
    console.print(f"[success][+] {message}[/success]")


def print_error(message: str):
    console.print(f"[error][-] {message}[/error]")


def print_info(message: str):
    console.print(f"[info][i] {message}[/info]")


def render_markdown(
    content: str, 
    title: str = "ANT-MAN Response", 
    tools_called: list[str] | None = None,
    token_stats: dict | None = None
):
    if not content or not content.strip():
        return

    console.print("")
    md = Markdown(content)
    console.print(md)

    if tools_called and len(tools_called) > 0:
        tools_str = ", ".join([f"[bold yellow]{t}[/bold yellow]" for t in tools_called])
        console.print(f"\n🛠️  [bold white]Tools Called:[/bold white] [bold green]YES[/bold green] ({tools_str})")
        console.print(f"📌 [bold cyan]Code Reference:[/bold cyan] [italic white]Architecture pattern referenced from GitHub via {tools_str}[/italic white]")
    else:
        console.print(f"\n🛠️  [bold white]Tools Called:[/bold white] [bold cyan]NO[/bold cyan] [dim white](Direct AI Generation)[/dim white]")

    if token_stats:
        tot = token_stats.get("total_tokens", 0)
        console.print(f"📊 [bold white]Token Usage Total:[/bold white] [bold yellow]{tot}[/bold yellow]\n")


def render_code(code_str: str, language: str = "python", filename: str = "code"):
    syntax = Syntax(code_str, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[accent]Code: {filename}[/accent]", border_style="magenta"))


def print_session_status(user_email: str | None = None, conversation_id: str | None = None, conversation_title: str | None = None):
    """Render a compact Claude Code status panel."""
    user_str = f"[bold green]{user_email}[/bold green]" if user_email else "[bold yellow]Not Logged In[/bold yellow]"
    conv_str = f"[bold cyan]{conversation_id}[/bold cyan]" if conversation_id else "[dim yellow]None (Will auto-create)[/dim yellow]"
    title_str = f" ([dim]{conversation_title}[/dim])" if conversation_title else ""

    status_text = (
        f"👤 [bold white]User:[/bold white] {user_str}  │  "
        f"💬 [bold white]Active Conv ID:[/bold white] {conv_str}{title_str}\n"
        f"[dim white]💡 Type prompt to chat with ANT-MAN, or type [/dim white][bold cyan]/[/bold cyan][dim white] or press [/dim white][bold yellow]↓ Down[/bold yellow][dim white] key to open services menu.[/dim white]"
    )
    console.print(Panel(status_text, title="🐜 [bold red]ANT-MAN CODE Session[/bold red]", border_style="bright_blue", padding=(0, 1)))


def print_help_menu():
    """Render Claude Code style categorized slash commands reference UI."""
    from rich.columns import Columns

    def create_category_table(category_name: str, color: str, commands: list[tuple[str, str, str]]):
        table = Table(
            title=f"[{color}]{category_name}[/{color}]",
            border_style=color,
            expand=True,
            show_header=True,
            header_style=f"bold {color}",
        )
        table.add_column("Command", style="bold cyan", no_wrap=True, ratio=3)
        table.add_column("Description", style="white", ratio=5)
        table.add_column("Usage Example", style="dim yellow", ratio=4)

        for cmd, desc, example in commands:
            table.add_row(cmd, desc, example)
        return table

    conv_cmds = [
        ("/history [id/#]", "View ChatGPT-style chat history transcript", "/history"),
        ("/new", "Start a new conversation thread (New Chat)", "/new"),
        ("/list, /chats", "List all past conversations with index numbers", "/list"),
        ("/switch <id/#>", "Switch active conversation by index # or UUID", "/switch 1"),
        ("/conv list", "List all active conversations", "/conv list"),
        ("/conv select <id/#>", "Select active conversation by index # or UUID", "/conv select 1"),
        ("/conv history [id/#]", "View chat history of specified session", "/conv history 1"),
        ("/resume <id/#>", "Quick resume session by index # or UUID", "/resume 1"),
    ]

    auth_cmds = [
        ("/auth login", "Login with email & password", "/auth login"),
        ("/auth register", "Register new user account", "/auth register"),
        ("/auth profile", "View current authenticated profile", "/auth profile"),
        ("/token <jwt>", "Set JWT Access Token directly", "/token eyJhbGci..."),
        ("/auth logout", "Log out and clear active session token", "/auth logout"),
    ]

    github_cmds = [
        ("/github user", "View authenticated GitHub profile", "/github user"),
        ("/github repos <q>", "Search GitHub repositories", "/github repos agentic ai"),
        ("/github code <q>", "Search code across GitHub", "/github code create_deep_agent"),
        ("/github file <owner> <repo> <path>", "Fetch source code file from GitHub", "/github file fastapi fastapi README.md"),
    ]

    sys_cmds = [
        ("/clear", "Clear terminal screen output", "/clear"),
        ("/help", "Show this slash command reference", "/help"),
        ("/exit, /quit", "Exit session & get Conversation ID", "/exit"),
    ]

    console.print("\n[bold bright_magenta]⚡ ANT-MAN CODE — Slash Commands & Services Reference[/bold bright_magenta]")
    console.print(create_category_table("💬 Conversation Services", "bright_cyan", conv_cmds))
    console.print(create_category_table("🔑 Authentication & User Profile", "bright_green", auth_cmds))
    console.print(create_category_table("🐙 GitHub Integration Services", "bright_blue", github_cmds))
    console.print(create_category_table("⚙️ System Commands", "bright_red", sys_cmds))
    console.print("[dim white]💡 Type your prompt directly to talk to ANT-MAN AI agent, or type any [/dim white][bold cyan]/command[/bold cyan][dim white] above.[/dim white]\n")


def render_chat_history(conversation_title: str, conversation_id: str, messages: list):
    """Render a ChatGPT-style visual transcript of conversation history."""
    console.print("")
    header_info = (
        f"[bold white]Title:[/bold white] [bold cyan]{conversation_title}[/bold cyan]  │  "
        f"[bold white]ID:[/bold white] [bold yellow]{conversation_id}[/bold yellow]  │  "
        f"[bold white]Messages:[/bold white] [bold green]{len(messages)}[/bold green]"
    )
    console.print(Panel(header_info, title="💬 [bold bright_magenta]ChatGPT Conversation History[/bold bright_magenta]", border_style="magenta"))

    if not messages:
        console.print("[dim yellow]No messages recorded in this conversation yet.[/dim yellow]\n")
        return

    turn_idx = 1
    for msg in messages:
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "user")
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        created_at = msg.get("created_at") if isinstance(msg, dict) else getattr(msg, "created_at", None)
        time_str = f" [dim white]({created_at})[/dim white]" if created_at else ""

        if role == "user":
            console.print(f"\n👤 [bold green]User (Turn #{turn_idx}):[/bold green]{time_str}")
            console.print(Panel(content, border_style="green", padding=(0, 1)))
        else:
            console.print(f"\n🤖 [bold cyan]ANT-MAN AI (Turn #{turn_idx}):[/bold cyan]{time_str}")
            md = Markdown(content)
            console.print(Panel(md, border_style="cyan", padding=(0, 1)))
            turn_idx += 1

    console.print("\n[dim cyan]───── End of Conversation History ─────[/dim cyan]\n")


def print_exit_summary(user_email: str | None, conversation_id: str | None, conversation_title: str | None = None):
    """Display session exit summary box with Conversation ID and resume instructions."""
    if conversation_id:
        summary_content = (
            f"[bold white]Active User:[/bold white] [bold green]{user_email or 'Guest'}[/bold green]\n"
            f"[bold white]Conversation Title:[/bold white] [bold yellow]{conversation_title or 'ANT-MAN Chat'}[/bold yellow]\n\n"
            f"🔑 [bold yellow]CONVERSATION ID:[/bold yellow]\n"
            f"[bold bright_cyan]{conversation_id}[/bold bright_cyan]\n\n"
            f"📋 [bold white]To resume this session next time:[/bold white]\n"
            f"  1. Paste the Conversation ID above when starting ANT-MAN CODE, OR\n"
            f"  2. Use command: [bold cyan]/resume {conversation_id}[/bold cyan]"
        )
        title = "👋 Session Ended — Save Your Conversation ID!"
        border = "bright_yellow"
    else:
        summary_content = "[bold yellow]Session ended. No active conversation was selected.[/bold yellow]"
        title = "👋 Session Ended"
        border = "red"

    console.print("\n")
    console.print(Panel(summary_content, title=f"🐜 {title}", border_style=border, padding=(1, 2)))
    console.print("[bold red]Goodbye! 🐜[/bold red]\n")

