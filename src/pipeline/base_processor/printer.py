"""Data printing utilities."""

from abc import ABC
from collections.abc import Callable

from src.data_models.masksql_input import MaskSqlInput
from src.pipeline.base_processor.list_processor import JsonListProcessor


class LambdaPrinter(JsonListProcessor[MaskSqlInput, MaskSqlInput], ABC):
    """
    Print data using custom printer function.

    Parameters
    ----------
    printer : callable
        Function to print each row
    """

    def __init__(self, printer: Callable[[MaskSqlInput], None]) -> None:
        super().__init__(MaskSqlInput)
        self.printer = printer

    async def _process_row(self, row: MaskSqlInput) -> MaskSqlInput:
        self.printer(row)
        return row
