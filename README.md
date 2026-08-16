# Software Agent (Antman Code)

A multi-agent AI software engineering platform and interactive terminal interface designed to generate API routes, database schemas, and repository architecture.

![Antman Banner](agent_image.png)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.137.1-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0 Async](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-d71e00.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-red.svg)](https://alembic.sqlalchemy.org/)
[![Rich CLI](https://img.shields.io/badge/Rich-Interactive%20CLI-magenta.svg)](https://github.com/Textualize/rich)
[![MCP Ready](https://img.shields.io/badge/MCP-Standard-orange.svg)](https://modelcontextprotocol.io/)
[![uv](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://github.com/astral-sh/uv)

---

## Table of Contents

- [About the Project](#about-the-project)
  - [Background and How It Evolved](#background-and-how-it-evolved)
  - [Why the Engineering Stack Was Separated](#why-the-engineering-stack-was-separated)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [How the Engineering Stack SDK Works](#how-the-engineering-stack-sdk-works)
- [Interactive CLI (Antman) and Slash Commands](#interactive-cli-antman-and-slash-commands)
- [FastAPI REST API Reference](#fastapi-rest-api-reference)
- [Installation and Setup](#installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Database Migrations](#database-migrations)
  - [Running the CLI](#running-the-cli)
  - [Running the FastAPI Server](#running-the-fastapi-server)
  - [Running with Docker Compose](#running-with-docker-compose)
- [Model Context Protocol (MCP) Integration](#model-context-protocol-mcp-integration)
- [Running Tests](#running-tests)
- [License](#license)

---

## About the Project

Software Agent is a developer tool built to assist in writing backend code, managing database models, and navigating codebases. It combines an asynchronous FastAPI backend with an interactive terminal interface (Antman) powered by a dedicated multi-agent reasoning system.

![Architecture Diagram](image.png)

### Background and How It Evolved

This project went through several practical iterations based on real-world constraints:

1. **Initial Web Application Prototype**: The project originally started as a full web application. However, deploying and maintaining a web frontend with multi-model LLM calls proved impractical due to API key handling constraints, deployment overhead, and unnecessary friction during everyday coding.
2. **Shift to the Antman CLI**: To make the tool fast and practical, the interface was moved to the terminal as **Antman** (`ant-man`). This brought the agent directly into the developer workflow, offering interactive auto-completion, quick session switching, and built-in GitHub search without needing a browser.
3. **Overcoming Project Clutter and Folder Errors**: As the agent grew to handle more complex code generation tasks across multiple folders and files, having all the orchestration code, prompts, and application logic living together in one codebase led to confusion and frequent runtime errors.
4. **Creating the Dedicated `engineeringstack` SDK**: To solve this problem, the agent logic was completely extracted into its own standalone package called **`engineeringstack`** in a separate repository. This cleaned up the main repository, ensured cleaner code generation, and made the reasoning engine reusable across both the CLI and REST API.

### Why the Engineering Stack Was Separated

Decoupling the agent logic into the `engineeringstack` SDK provided three major benefits:

- **Cleaner Code Output**: Keeps prompt engineering, tool routing, and agent state logic separated from application routing and database operations.
- **Fewer File and Folder Errors**: Prevents the agent from getting confused by bloated project folders when generating multi-file codebases.
- **Modular Design**: The core reasoning engine can now be imported and updated independently without risking regressions in the CLI or API server.

---

## Key Features

- **Interactive Terminal Interface**: A rich terminal REPL with autocompletion for slash commands (`/help`, `/new`, `/switch`, `/history`, `/github`), session management, and formatted markdown output.
- **Decoupled Agent Reasoning**: Uses the standalone `EngineeringStack` SDK with support for Groq (`openai/gpt-oss-20b`), Ollama (`qwen2.5-coder:7b`), OpenAI, and Gemini.
- **Secure Authentication**: Argon2 password hashing via `pwdlib` and JWT access tokens for per-user conversation isolation.
- **Stateful Conversations**: Multi-turn chat history automatically stored in PostgreSQL using SQLAlchemy 2.0 Async and asyncpg.
- **GitHub Integration**: Search repositories, query code snippets, and inspect remote files directly from the command line.
- **Model Context Protocol (MCP)**: Standardized `mcp.json` configuration for PostgreSQL, GitHub, and Docker tool servers.
- **Production-Ready Containerization**: Multi-stage `Dockerfile` using `uv` for fast builds and `compose.yml` for database and backend services.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Clients
        CLI["Antman Interactive CLI (Rich / prompt_toolkit)"]
        REST["FastAPI REST Endpoints (/api/...)"]
    end

    subgraph Authentication & Security
        AUTH["JWT & Argon2 Security (app/core/security.py)"]
    end

    subgraph Data Layer
        DB[(PostgreSQL Database)]
        REPO["Repositories (Users, Conversations, Messages)"]
    end

    subgraph Agent Engine & Services
        ES["EngineeringStack SDK (Dedicated Engine)"]
        LLM["Language Models (Groq / Ollama / OpenAI / Gemini)"]
        GH["PyGithub / GitHub API"]
        MCP["MCP Servers (Postgres / GitHub / Docker)"]
    end

    CLI --> AUTH
    REST --> AUTH
    AUTH --> REPO
    REPO --> DB
    REST --> ES
    CLI --> ES
    ES --> LLM
    CLI --> GH
    ES --> MCP
```

---

## Directory Structure

```text
.
├── .antman_session.json        # Cached local user session and active conversation ID
├── .env                        # Environment variables and API keys
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Multi-stage container build
├── README.md                   # Project documentation
├── Software_db_migiration/     # Alembic database migration environment and versions
├── alembic.ini                 # Alembic configuration file
├── app/                        # Main application source code
│   ├── cli/                    # Antman CLI implementation
│   │   ├── auth.py             # Login, registration, and profile commands
│   │   ├── conversation.py     # Conversation listing, switching, and chat handlers
│   │   ├── github_cli.py       # GitHub repository and code search tools
│   │   ├── interactive.py      # Interactive REPL shell and slash command router
│   │   ├── main.py             # Typer CLI entry point
│   │   ├── mcp.py              # MCP tool definitions
│   │   └── ui.py               # Rich terminal themes, banners, and formatters
│   ├── core/                   # Configuration and security utilities
│   │   ├── config.py           # Pydantic Settings and environment variable validation
│   │   └── security.py         # Argon2 password hashing and JWT token management
│   ├── db/                     # Database setup
│   │   └── database.py         # Asynchronous SQLAlchemy engine and session factory
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── conversation_model.py
│   │   ├── messages_model.py
│   │   └── users_model.py
│   ├── repository/             # Database access layer
│   │   ├── conversation_repo.py
│   │   ├── message_repo.py
│   │   └── userautentication_repo.py
│   ├── routers/                # FastAPI endpoint routers
│   │   ├── authentication.py   # User registration endpoint
│   │   ├── conversation.py     # Conversation management endpoints
│   │   ├── message.py          # Message handling and agent invocation
│   │   └── token.py            # OAuth2 token authentication endpoint
│   ├── schema/                 # Pydantic schemas for request and response validation
│   │   ├── conversation_schema.py
│   │   ├── message_schema.py
│   │   ├── token.py
│   │   └── user_schema.py
│   └── services/               # Service layer
│       └── Agent.py            # Bridge to the EngineeringStack SDK
├── compose.yml                 # Docker Compose multi-service definition
├── main.py                     # FastAPI application entry point
├── mcp.json                    # Model Context Protocol configuration
├── pyproject.toml              # Project dependencies and CLI entry point definitions
├── secrets/                    # Secret storage (e.g. postgres_password.txt)
├── test/                       # Unit and integration test suite
└── uv.lock                     # Locked dependency tree
```

---

## How the Engineering Stack SDK Works

The project delegates agent reasoning to the separate `engineeringstack` package. This keeps the application clean and prevents bloated files from interfering with model generation:

```python
# app/services/Agent.py
from langchain.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from engineeringstack import EngineeringStack

# Configure language model
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key="<YOUR_GROQ_KEY>",
    max_retries=2
)

# Instantiate the decoupled engineering stack
agent = EngineeringStack(model=llm)

def chat(conversation_history, conversation_id: str | None = None):
    messages = [
        HumanMessage(content=msg.content) if msg.role == "user"
        else AIMessage(content=msg.content)
        for msg in conversation_history
    ]

    response = agent.invoke(
        {"messages": messages},
        thread_id=conversation_id
    )
    return response["final_answer"]
```

---

## Interactive CLI (Antman) and Slash Commands

You can run Antman directly from the terminal:

```bash
# Using uv
uv run ant-man

# Or using an installed command
ant-man
# or
software-agent
# or
ant-man-code
```

### Slash Commands Reference

| Command | Description | Example |
|---|---|---|
| `/help` | Display the list of available slash commands | `/help` |
| `/new` | Start a new conversation thread | `/new` |
| `/chats` or `/list` | List all saved conversations with index numbers | `/chats` |
| `/switch <#\|id>` | Switch the active conversation by index or UUID | `/switch 1` |
| `/history [id]` | View formatted conversation history | `/history` |
| `/auth login` | Log in with email and password | `/auth login` |
| `/auth register` | Create a new user account | `/auth register` |
| `/auth profile` | View current user profile information | `/auth profile` |
| `/auth logout` | Clear active session token | `/auth logout` |
| `/token <jwt>` | Set or update a JWT access token manually | `/token eyJhbGci...` |
| `/github user` | View authenticated GitHub profile details | `/github user` |
| `/github repos <query>` | Search GitHub repositories | `/github repos fastapi` |
| `/github code <query>` | Search code across GitHub | `/github code create_agent` |
| `/github file <owner> <repo> <path>` | Fetch and display a syntax-highlighted file | `/github file fastapi fastapi README.md` |
| `/clear` | Clear the terminal screen | `/clear` |
| `/exit` | Exit the CLI session and save progress | `/exit` |

---

## FastAPI REST API Reference

The backend can be run as a standalone REST API service:

| HTTP Method | Path | Description | Authentication |
|---|---|---|---|
| `POST` | `/api/user` | Register a new user | Public |
| `POST` | `/login/Token` | OAuth2 form login (generates bearer token) | Public |
| `POST` | `/api/token` | JSON login endpoint | Public |
| `POST` | `/api/conversation` | Create a new conversation thread | Bearer JWT |
| `GET` | `/api/conversations` | List conversations belonging to current user | Bearer JWT |
| `GET` | `/api/conversation/{id}` | Get conversation metadata | Bearer JWT |
| `DELETE` | `/api/conversation/{id}` | Delete a conversation thread | Bearer JWT |
| `POST` | `/api/conversation/{id}/message` | Send message to agent and receive response | Bearer JWT |

---

## Installation and Setup

### Prerequisites

- **Python**: Version 3.12 or newer
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- **Database**: PostgreSQL 16+ (or use the provided Docker Compose file)

### Environment Configuration

Create a `.env` file in the project root:

```env
# Database Connection
DB_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/coding_db

# Security
SECRET_KEY=your_secret_key_here

# LLM API Keys
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
NVIDIA_API_KEY=your_nvidia_key

# GitHub Access (Optional)
GITHUB_ACCESS_TOKEN=your_personal_access_token
```

Install dependencies:

```bash
uv sync
```

### Database Migrations

Apply database migrations using Alembic:

```bash
uv run alembic upgrade head
```

### Running the CLI

```bash
uv run ant-man
```

### Running the FastAPI Server

```bash
uv run uvicorn main:app --reload --port 8000
```

Once running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running with Docker Compose

To start both PostgreSQL and the FastAPI application in containers:

```bash
# Create local password secret file
mkdir -p secrets
echo "your_secure_password" > secrets/postgres_password.txt

# Start services
docker compose up --build -d
```

---

## Model Context Protocol (MCP) Integration

The project includes an `mcp.json` file configuring standard MCP servers:

- **Postgres Server**: Database schema inspection and query testing.
- **GitHub Server**: Repository metadata and code search.
- **Docker Server**: Sandboxed execution support.

---

## Running Tests

Run the test suite using pytest:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

---

## License

This project is open source and available under the MIT License.