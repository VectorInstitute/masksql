"""Utilities for asynchronous processing with rate limiting."""

import asyncio
import os
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

from tqdm.asyncio import tqdm


ASYNC_BATCH = int(os.environ.get("ASYNC_BATCH", "1"))

T = TypeVar("T")
R = TypeVar("R")


async def apply_async(
    fun: Callable[[T], Awaitable[R]], items: Iterable[T], desc: str = ""
) -> list[R]:
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

    async def sem_task(item: T) -> R:
        async with semaphore:
            return await fun(item)

    items_list = list(items)
    tasks = [asyncio.create_task(sem_task(item)) for item in items_list]
    return await tqdm.gather(*tasks, total=len(items_list), desc=desc)
