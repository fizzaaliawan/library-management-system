# Slim python base image
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency configuration files
COPY pyproject.toml uv.lock ./

# Sync dependencies (without installing the root package itself first)
RUN uv sync --no-install-project --no-dev

# Copy source code and worker directories
COPY backend/app/ ./app/
COPY backend/workers/ ./workers/

# Sync/install the root package
RUN uv sync --no-dev

# Set the environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV DATABASE_URL="postgresql://postgres:postgres@postgres:5432/library_db"
ENV REDIS_URL="redis://redis:6379/0"
ENV JWT_SECRET="supersecretjwtkeythatisextremelysecure123!"

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
