"""Main entry point for the MaskSQL pipeline."""

import argparse
import asyncio
import shutil

from dotenv import load_dotenv

from src.utils.logging import configure_logging


load_dotenv()

from src.masksql import MaskSQL  # noqa: E402


async def main() -> None:
    """Run the MaskSQL main pipeline."""
    parser = argparse.ArgumentParser(description="MaskSQL")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean cached files from cache directory",
    )
    parser.add_argument(
        "-c", "--config", default="configs/conf.yaml", help="Path to config file"
    )
    args = parser.parse_args()
    configure_logging()

    mask_sql = MaskSQL.from_config(args.config)

    if args.clean:
        shutil.rmtree(mask_sql.conf.cache_dir, ignore_errors=True)
    else:
        await mask_sql.evaluate()


if __name__ == "__main__":
    asyncio.run(main())
