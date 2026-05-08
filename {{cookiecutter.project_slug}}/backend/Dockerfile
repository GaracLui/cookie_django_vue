FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /usr/local/bin/uv

# Accept build args for host UID/GID
ARG UID=1000
ARG GID=1000

# Create a user that matches the host user
RUN groupadd -g ${GID} appgroup && \
    useradd -u ${UID} -g appgroup -m appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install deps as root first, then switch
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev && uv cache clean

# Give ownership to appuser
RUN chown -R appuser:appgroup /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
