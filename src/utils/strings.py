"""String manipulation utilities."""

import re
from difflib import SequenceMatcher
from enum import Enum

from src.utils.logging import logger


def delete_whitespace(content: str) -> str:
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


def is_quoted(s: str) -> bool:
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


def quote_str(s: str) -> str:
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


def shrink_whitespaces(s: str | None) -> str | None:
    """
    Normalize whitespace in a string.

    Strips leading/trailing whitespace, replaces newlines and carriage returns
    with spaces, and collapses multiple consecutive whitespaces into single spaces.

    Parameters
    ----------
    s : str | None
        The string to process, or None.

    Returns
    -------
    str | None
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


def colored(s: str, color: Color) -> str:
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


def extract_sql(output: str) -> str:
    """
    Extract SQL query from LLM output.

    Parameters
    ----------
    output : str
        Raw LLM output containing SQL

    Returns
    -------
    str
        Extracted SQL query
    """
    output = output.strip()
    output = output.strip('"')
    sql = "SELECT"
    if output.startswith("SELECT"):
        sql = output
    elif "```sql" in output:
        res = re.findall(r"```sql([\s\S]*?)```", output)
        if res:
            sql = res[0]
        else:
            logger.error(
                f"Failed to extract sql from output with ```sql marker: {output}"
            )
    elif "```" in output:
        res = re.findall(r"```([\s\S]*?)```", output)
        if res:
            sql = res[0]
        else:
            logger.error(f"Failed to extract sql from output with ``` marker: {output}")
    elif "`" in output:
        res = re.findall(r"`([\s\S]*?)`", output)
        if res:
            sql = res[0]
        else:
            logger.error(f"Failed to extract sql from output with ` marker: {output}")
    else:
        logger.error(f"Failed to extract sql from output: {output}")
    sql = sql.strip()
    return sql.replace("\n", " ")
