import json
from github import Github, Auth
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from .ui import console, print_success, print_error, render_code
from ..core.config import settings


def get_github_client(token: str | None = None) -> Github:
    github_token = token or settings.GITHUB_ACCESS_TOKEN
    if github_token:
        auth = Auth.Token(github_token)
        return Github(auth=auth)
    return Github()


def user_info_cmd(token: str | None = None, json_output: bool = False):
    """Fetch GitHub user info for current authenticated token."""
    try:
        gh = get_github_client(token)
        user = gh.get_user()
        res = {
            "status": "success",
            "user": {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "html_url": user.html_url,
            }
        }
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            table = Table(title="🐙 ANT-MAN GitHub User Profile", border_style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="white")
            table.add_row("Username", user.login)
            table.add_row("Name", user.name or "N/A")
            table.add_row("Email", user.email or "N/A")
            table.add_row("Public Repos", str(user.public_repos))
            table.add_row("Followers", str(user.followers))
            table.add_row("Profile URL", user.html_url)
            console.print(table)
        return res
    except Exception as e:
        res = {"status": "error", "detail": str(e)}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            print_error(f"GitHub User Error: {e}")
        return res


def search_repos_cmd(query: str, token: str | None = None, limit: int = 10, json_output: bool = False):
    """Search GitHub repositories matching a query."""
    try:
        gh = get_github_client(token)
        repos = gh.search_repositories(query=query)
        results = []
        for repo in repos[:limit]:
            results.append({
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "language": repo.language,
                "html_url": repo.html_url,
            })
        res = {"status": "success", "count": len(results), "repositories": results}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            table = Table(title=f"🔎 ANT-MAN GitHub Repository Search ('{query}')", border_style="green")
            table.add_column("Repository", style="bold yellow")
            table.add_column("Language", style="cyan")
            table.add_column("Stars", style="bold magenta")
            table.add_column("Description", style="white")
            for r in results:
                table.add_row(r["full_name"], r["language"] or "N/A", str(r["stars"]), (r["description"] or "")[:60])
            console.print(table)
        return res
    except Exception as e:
        res = {"status": "error", "detail": str(e)}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            print_error(f"GitHub Search Error: {e}")
        return res


def search_code_cmd(query: str, token: str | None = None, limit: int = 10, json_output: bool = False):
    """Search code across GitHub repositories."""
    try:
        gh = get_github_client(token)
        code_results = gh.search_code(query=query)
        results = []
        for file in code_results[:limit]:
            results.append({
                "name": file.name,
                "path": file.path,
                "repo": file.repository.full_name,
                "html_url": file.html_url,
            })
        res = {"status": "success", "count": len(results), "code_results": results}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            table = Table(title=f"💻 ANT-MAN GitHub Code Search ('{query}')", border_style="magenta")
            table.add_column("File Name", style="bold yellow")
            table.add_column("Path", style="cyan")
            table.add_column("Repository", style="bold white")
            for c in results:
                table.add_row(c["name"], c["path"], c["repo"])
            console.print(table)
        return res
    except Exception as e:
        res = {"status": "error", "detail": str(e)}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            print_error(f"GitHub Code Search Error: {e}")
        return res


def get_file_cmd(owner: str, repo: str, path: str, token: str | None = None, json_output: bool = False):
    """Fetch content of a file from a GitHub repository."""
    try:
        gh = get_github_client(token)
        repository = gh.get_repo(f"{owner}/{repo}")
        file_content = repository.get_contents(path)
        content_decoded = file_content.decoded_content.decode("utf-8")
        res = {
            "status": "success",
            "file": {
                "name": file_content.name,
                "path": file_content.path,
                "sha": file_content.sha,
                "size": file_content.size,
                "content": content_decoded,
            }
        }
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            lang = "python"
            if path.endswith(".js") or path.endswith(".ts"):
                lang = "javascript"
            elif path.endswith(".json"):
                lang = "json"
            elif path.endswith(".md"):
                lang = "markdown"
            elif path.endswith(".html"):
                lang = "html"
            render_code(content_decoded, language=lang, filename=f"{owner}/{repo}:{path}")
        return res
    except Exception as e:
        res = {"status": "error", "detail": str(e)}
        if json_output:
            print(json.dumps(res, indent=2))
        else:
            print_error(f"GitHub File Fetch Error: {e}")
        return res
