import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from bot.main_bot import run_bot
from config.settings import get_settings
from db.database_setup import init_db, init_db_connection

_STARTUP_BANNER = r"""
              ~ ~ ~  r e m n a w a v e  ~ ~ ~

  ███╗   ███╗██╗███╗   ██╗██╗███████╗██╗  ██╗ ██████╗ ██████╗
  ████╗ ████║██║████╗  ██║██║██╔════╝██║  ██║██╔═══██╗██╔══██╗
  ██╔████╔██║██║██╔██╗ ██║██║███████╗███████║██║   ██║██████╔╝
  ██║╚██╔╝██║██║██║╚██╗██║██║╚════██║██╔══██║██║   ██║██╔═══╝
  ██║ ╚═╝ ██║██║██║ ╚████║██║███████║██║  ██║╚██████╔╝██║
  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝

         https://github.com/3252a8/remnawave-minishop
"""


def _print_startup_banner() -> None:
    # Bypass the logging formatter so the ASCII art renders without per-line
    # timestamp/level prefixes mangling the box characters.
    try:
        sys.stdout.write(_STARTUP_BANNER + "\n")
        sys.stdout.flush()
    except Exception:
        # Banner is purely cosmetic; never fail startup over it.
        pass


def _resolve_log_level(value: str) -> int:
    return getattr(logging, value.upper(), logging.INFO)


async def main():
    settings = get_settings()

    session_factory = init_db_connection(settings)
    if not session_factory:
        logging.critical("Failed to initialize DB connection and session factory. Exiting.")
        return

    await init_db(settings, session_factory)

    await run_bot(settings)


if __name__ == "__main__":
    _print_startup_banner()
    load_dotenv()
    logging.basicConfig(
        level=_resolve_log_level(os.getenv("LOG_LEVEL", "INFO")),
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually")
    except Exception as e_global:
        logging.critical(f"Global unhandled exception in main: {e_global}", exc_info=True)
        sys.exit(1)
