FROM python:3.12-slim

WORKDIR /app

# Copy project definition and source before installing
# (setuptools needs src/ to discover packages)
COPY pyproject.toml ./
COPY src/ ./src/

# Install production dependencies
RUN pip install --no-cache-dir .

# Create non-root user and transfer ownership
RUN useradd --no-create-home --shell /bin/bash appuser \
    && chown -R appuser /app

USER appuser

EXPOSE 8000

# Production command (docker-compose.yml overrides this with --reload for dev)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
