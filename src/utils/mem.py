"""Memory usage monitoring utilities."""

import logging
import os
import threading
import time
from collections.abc import Awaitable, Callable
from typing import Any

import psutil


logger = logging.getLogger(__name__)


def _monitor_memory(
    interval: float, stop_event: threading.Event, mem_usage: list[float]
) -> None:
    process = psutil.Process(os.getpid())
    sample_count = 0
    while not stop_event.is_set():
        rss = process.memory_info().rss / (1024 * 1024)
        mem_usage.append(rss)
        # Only log every 10th sample to reduce verbosity
        sample_count += 1
        if sample_count % 10 == 0:
            logger.debug(f"[yellow]Memory[/yellow]: {rss:.1f} MB")
        time.sleep(interval)


async def track_memory_async(
    coro: Callable[..., Awaitable[Any]], *args: Any, interval: float = 1, **kwargs: Any
) -> tuple[Any, float, float]:
    """
    Track memory usage during coroutine execution.

    Parameters
    ----------
    coro : coroutine
        Coroutine to execute and monitor
    *args
        Positional arguments for coroutine
    interval : float, optional
        Memory sampling interval in seconds, default 1
    **kwargs
        Keyword arguments for coroutine

    Returns
    -------
    tuple
        (result, average_memory_mb, peak_memory_mb)
    """
    mem_usage: list[float] = []
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=_monitor_memory, args=(interval, stop_event, mem_usage)
    )
    monitor_thread.start()

    try:
        result = await coro(*args, **kwargs)
    finally:
        stop_event.set()
        monitor_thread.join()

    avg_mem = sum(mem_usage) / len(mem_usage) if mem_usage else 0
    peak_mem = max(mem_usage) if mem_usage else 0
    # print("MEM USAGE LEN: ", len(mem_usage))
    # print("MEM USAGE SUM: ", sum(mem_usage))
    return result, avg_mem, peak_mem
