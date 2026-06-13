"""OmniFlow 入口 - python -m omniflow."""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from .server import main as server_main


def main():
    """主入口函数."""
    asyncio.run(server_main())


if __name__ == "__main__":
    main()
