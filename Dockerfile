# ---- Build Stage ----
FROM python:3.14-slim AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev group) into the project virtual env
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application source
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev


# ---- Runtime Stage ----
FROM python:3.14-slim AS runtime

WORKDIR /app

# Copy the entire app + virtual env from builder
COPY --from=builder /app /app

# Add the virtual env to PATH so `uvicorn` is available
ENV PATH="/app/.venv/bin:$PATH"

# Expose the default uvicorn port
EXPOSE 8000

# Run the FastAPI app via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
