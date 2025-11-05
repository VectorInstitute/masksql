"""Logging configuration utilities using rich library."""

import logging
import os
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
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


def configure_logging() -> None:
    """Configure Python logging with rich formatting and custom handlers.

    This function sets up logging with:
    - Rich colored console output
    - Concise timestamp format
    - Different colors for different log levels
    - Enhanced traceback formatting for exceptions
    """
    # Remove existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create rich handler with custom formatting
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        show_level=True,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True,
        log_time_format="[%H:%M:%S]",
        omit_repeated_times=False,
    )

    # Minimal formatter for cleaner output
    rich_handler.setFormatter(
        logging.Formatter(
            fmt="%(message)s",
            datefmt="[%X]",
        )
    )

    # Configure root logger
    root_logger.addHandler(rich_handler)
    root_logger.setLevel(LOG_LEVEL)

    # Silence verbose HTTP request logs from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def log_error(message: str, **kwargs: Any) -> None:
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


def log_warning(message: str, **kwargs: Any) -> None:
    """Log a warning message in a styled box.

    Parameters
    ----------
    message : str
        The warning message to display
    **kwargs : Any
        Additional context information to include in the warning box
    """
    # Build warning content
    warning_text = Text()
    warning_text.append(message, style="bold yellow")

    if kwargs:
        warning_text.append("\n\n", style="")
        warning_text.append("Context:\n", style="bold cyan")
        for key, value in kwargs.items():
            warning_text.append(f"  {key}: ", style="cyan")
            warning_text.append(f"{value}\n", style="white")

    # Display in a yellow panel
    panel = Panel(
        warning_text,
        title="[bold yellow]WARNING",
        border_style="yellow",
        padding=(1, 2),
    )
    console.print(panel)


def log_success(message: str, **kwargs: Any) -> None:
    """Log a success message in a styled box.

    Parameters
    ----------
    message : str
        The success message to display
    **kwargs : Any
        Additional context information to include in the success box
    """
    # Build success content
    success_text = Text()
    success_text.append(message, style="bold green")

    if kwargs:
        success_text.append("\n\n", style="")
        success_text.append("Details:\n", style="bold cyan")
        for key, value in kwargs.items():
            success_text.append(f"  {key}: ", style="cyan")
            success_text.append(f"{value}\n", style="white")

    # Display in a green panel
    panel = Panel(
        success_text,
        title="[bold green]SUCCESS",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def log_info(message: str, **kwargs: Any) -> None:
    """Log an info message in a styled box.

    Parameters
    ----------
    message : str
        The info message to display
    **kwargs : Any
        Additional context information to include in the info box
    """
    # Build info content
    info_text = Text()
    info_text.append(message, style="bold blue")

    if kwargs:
        info_text.append("\n\n", style="")
        info_text.append("Details:\n", style="bold cyan")
        for key, value in kwargs.items():
            info_text.append(f"  {key}: ", style="cyan")
            info_text.append(f"{value}\n", style="white")

    # Display in a blue panel
    panel = Panel(
        info_text,
        title="[bold blue]INFO",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


# Create a logger instance that can be imported
logger = logging.getLogger("masksql")


def log_stage_start(stage_name: str) -> None:
    """Log the start of a pipeline stage.

    Parameters
    ----------
    stage_name : str
        Name of the pipeline stage starting
    """
    console.print(
        f"\n[bold cyan]▶ Starting Stage:[/bold cyan] [bold white]{stage_name}[/bold white]"
    )


def log_stage_complete(stage_name: str, elapsed_time: float) -> None:
    """Log the completion of a pipeline stage with timing.

    Parameters
    ----------
    stage_name : str
        Name of the pipeline stage completed
    elapsed_time : float
        Time taken to complete the stage in seconds
    """
    # Store timing for summary
    _stage_timings.append((stage_name, elapsed_time))

    # Format time with appropriate precision and color
    if elapsed_time < 1.0:
        time_str = f"{elapsed_time:.3f}s"
        time_color = "green"
    elif elapsed_time < 10.0:
        time_str = f"{elapsed_time:.2f}s"
        time_color = "yellow"
    else:
        time_str = f"{elapsed_time:.2f}s"
        time_color = "red"

    console.print(
        f"[bold green]✓ Done Stage:[/bold green] [bold white]{stage_name}[/bold white] "
        f"[dim]│[/dim] [{time_color}]{time_str}[/{time_color}]"
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


def reset_stage_timings() -> None:
    """Reset the stage timings tracker.

    This should be called at the start of a pipeline run.
    """
    global _stage_timings  # noqa: PLW0603
    _stage_timings = []
