# Use a slim Python base image
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency configuration files
COPY pyproject.toml uv.lock ./

# Sync dependencies (without installing the root package itself first)
RUN uv sync --no-install-project --no-dev

# Copy source code
COPY cli/src/ ./src/

# Sync/install the root package
RUN uv sync --no-dev

# Set the environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV DATABASE_URL="postgresql://postgres:postgres@postgres:5432/library_db"

# Default command to show help
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--help"]
