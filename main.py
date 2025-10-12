import os

import click
import uvicorn

from core.config import config
from core.logging_config import setup_logging


@click.command()
@click.option(
    "--env",
    type=click.Choice(["local", "dev", "prod"], case_sensitive=False),
    default="local",
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
def main(env: str, debug: bool):
    os.environ["ENV"] = env
    os.environ["DEBUG"] = str(debug)

    # Initialize logging configuration
    setup_logging()

    uvicorn.run(
        app="app.server:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.ENV != "production",
        workers=1,
    )


if __name__ == "__main__":
    main()
