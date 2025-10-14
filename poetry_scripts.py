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
    # Poetry strips the first argument, so we need to reconstruct it
    import sys
    
    # Get all arguments after the command name
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # If the first arg is not --action, assume it's the action value
    if args and not args[0].startswith('--'):
        # Insert --action before the first argument
        args = ['--action'] + args
    
    # Run the script with reconstructed arguments
    cmd = [sys.executable, "scripts/check_chroma_db.py"] + args
    subprocess.run(cmd, check=False)


def docker_up():
    """Start Docker services (Redis)"""
    subprocess.run(
        ["docker-compose", "-f", "docker/docker-compose.yml", "up", "redis"],
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
            "Available commands: start, test, test-cov, seed, check-chroma, docker-up"
        )
        sys.exit(1)

    command = sys.argv[1]
    if command == "start":
        start()
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
