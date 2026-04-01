"""Pipeline execution and management."""

import os
from typing import Any, Generic, TypeVar

from src.data_models.base_object import BaseObject
from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.utils.logging import (
    log_pipeline_summary,
)
from src.utils.mem import track_memory_async
from src.utils.timer import Timer


T = TypeVar("T", bound=BaseObject)


class Pipeline(Generic[T]):
    """
    Pipeline for sequential execution of processing stages.

    Parameters
    ----------
    stages : list[JsonListProcessor]
        List of processing stages to execute in order
    """

    def __init__(
        self, name: str, cache_dir: str, stages: list[JsonListProcessor]
    ) -> None:
        self.name = name
        self.stages = stages
        for i, stage in enumerate(self.stages):
            pipeline_cache_dir = os.path.join(cache_dir, name)
            if not os.path.exists(pipeline_cache_dir):
                os.makedirs(pipeline_cache_dir, exist_ok=True)
            stage.set_cache_file(pipeline_cache_dir, i + 1)

    async def __run_internal(self, input_data: list[T]) -> list[Any]:
        tmp_data = input_data
        for stage in self.stages:
            tmp_data = await stage.run(tmp_data)
        return tmp_data

    async def run(self, input_data: list[T]) -> list[Any]:
        """
        Execute pipeline on input file.

        Parameters
        ----------
        input_file : str
            Path to input data file

        Returns
        -------
        tuple[Any, float, float]
            Tuple of (result, average_memory_mb, peak_memory_mb)
        """
        timer: Timer = Timer.start()
        result, avg_mem, peak_mem = await track_memory_async(
            self.__run_internal, input_data
        )
        total_time = timer.lap()

        # Extract results if available
        results_dict = None
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            # Check if there's a summary in the result
            pass  # Results will be handled by the Results stage itself

        # Log comprehensive summary
        log_pipeline_summary(total_time, avg_mem, peak_mem, results_dict)

        return result
