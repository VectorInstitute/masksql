"""JSON file reading and writing utilities."""

import json
from typing import Any, Type, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


def read_json_raw(path: str) -> Any:
    """Read and parse a JSON file without model validation.

    Parameters
    ----------
    path : str
        Path to the JSON file.

    Returns
    -------
    Any
        The parsed JSON data as Python objects.
    """
    with open(path) as f:
        return json.load(f)


@logger.catch(
    message="Failed to validate data", reraise=True, exception=ValidationError
)
def read_json(path: str, cls: Type[T]) -> list[T]:
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
    data = read_json_raw(path)
    if cls is not None:
        return [cls.model_validate(item) for item in data]
    return data


def write_json_raw(path: str, data: list[dict]) -> None:
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
        f.write(json.dumps(data, indent=4) + "\n")


def write_json(path: str, data: list[T]) -> None:
    """
    Write data to a JSON file with indentation.

    Parameters
    ----------
    path : str
        Path to the output JSON file.
    data : dict or list
        The data to write as JSON.
    """
    out_data = [item.model_dump() for item in data]
    with open(path, "w") as f:
        f.write(json.dumps(out_data, indent=4) + "\n")
