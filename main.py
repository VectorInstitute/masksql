"""Main entry point for the MaskSQL pipeline."""

import argparse
import asyncio
import logging
import shutil
from pathlib import Path

from src.masksql import MaskSQL
from src.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def clean_cache_directory(cache_dir: str) -> None:
    """Clean intermediate files from the data directory.

    Removes files matching the pattern [0-9]*_* but excludes files starting with 1_*.
    This is used to clean up intermediate pipeline output files while preserving
    the initial input files.

    Parameters
    ----------
    cache_dir : str
        Path to the cache directory to clean.
    """
    cache_path = Path(cache_dir)

    if not cache_path.exists():
        logger.error(f"Data directory does not exist: {cache_dir}")
        return

    shutil.rmtree(cache_path)

    logger.info("Cleanup complete")


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
        clean_cache_directory(mask_sql.conf.cache_dir)
    else:
        await mask_sql.evaluate()


if __name__ == "__main__":
    asyncio.run(main())
