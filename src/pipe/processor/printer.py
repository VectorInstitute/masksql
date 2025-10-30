"""Data printing utilities."""

from abc import ABC
from collections.abc import Callable
from typing import Any

from src.pipe.processor.list_processor import JsonListProcessor


class DataPrinter(JsonListProcessor, ABC):
    """Base class for processors that print data without modifying files."""

    async def run(self, input_file: str) -> str:
        """
        Process input file and return same path.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        str
            Same input file path
        """
        output_file = input_file
        await super().run(input_file)
        return output_file


class CustomPrinter(DataPrinter):
    """Print questions and their masked versions."""

    async def _process_row(self, row: Any) -> Any:
        print("-" * 10)
        print("Question:", row["question"])
        print("Masked:", row["symbolic"]["question"])
        # print("REP:", row['repaired_schema_links'])
        print("-" * 10)
        return row


class LambdaPrinter(DataPrinter):
    """
    Print data using custom printer function.

    Parameters
    ----------
    printer : callable
        Function to print each row
    """

    def __init__(self, printer: Callable[[Any], None]) -> None:
        super().__init__()
        self.printer = printer

    async def _process_row(self, row: Any) -> Any:
        self.printer(row)
        return row
