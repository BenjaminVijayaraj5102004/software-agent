import asyncio
import json
from uuid import UUID
from sqlalchemy import select
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from .ui import console, print_success, print_error, print_info, render_markdown, render_chat_history
from ..db.database import SessionLocal
from ..models.users_model import User
from ..core.security import verify_access_token
from ..repository.conversation_repo import ConversationRepository
from ..repository.message_repo import MessageRepository
from ..services.Agent import chat

conversation_repo = ConversationRepository()
message_repo = MessageRepository()


async def resolve_conversation_id(db, user_id, input_id: str | None) -> str | None:
    """Resolve a conversation UUID or 1-based index string (e.g., '1') to a valid UUID string strictly for user_id."""
    if not input_id or not str(input_id).strip():
        return None
    input_str = str(input_id).strip()

    if input_str.isdigit():
        idx = int(input_str)
        conversations = await conversation_repo.get_conversations_list(db=db, user_id=user_id)
        if 1 <= idx <= len(conversations):
            return str(conversations[idx - 1].id)
        return None

    try:
        val = UUID(input_str)
        return str(val)
    except ValueError:
        pass

    return input_str


async def get_user_from_token(db, token: str | None = None) -> User:
    """Strictly verify JWT access token and return authorized User object."""
    if token:
        email = verify_access_token(token)
        if email:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                return user

    raise ValueError("Authentication error: Missing or invalid JWT access token. Please log in first.")



async def create_conversation_cmd(title: str, token: str | None = None, json_output: bool = False, silent: bool = False):
    """Create a new conversation."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        conv = await conversation_repo.create_conversation(
            db=db, title=title, user_id=user.id
        )
        res = {
            "status": "success",
            "conversation": {
                "id": str(conv.id),
                "title": conv.title,
                "user_id": str(conv.user_id),
                "created_at": str(conv.created_at) if hasattr(conv, "created_at") else None,
            }
        }
        if not silent:
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_success(f"Created conversation: [bold cyan]{conv.title}[/bold cyan]")
                console.print(Panel(f"[bold yellow]Conversation ID:[/bold yellow] {conv.id}\n[bold white]Title:[/bold white] {conv.title}", title="💬 ANT-MAN Conversation", border_style="cyan"))
        return res


async def list_conversations_cmd(token: str | None = None, json_output: bool = False, silent: bool = False):
    """List all user conversations."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        conversations = await conversation_repo.get_conversations_list(
            db=db, user_id=user.id
        )
        items = [
            {
                "index": idx,
                "id": str(c.id),
                "title": c.title,
                "created_at": str(c.created_at) if hasattr(c, "created_at") else None,
            }
            for idx, c in enumerate(conversations, 1)
        ]
        res = {"status": "success", "conversations": items}
        if not silent:
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                if not conversations:
                    print_info("No conversations found. Create one using `conversation create` or start typing your query.")
                else:
                    table = Table(title="💬 ANT-MAN Active Conversations", border_style="green")
                    table.add_column("#", style="bold bright_magenta", justify="center")
                    table.add_column("Conversation ID", style="bold yellow")
                    table.add_column("Title", style="bold cyan")
                    table.add_column("Created At", style="white")
                    for idx, c in enumerate(conversations, 1):
                        table.add_row(f"[{idx}]", str(c.id), c.title, str(c.created_at) if hasattr(c, "created_at") else "N/A")
                    console.print(table)
                    console.print("[dim white]💡 Type [/dim white][bold cyan]/switch <#>[/bold cyan][dim white] or [/dim white][bold cyan]/history <#>[/bold cyan][dim white] to switch or view history by index number.[/dim white]\n")
        return res


async def get_conversation_cmd(conversation_id: str, token: str | None = None, json_output: bool = False, silent: bool = False):
    """Get details of a specific conversation."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        resolved_id = await resolve_conversation_id(db, user.id, conversation_id)
        if not resolved_id:
            res = {"status": "error", "detail": f"Conversation '{conversation_id}' not found for user."}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error(f"Conversation '{conversation_id}' not found. Type /list to see your active conversations.")
            return res

        try:
            conv_uuid = UUID(resolved_id)
        except (ValueError, TypeError):
            res = {"status": "error", "detail": "Invalid conversation UUID format"}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error("Invalid conversation UUID format")
            return res

        conv = await conversation_repo.get_conversation_by_id(
            db=db, conversation_id=conv_uuid, user_id=user.id
        )
        if not conv:
            res = {"status": "error", "detail": "Conversation not found"}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error("Conversation not found")
            return res

        res = {
            "status": "success",
            "conversation": {
                "id": str(conv.id),
                "title": conv.title,
                "user_id": str(conv.user_id),
                "created_at": str(conv.created_at) if hasattr(conv, "created_at") else None,
            }
        }
        if not silent:
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                console.print(Panel(f"[bold yellow]ID:[/bold yellow] {conv.id}\n[bold white]Title:[/bold white] {conv.title}", title=f"💬 Conversation Details", border_style="cyan"))
        return res


async def delete_conversation_cmd(conversation_id: str, token: str | None = None, json_output: bool = False, silent: bool = False):

    """Delete a conversation."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        resolved_id = await resolve_conversation_id(db, user.id, conversation_id)
        try:
            conv_uuid = UUID(resolved_id)
        except (ValueError, TypeError):
            res = {"status": "error", "detail": "Invalid conversation UUID format"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("Invalid conversation UUID format")
            return res

        conv = await conversation_repo.delete_conversation_by_id(
            db=db, conversation_id=conv_uuid, user_id=user.id
        )
        if not conv:
            res = {"status": "error", "detail": "Conversation not found"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("Conversation not found")
            return res

        res = {"status": "success", "message": "Conversation deleted successfully"}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            print_success(f"Deleted conversation {conversation_id}")
        return res


async def chat_cmd(conversation_id: str, message: str, token: str | None = None, json_output: bool = False):
    """Send a user message to a conversation and get the AI agent response."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        resolved_id = await resolve_conversation_id(db, user.id, conversation_id)
        try:
            conv_uuid = UUID(resolved_id)
        except (ValueError, TypeError):
            res = {"status": "error", "detail": "Invalid conversation UUID format"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("Invalid conversation UUID format")
            return res

        conv = await message_repo.get_conversation(
            db=db, conversation_id=conv_uuid, user_id=user.id
        )
        if not conv:
            res = {"status": "error", "detail": "Conversation not found"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("Conversation not found")
            return res

        # Create user message
        await message_repo.create_message(
            db=db, conversation_id=conv_uuid, role="user", content=message
        )

        # Get recent messages history
        history = await message_repo.get_recent_messages(
            db=db, conversation_id=conv_uuid, limit=20
        )

        user_name = getattr(user, "name", None)

        if not json_output:
            with console.status("[antman]🐜 ANT-MAN Code Agent is thinking...[/antman] [bold cyan]Tokens: ~0 intake │ ~0 output[/bold cyan]", spinner="dots") as status:
                def live_token_callback(intake: int, output: int, tools: list):
                    tools_str = f" │ Tools: {', '.join(tools)}" if tools else ""
                    status.update(
                        f"[antman]🐜 ANT-MAN Code Agent is thinking...[/antman] "
                        f"[bold cyan]Tokens: ~{intake} intake │ ~{output} output{tools_str}[/bold cyan]"
                    )

                ai_response = await asyncio.to_thread(
                    chat,
                    conversation_history=history,
                    user_name=user_name,
                    conversation_id=str(conv_uuid),
                )
                tools_called, token_stats = [], {}
        else:
            ai_response = await asyncio.to_thread(
                chat,
                conversation_history=history,
                user_name=user_name,
                conversation_id=str(conv_uuid),
            )
            tools_called, token_stats = [], {}

        # Create assistant message
        assistant_message = await message_repo.create_message(
            db=db, conversation_id=conv_uuid, role="assistant", content=ai_response
        )

        res = {
            "status": "success",
            "response": {
                "id": str(assistant_message.id),
                "conversation_id": str(assistant_message.conversation_id),
                "role": assistant_message.role,
                "content": assistant_message.content,
                "tools_called": tools_called,
                "token_usage": token_stats,
                "created_at": str(assistant_message.created_at) if hasattr(assistant_message, "created_at") else None,
            }
        }
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            render_markdown(ai_response, title=f"ANT-MAN CODE AI Agent Response", tools_called=tools_called, token_stats=token_stats)
        return res


async def get_conversation_history_cmd(conversation_id: str | None = None, token: str | None = None, limit: int = 50, json_output: bool = False):
    """Retrieve chat history for a conversation."""
    async with SessionLocal() as db:
        user = await get_user_from_token(db, token)

        resolved_id = await resolve_conversation_id(db, user.id, conversation_id)
        if not resolved_id:
            # Fallback to the latest active conversation for the user
            conversations = await conversation_repo.get_conversations_list(db=db, user_id=user.id)
            if conversations:
                resolved_id = str(conversations[0].id)

        if not resolved_id:
            res = {"status": "error", "detail": "No active conversation found"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("No active conversation found. Type your query first to auto-create one.")
            return res

        try:
            conv_uuid = UUID(resolved_id)
        except (ValueError, TypeError):
            res = {"status": "error", "detail": "Invalid conversation UUID format"}
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_error("Invalid conversation UUID format")
            return res

        conv = await conversation_repo.get_conversation_by_id(db=db, conversation_id=conv_uuid, user_id=user.id)
        conv_title = conv.title if conv else "ANT-MAN Chat"

        messages = await message_repo.get_recent_messages(
            db=db, conversation_id=conv_uuid, limit=limit
        )
        msg_list = [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "created_at": str(m.created_at) if hasattr(m, "created_at") else None,
            }
            for m in messages
        ]
        res = {"status": "success", "conversation_id": str(conv_uuid), "title": conv_title, "messages": msg_list}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            render_chat_history(conv_title, str(conv_uuid), messages)
        return res


