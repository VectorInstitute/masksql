"""Utilities for asynchronous processing with rate limiting."""

import asyncio
import os

from tqdm.asyncio import tqdm


ASYNC_BATCH = int(os.environ.get("ASYNC_BATCH", "1"))


async def apply_async(fun, items, desc=""):
    """
    Apply async function to items with rate limiting and progress tracking.

    Parameters
    ----------
    fun : callable
        Async function to apply to each item.
    items : iterable
        Items to process.
    desc : str, optional
        Description for progress bar, by default "".

    Returns
    -------
    list
        Results from processing all items.
    """
    semaphore = asyncio.Semaphore(ASYNC_BATCH)

    async def sem_task(item):
        async with semaphore:
            return await fun(item)

    tasks = [asyncio.create_task(sem_task(item)) for item in items]
    return await tqdm.gather(*tasks, total=len(items), desc=desc)
