"""General utility functions for pipeline processing."""

import re
from datetime import datetime

from loguru import logger


def replace_str(text: str, src: str, dst: str) -> str:
    """
    Replace a substring in text with word boundaries.

    Parameters
    ----------
    text : str
        The text to search in
    src : str
        The substring to replace
    dst : str
        The replacement substring

    Returns
    -------
    str
        Text with replacements made
    """
    try:
        result = re.sub(
            r"\b{}\b".format(re.escape(src)), dst, text, flags=re.IGNORECASE
        )
    except Exception:
        logger.error(f"Failed to replace {src} -> {dst} in {text}")
        result = text
    return result


def check_str(text: str, src: str) -> bool:
    """
    Check if a substring exists in text with word boundaries.

    Parameters
    ----------
    text : str
        The text to search in
    src : str
        The substring to search for

    Returns
    -------
    bool
        True if substring found with word boundaries, False otherwise
    """
    try:
        pattern = r"\b{}\b".format(re.escape(src))
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    except Exception:
        logger.error(f"Failed to search {src} in {text}")
    return False


def replace_str_punc(text: str, src: str, dst: str) -> str:
    """
    Replace a substring in text with punctuation-aware boundaries.

    Parameters
    ----------
    text : str
        The text to search in
    src : str
        The substring to replace
    dst : str
        The replacement substring

    Returns
    -------
    str
        Text with replacements made
    """
    try:
        result = re.sub(
            r"(?<![\w.]){}(?!\w)".format(re.escape(src)), dst, text, flags=re.IGNORECASE
        )
    except Exception:
        logger.error(f"Failed to replace {src} -> {dst} in {text}")
        result = text
    return result


def check_str_punc(text: str, src: str) -> bool:
    """
    Check if a substring exists in text with punctuation-aware boundaries.

    Parameters
    ----------
    text : str
        The text to search in
    src : str
        The substring to search for

    Returns
    -------
    bool
        True if substring found with punctuation boundaries, False otherwise
    """
    try:
        pattern = r"(?<![\w.]){}(?!\w)".format(re.escape(src))
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    except Exception:
        logger.error(f"Failed to search {src} in {text}")
    return False


class Timer:
    """
    Simple timer for measuring elapsed time.

    Attributes
    ----------
    start_time : datetime
        The time when the timer was created
    """

    start_time: datetime

    def __init__(self):
        self.start_time = datetime.now()

    @staticmethod
    def start():
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
