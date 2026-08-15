from datetime import timedelta
import json
from sqlalchemy import select
from rich.panel import Panel
from rich.table import Table
from .ui import console, print_success, print_error
from ..db.database import SessionLocal
from ..repository.userautentication_repo import userauthentication
from ..models.users_model import User
from ..core.config import settings
from ..core.security import (
    create_access_token,
    verify_password,
    verify_access_token,
)

user_repo = userauthentication()


async def register_cmd(email: str, password: str, name: str | None = None, json_output: bool = False, silent: bool = False):
    """Register a new user via CLI."""
    async with SessionLocal() as db:
        try:
            db_user = await user_repo.user_auth(
                db=db,
                email=email,
                password_hash=password,
                name=name
            )
            res = {
                "status": "success",
                "message": "User registered successfully",
                "user": {
                    "id": str(db_user.id),
                    "email": db_user.email,
                }
            }
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_success("User registered successfully!")
                    table = Table(title="🐜 User Registration Details", border_style="cyan")
                    table.add_column("Field", style="bold yellow")
                    table.add_column("Value", style="bold white")
                    table.add_row("User ID", str(db_user.id))
                    table.add_row("Email", db_user.email)
                    console.print(table)
            return res
        except Exception as e:
            res = {"status": "error", "detail": str(e)}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error(f"Registration failed: {e}")
            return res


async def login_cmd(email: str, password: str, json_output: bool = False, silent: bool = False):
    """Login user and return JWT access token via CLI."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            res = {"status": "error", "detail": "Invalid email address"}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error("Invalid email address")
            return res

        if not verify_password(password, db_user.password_hash):
            res = {"status": "error", "detail": "Invalid password"}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error("Invalid password")
            return res

        token = create_access_token(
            data={"sub": db_user.email},
            expires_delta=timedelta(hours=settings.cli_access_token_expire_hours)
        )
        res = {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(db_user.id),
                "email": db_user.email,
            }
        }
        if not silent:
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_success(f"Authenticated as [bold cyan]{db_user.email}[/bold cyan]")
                panel_content = (
                    f"[bold green]User ID:[/bold green] {db_user.id}\n"
                    f"[bold white]Email:[/bold white] {db_user.email}\n"
                    f"[bold yellow]JWT Token:[/bold yellow] [dim white]•••••••••••• (Hidden for security)[/dim white]"
                )
                console.print(Panel(panel_content, title="🔑 Authorized Session Active", border_style="green"))
        return res


async def me_cmd(token: str | None = None, json_output: bool = False, silent: bool = False):
    """Verify access token and return user details via CLI."""
    async with SessionLocal() as db:
        db_user = None
        if token:
            email = verify_access_token(token)
            if email:
                result = await db.execute(select(User).where(User.email == email))
                db_user = result.scalar_one_or_none()

        if not db_user:
            res = {"status": "error", "detail": "Invalid or missing JWT token. Authentication required."}
            if not silent:
                if json_output:
                    print(json.dumps(res, indent=2))
                else:
                    print_error("Invalid or missing JWT token. Please log in.")
            return res

        res = {
            "status": "success",
            "user": {
                "id": str(db_user.id),
                "email": db_user.email,
                "created_at": str(db_user.created_at) if hasattr(db_user, "created_at") else None,
            }
        }
        if not silent:
            if json_output:
                print(json.dumps(res, indent=2))
            else:
                print_success("Token validated successfully")
                table = Table(title="👤 ANT-MAN User Profile", border_style="magenta")
                table.add_column("Property", style="bold yellow")
                table.add_column("Details", style="cyan")
                table.add_row("User ID", str(db_user.id))
                table.add_row("Email", db_user.email)
                table.add_row("Created At", str(db_user.created_at) if hasattr(db_user, "created_at") else "N/A")
                console.print(table)
        return res


