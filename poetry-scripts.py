#!/usr/bin/env python3
"""
Poetry scripts for the wp-codex-rag project
"""
import os
import subprocess
import sys


def start():
    """Start the development server with live reload"""
    os.environ["ENV"] = "local"
    os.environ["DEBUG"] = "true"
    subprocess.run(
        [
            "uvicorn",
            "app.server:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
        ],
        check=False,
    )


def migrate():
    """Run database migrations"""
    subprocess.run(["alembic", "upgrade", "head"], check=False)


def migrate_create():
    """Create a new migration"""
    subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "auto migration"], check=False
    )


def test():
    """Run tests"""
    subprocess.run(["pytest"], check=False)


def test_cov():
    """Run tests with coverage"""
    subprocess.run(["pytest", "--cov=app", "--cov-report=html"], check=False)


def seed():
    """Seed the vector database with WordPress Codex documentation"""
    subprocess.run([sys.executable, "scripts/ingest_wp_codex.py"], check=False)


def check_chroma():
    """Check ChromaDB data and collections"""
    # Pass all arguments after 'check-chroma' to the script
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    subprocess.run([sys.executable, "scripts/check_chroma_db.py"] + args, check=False)


def docker_up():
    """Start Docker services (MySQL and Redis)"""
    subprocess.run(
        ["docker-compose", "-f", "docker/docker-compose.yml", "up", "mysql", "redis"],
        check=False,
    )


def docker_down():
    """Stop Docker services"""
    subprocess.run(
        ["docker-compose", "-f", "docker/docker-compose.yml", "down"], check=False
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Available commands: start, migrate, migrate-create, test, test-cov, seed, check-chroma, docker-up"
        )
        sys.exit(1)

    command = sys.argv[1]
    if command == "start":
        start()
    elif command == "migrate":
        migrate()
    elif command == "migrate-create":
        migrate_create()
    elif command == "test":
        test()
    elif command == "test-cov":
        test_cov()
    elif command == "seed":
        seed()
    elif command == "check-chroma":
        check_chroma()
    elif command == "docker-up":
        docker_up()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
