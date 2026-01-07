"""Base list processing utilities."""

import os.path
from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from loguru import logger

from src.data_cache.json_cache import JsonCache
from src.data_models.base_object import BaseObject
from src.utils.async_utils import apply_async
from src.utils.logging import along


T = TypeVar("T", bound=BaseObject)
U = TypeVar("U", bound=BaseObject)


class JsonListProcessor(ABC, Generic[T, U]):
    """Base class for JSON list processing operations."""

    cls: Type[U]
    force: bool
    cache: JsonCache[U] | None = None

    def __init__(self, cls: Type[U], force: bool = False) -> None:
        self.cls = cls
        self.force = force

    def set_cache_file(self, cache_dir: str, sequence: int) -> None:
        """
        Set up the cache file for storing processed results.

        Parameters
        ----------
        cache_dir : str
            Directory to store cache files
        sequence : int
            Sequence number for the cache file
        """
        self.cache = JsonCache[U](
            self.get_cache_file_path(cache_dir, sequence), self.cls
        )

    def get_cache_file_path(self, cache_dir: str, sequence: int) -> str:
        """
        Generate the path for the cache file.

        Parameters
        ----------
        cache_dir : str
            Directory to store cache files
        sequence : int
            Sequence number for the cache file

        Returns
        -------
        str
            Full path to the cache file
        """
        return os.path.join(cache_dir, f"{sequence}_{self.name}.json")

    @logger.catch(message="Failed to process row", reraise=True)
    async def __process_row_internal(self, row: T) -> U:
        if self.cache and not self.force and row.idx in self.cache:
            return self.cache[row.idx]

        processed_row = await self._process_row(row)

        if self.cache:
            self.cache.add_or_update(processed_row)
        return processed_row

    @abstractmethod
    async def _process_row(self, row: T) -> U:
        pass

    @property
    def name(self) -> str:
        """
        Get base_processor name.

        Returns
        -------
        str
            Class name of base_processor
        """
        return self.__class__.__name__

    def _pre_run(self) -> None:  # noqa: B027
        """Override to add pre-processing logic before run."""

    def _post_run(self) -> None:  # noqa: B027
        """Override to add post-processing logic after run."""

    @along("Processor completed: {0}")
    async def run(self, input_data: list[T]) -> list[U]:
        """
        Process input file and return output_data.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        list | str
            Processed data rows or output_data file path
        """
        data = [item.model_copy() for item in input_data]
        self._pre_run()

        output_data = await apply_async(self.__process_row_internal, data, self.name)

        self._post_run()

        return output_data

    def __repr__(self) -> str:
        """Name of the processor."""
        return self.name
