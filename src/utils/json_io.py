"""JSON file reading and writing utilities."""

import json
from typing import Any


def read_json(path: str) -> Any:
    """
    Read and parse a JSON file.

    Parameters
    ----------
    path : str
        Path to the JSON file.

    Returns
    -------
    dict or list
        The parsed JSON data.
    """
    with open(path) as f:
        return json.load(f)


def write_json(path: str, data: Any) -> None:
    """
    Write data to a JSON file with indentation.

    Parameters
    ----------
    path : str
        Path to the output JSON file.
    data : dict or list
        The data to write as JSON.
    """
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=4))
