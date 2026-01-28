"""Results printing base_processor."""


def print_color(text: str, color: str = "green") -> None:
    """
    Print text with ANSI color codes.

    Parameters
    ----------
    text : str
        Text to print
    color : str, optional
        Color name (red, green, blue), default green
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "blue": "\033[94m",
    }
    reset = "\033[0m"
    color_code = colors.get(color.lower(), "")
    print(f"{color_code}{text}{reset}")
