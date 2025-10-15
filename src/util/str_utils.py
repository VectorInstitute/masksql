"""String manipulation utilities."""

import re
from difflib import SequenceMatcher
from enum import Enum
from typing import Optional


def delete_whitespace(content):
    """
    Remove all newline and carriage return characters from a string.

    Parameters
    ----------
    content : str
        The string to process.

    Returns
    -------
    str
        The string with all newlines and carriage returns removed.
    """
    return content.replace("\n", "").replace("\r", "")


def is_quoted(s) -> bool:
    """
    Check if a string is wrapped in quotes.

    Parameters
    ----------
    s : str
        The string to check.

    Returns
    -------
    bool
        True if the string is wrapped in single or double quotes.
    """
    return (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    )


def quote_str(s) -> str:
    """
    Wrap a string in single quotes if not already quoted.

    Parameters
    ----------
    s : str
        The string to quote.

    Returns
    -------
    str
        The quoted string.
    """
    if is_quoted(s):
        return s
    return f"'{s}'"


def shrink_whitespaces(s: Optional[str]) -> Optional[str]:
    """
    Normalize whitespace in a string.

    Strips leading/trailing whitespace, replaces newlines and carriage returns
    with spaces, and collapses multiple consecutive whitespaces into single spaces.

    Parameters
    ----------
    s : Optional[str]
        The string to process, or None.

    Returns
    -------
    Optional[str]
        The normalized string, or None if input was None.
    """
    if s is None:
        return s
    s = s.strip()
    s = s.replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", s)


def pascal_to_snake(name: str) -> str:
    """
    Convert PascalCase string to snake_case.

    Parameters
    ----------
    name : str
        The PascalCase string to convert.

    Returns
    -------
    str
        The snake_case version of the string.

    Examples
    --------
    >>> pascal_to_snake("BarBaz")
    'bar_baz'
    """
    snake_case = re.sub("([A-Z])", r"_\1", name).lower()
    return snake_case.lstrip("_")


def split_pascal(name: str) -> str:
    """
    Split PascalCase string into space-separated words.

    Parameters
    ----------
    name : str
        The PascalCase string to split.

    Returns
    -------
    str
        The space-separated version of the string.

    Examples
    --------
    >>> split_pascal("BarBaz")
    'Bar Baz'
    """
    return " ".join(re.findall(r"[A-Z][a-z]*|[a-z]+|[A-Z]+(?=[A-Z]|$)", name))


def split_to_snake(space_separated_str: str) -> str:
    """
    Convert space-separated string to snake_case.

    Parameters
    ----------
    space_separated_str : str
        The space-separated string to convert.

    Returns
    -------
    str
        The snake_case version of the string.

    Examples
    --------
    >>> split_to_snake("Bar Baz")
    'bar_baz'
    """
    return "_".join(space_separated_str.lower().split())


class Color(Enum):
    """ANSI color codes for terminal output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[0m"


def colored(s: str, color: Color):
    """
    Apply color formatting to a string.

    Parameters
    ----------
    s : str
        The string to colorize.
    color : Color
        The color to apply.

    Returns
    -------
    str
        The colored string with ANSI color codes.
    """
    return f"{color.value}{s}{Color.ENDC.value}"


def get_colored_diff(a: str, b: str) -> str:
    """
    Generate a colored diff between two strings.

    Parameters
    ----------
    a : str
        The first string to compare.
    b : str
        The second string to compare.

    Returns
    -------
    str
        A string with color-coded differences.
    """
    a = a.lower()
    b = b.lower()
    matcher = SequenceMatcher(a=a, b=b, isjunk=lambda c: c in " \t")
    result = ""
    for op_code in matcher.get_opcodes():
        (tag, i1, i2, j1, j2) = op_code
        if tag == "equal":
            result += a[i1:i2]
        if tag == "insert":
            result += colored(b[j1:j2], Color.GREEN)
        if tag == "delete":
            result += colored(a[i1:i2], Color.RED)
        if tag == "replace":
            result += colored(b[j1:j2], Color.BLUE)
    return result
