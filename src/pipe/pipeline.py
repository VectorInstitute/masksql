"""Pipeline execution and management."""

from typing import Any

from src.pipe.monitor.lib import Timer
from src.pipe.monitor.mem import track_memory_async
from src.pipe.processor.list_processor import JsonListProcessor


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
        for stage in self.stages:
            print(f"Starting Stage: {stage.name}")
            tmp_file = await stage.run(tmp_file)
            print(f"Done Stage: {stage.name}, time={timer.lap()}")
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
        timer: Timer = Timer.start()
        result, avg_mem, peak_mem = await track_memory_async(
            self.__run_internal, input_file
        )
        timer.lap()
        # logger.info(f"TOTAL PRED TIME: {total_time}")
        # logger.info(f"AVG MEM: {avg_mem}")
        # logger.info(f"PEAK MEM: {peak_mem}")
        return result, avg_mem, peak_mem
