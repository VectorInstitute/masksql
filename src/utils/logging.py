"""Logging configuration utilities using rich library."""

import os
import sys
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.traceback import install as install_rich_traceback


# Configure rich console for logging
console = Console(stderr=True, force_terminal=True)

# Stage timing tracker
_stage_timings: list[tuple[str, float]] = []

# Environment variable for log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Install rich traceback handler for better exception formatting
install_rich_traceback(console=console, show_locals=False, width=100, word_wrap=True)


def log_panel(message: str, **kwargs: Any) -> None:
    """Log an error message in a styled box.

    Parameters
    ----------
    message : str
        The error message to display
    **kwargs : Any
        Additional context information to include in the error box
    """
    # Build error content
    error_text = Text()
    error_text.append(message, style="bold red")

    if kwargs:
        error_text.append("\n\n", style="")
        error_text.append("Context:\n", style="bold yellow")
        for key, value in kwargs.items():
            error_text.append(f"  {key}: ", style="cyan")
            error_text.append(f"{value}\n", style="white")

    # Display in a red panel
    panel = Panel(
        error_text,
        title="[bold red]ERROR",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def configure_logging() -> None:
    """Configure Python logging with rich formatting and custom handlers."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        colorize=True,
        backtrace=False,
        catch=False,
        format="<level>[{level:>7}]: {message}</level>",
    )
    logger.add(
        "logs/debug-{time:MMMD-HH-mm}.log",
        level="DEBUG",
        format="[{time:HH:mm:ss}]-[{level:<7}]-[{name:>20} | {function:<25}:{line:<3}]: {message}",
    )

    logger.add(
        "logs/prompts-{time:MMMD-HH-mm}.jsonl",
        level="DEBUG",
        filter=lambda record: record["extra"].get("type") == "prompt",
        format="{message}",
        serialize=True,
    )


def log_pipeline_summary(
    total_time: float,
    avg_memory: float,
    peak_memory: float,
    results: dict[str, Any] | None = None,
) -> None:
    """Log a comprehensive pipeline execution summary.

    Parameters
    ----------
    total_time : float
        Total pipeline execution time in seconds
    avg_memory : float
        Average memory usage in MB
    peak_memory : float
        Peak memory usage in MB
    results : dict, optional
        Optional results dictionary to display
    """
    console.print("\n")

    # Create timing summary table
    timing_table = Table(
        title="[bold cyan]Pipeline Execution Summary[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold cyan",
    )

    timing_table.add_column("Stage", style="cyan", no_wrap=True, width=30)
    timing_table.add_column("Time", style="yellow", justify="right", width=12)
    timing_table.add_column("% of Total", style="green", justify="right", width=12)

    # Add stage timings
    for stage_name, elapsed_time in _stage_timings:
        percentage = (elapsed_time / total_time * 100) if total_time > 0 else 0

        # Color code based on percentage
        if percentage > 50:
            pct_color = "red"
        elif percentage > 25:
            pct_color = "yellow"
        else:
            pct_color = "green"

        timing_table.add_row(
            stage_name,
            f"{elapsed_time:.3f}s",
            f"[{pct_color}]{percentage:.1f}%[/{pct_color}]",
        )

    # Add separator and total
    timing_table.add_section()
    timing_table.add_row(
        "[bold]Total Time[/bold]",
        f"[bold]{total_time:.3f}s[/bold]",
        "[bold]100.0%[/bold]",
    )

    console.print(timing_table)

    # Memory usage summary
    console.print("\n[bold cyan]Memory Usage:[/bold cyan]")
    memory_table = Table(
        show_header=False,
        border_style="blue",
        box=None,
        pad_edge=False,
    )
    memory_table.add_column("Metric", style="cyan", width=20)
    memory_table.add_column("Value", style="yellow", justify="right")

    memory_table.add_row("Average", f"{avg_memory:.2f} MB")
    memory_table.add_row("Peak", f"{peak_memory:.2f} MB")

    console.print(memory_table)

    # Results summary if provided
    if results:
        console.print("\n[bold cyan]Results:[/bold cyan]")
        results_table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="green",
        )
        results_table.add_column("Metric", style="cyan", width=20)
        results_table.add_column("Value", style="yellow", justify="right", width=15)

        for key, value in results.items():
            formatted_value = f"{value:.6f}" if isinstance(value, float) else str(value)
            results_table.add_row(key, formatted_value)

        console.print(results_table)

    console.print("\n")


P = ParamSpec("P")
R = TypeVar("R")
AR = Awaitable[R]


def log(
    message: str = "", before: str | None = None
) -> Callable[[Callable[P, AR]], Callable[P, AR]]:
    """Log messages before and after an async function execution."""

    def decorator(func: Callable[P, AR]) -> Callable[P, AR]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AR:
            if before is not None:
                logger.info(before.format(*args, **kwargs))
            result = await func(*args, **kwargs)
            logger.info(message.format(*args, **kwargs))
            return result

        return wrapper

    return decorator
