"""Pipeline execution and management."""

from typing import Any

from src.pipe.monitor.lib import Timer
from src.pipe.monitor.mem import track_memory_async
from src.pipe.processor.list_processor import JsonListProcessor
from src.utils.logging import (
    log_pipeline_summary,
    log_stage_complete,
    log_stage_start,
    reset_stage_timings,
)


class Pipeline:
    """
    Pipeline for sequential execution of processing stages.

    Parameters
    ----------
    stages : list[JsonListProcessor]
        List of processing stages to execute in order
    """

    def __init__(self, stages: list[JsonListProcessor]) -> None:
        self.stages = stages

    async def __run_internal(self, input_file: str) -> Any:
        tmp_file: Any = input_file
        timer: Timer = Timer()
        timer.start()
        last_lap_time = 0.0

        for stage in self.stages:
            log_stage_start(stage.name)
            tmp_file = await stage.run(tmp_file)

            # Get cumulative time and calculate stage time
            cumulative_time = timer.lap()
            stage_time = cumulative_time - last_lap_time
            last_lap_time = cumulative_time

            log_stage_complete(stage.name, stage_time)
        return tmp_file

    async def run(self, input_file: str) -> tuple[Any, float, float]:
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
            self.__run_internal, input_file
        )
        total_time = timer.lap()

        # Extract results if available
        results_dict = None
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            # Check if there's a summary in the result
            pass  # Results will be handled by the Results stage itself

        # Log comprehensive summary
        log_pipeline_summary(total_time, avg_mem, peak_mem, results_dict)

        return result, avg_mem, peak_mem
