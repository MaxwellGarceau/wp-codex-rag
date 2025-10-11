#!/usr/bin/env python3
"""
Poetry scripts for the wp-codex-rag project
"""
import subprocess
import sys
import os


def start():
    """Start the development server with live reload"""
    os.environ["ENV"] = "local"
    os.environ["DEBUG"] = "true"
    subprocess.run([
        "uvicorn",
        "app.server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])


def migrate():
    """Run database migrations"""
    subprocess.run(["alembic", "upgrade", "head"])


def migrate_create():
    """Create a new migration"""
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "auto migration"])


def test():
    """Run tests"""
    subprocess.run(["pytest"])


def test_cov():
    """Run tests with coverage"""
    subprocess.run(["pytest", "--cov=app", "--cov-report=html"])


def seed():
    """Seed the database"""
    subprocess.run([sys.executable, "scripts/ingest_wp_codex.py"])


def docker_up():
    """Start Docker services (MySQL and Redis)"""
    subprocess.run(["docker-compose", "-f", "docker/docker-compose.yml", "up", "mysql", "redis"])

def docker_down():
    """Stop Docker services"""
    subprocess.run(["docker-compose", "-f", "docker/docker-compose.yml", "down"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Available commands: start, migrate, migrate-create, test, test-cov, seed, docker-up")
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
    elif command == "docker-up":
        docker_up()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
