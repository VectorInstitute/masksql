"""JSON-based caching system for storing and retrieving objects.

This module provides a generic cache implementation that stores objects
in a JSON file and provides methods for adding, updating, and retrieving them.
"""

import os
from typing import Dict, Generic, Type, TypeVar

from src.models.base_object import BaseObject
from src.utils.json_io import read_json, write_json


T = TypeVar("T", bound=BaseObject)


class JsonCache(Generic[T]):
    """A generic cache that stores objects in a JSON file.

    This class provides functionality to store, retrieve, and manage objects
    that inherit from BaseObject. Objects are stored in a JSON file and can
    be accessed by their unique identifier.

    Attributes
    ----------
        data: Dictionary mapping object IDs to objects
        path: Path to the JSON file where objects are stored
        cls: Type of objects stored in the cache
    """

    data: Dict[str, T]
    path: str
    cls: Type[T]

    def __init__(self, file_path: str, cls: Type[T]):
        self.path = file_path
        self.cls = cls
        self.data = {}
        self.load()

    def add_or_update(self, obj: T) -> None:
        """Add a new object to the cache or update an existing one.

        Args:
            obj: The object to add or update
        """
        self.data[obj.idx] = obj
        self.save()

    def delete(self, idx: str) -> None:
        """Delete an object from the cache by its ID.

        Args:
            idx: The ID of the object to delete
        """
        del self.data[idx]

    def load(self) -> None:
        """Load objects from the JSON file into the cache.

        If the file exists, reads all objects and adds them to the cache.
        """
        if os.path.exists(self.path):
            data = read_json(self.path, self.cls)
            for d in data:
                self.add_or_update(d)

    def save(self) -> None:
        """Save all objects in the cache to the JSON file."""
        write_json(self.path, list(self.data.values()))

    def __contains__(self, idx: str) -> bool:
        """Check if an object with the given ID exists in the cache.

        Args:
            idx: The ID to check

        Returns
        -------
            True if an object with the given ID exists, False otherwise
        """
        return idx in self.data

    def __getitem__(self, idx: str) -> T:
        """Get an object from the cache by its ID.

        Args:
            idx: The ID of the object to retrieve

        Returns
        -------
            The object with the given ID
        """
        return self.data[idx]
