FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml ./

# Configure Poetry: Don't create virtual environment (we're in Docker)
RUN poetry config virtualenvs.create false

# Install dependencies (this will regenerate the lock file if needed)
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create directory for Chroma persistence
RUN mkdir -p .chroma

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py", "--env", "local"]
