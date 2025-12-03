"""Pipeline execution and management."""

import os
from typing import Any, Generic, TypeVar

from src.models.base_object import BaseObject
from src.pipe.monitor.lib import Timer
from src.pipe.monitor.mem import track_memory_async
from src.pipe.processor.list_processor import JsonListProcessor
from src.utils.logging import (
    log_pipeline_summary,
    log_stage_complete,
    log_stage_start,
    reset_stage_timings,
)


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
        # tmp_file: Any = input_file
        tmp_data = input_data
        timer: Timer = Timer()
        timer.start()
        last_lap_time = 0.0

        for stage in self.stages:
            log_stage_start(stage.name)
            tmp_data = await stage.run(tmp_data)

            # Get cumulative time and calculate stage time
            cumulative_time = timer.lap()
            stage_time = cumulative_time - last_lap_time
            last_lap_time = cumulative_time

            log_stage_complete(stage.name, stage_time)
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
        # Reset timing tracker for new pipeline run
        reset_stage_timings()

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
