"""Monitoring and logging utilities."""

import datetime
import math
import subprocess
from datetime import datetime

import pandas as pd


class TimeLogger:
    """
    Logger for tracking operation timing.

    Parameters
    ----------
    idx : str
        Identifier for the logged operation
    """

    idx: str

    def __init__(self, idx: str):
        self.idx = idx

    @staticmethod
    def start(idx: str):
        """
        Start timing an operation.

        Parameters
        ----------
        idx : str
            Operation identifier

        Returns
        -------
        TimeLogger
            Timer instance
        """
        # logger.info(f"started", idx=f"{idx}", start=True)
        return TimeLogger(idx)

    def lap(self):
        """Record lap time for operation."""
        pass
        # logger.info(f"finished", idx=f"{self.idx}", finish=True)


class Timer:
    """Simple timer for measuring elapsed time."""

    start_time: datetime

    def __init__(self):
        self.start_time = datetime.now()

    @staticmethod
    def start():
        """
        Start a new timer.

        Returns
        -------
        Timer
            New timer instance
        """
        return Timer()

    def lap(self) -> float:
        """
        Get elapsed time since timer start.

        Returns
        -------
        float
            Elapsed time in seconds
        """
        return (datetime.now() - self.start_time).total_seconds()


def confidence_interval(column: pd.Series) -> str:
    """
    Calculate confidence interval for numeric column.

    Parameters
    ----------
    column : pd.Series
        Numeric data series

    Returns
    -------
    str
        Formatted confidence interval string
    """
    if not pd.api.types.is_numeric_dtype(column):
        return "NA"
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interval_start = mean - err_margin
    interval_end = mean + err_margin
    if (
        interval_start >= 0
        and interval_end <= 1
        and interval_start >= 0
        and interval_end <= 1
    ):
        return "({:.2f}%, {:.2f}%)".format(interval_start * 100, interval_end * 100)
    return "({:.2f}, {:.2f})".format(interval_start * 100, interval_end * 100)
    # return f"({interval_start}, {interval_end})"


def execute_command(command: str):
    """
    Execute shell command and capture output.

    Parameters
    ----------
    command : str
        Shell command to execute

    Raises
    ------
    subprocess.CalledProcessError
        If command execution fails
    """
    with subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True
    ) as p:
        output, errors = p.communicate()
        print(output, errors)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
