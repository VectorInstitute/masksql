"""Utility module for time measurement and tracking.

This module provides a simple Timer class for measuring elapsed time in seconds.
"""

from datetime import datetime


class Timer:
    """
    Simple timer for measuring elapsed time.

    Attributes
    ----------
    start_time : datetime
        The time when the timer was created
    """

    start_time: datetime

    def __init__(self) -> None:
        self.start_time = datetime.now()

    @staticmethod
    def start() -> "Timer":
        """
        Create and start a new timer.

        Returns
        -------
        Timer
            A new timer instance
        """
        return Timer()

    def lap(self) -> float:
        """
        Get elapsed time since timer started.

        Returns
        -------
        float
            Elapsed time in seconds
        """
        return (datetime.now() - self.start_time).total_seconds()
