"""Utilities for asynchronous processing with rate limiting."""

import asyncio
import os
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from src.utils.logging import console


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
    total = len(items_list)

    # Create rich progress bar with custom columns
    progress = Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None, complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    with progress:
        task_id = progress.add_task(desc, total=total)

        # Create tasks and track completion
        tasks = [asyncio.create_task(sem_task(item)) for item in items_list]

        # Wait for all tasks to complete while updating progress
        for coro in asyncio.as_completed(tasks):
            await coro
            progress.update(task_id, advance=1)

        # Gather results in original order
        return [await task for task in tasks]
