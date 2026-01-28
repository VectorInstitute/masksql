"""List length limiting base_processor."""

import os

from src.data_models.masksql_input import MaskSqlInput
from src.pipeline.base_processor.list_processor import JsonListProcessor


START = int(os.environ.get("START", "0"))
LIMIT = int(os.environ.get("LIMIT", "10"))


class Bar:
    """Placeholder class for demonstration or testing purposes."""

    pass


class LimitJson(JsonListProcessor[MaskSqlInput, MaskSqlInput]):
    """Limit JSON list to subset based on START and LIMIT environment variables."""

    def __init__(self) -> None:
        super().__init__(MaskSqlInput, force=True)

    async def _process_row(self, row: MaskSqlInput) -> MaskSqlInput:
        return row

    async def run(self, input_data: list[MaskSqlInput]) -> list[MaskSqlInput]:
        """
        Process a subset of the input data based on START and LIMIT.

        Parameters
        ----------
        input_data : list[MaskSqlInput]
            List of input data rows

        Returns
        -------
        list[MaskSqlInput]
            Processed subset of input data
        """
        return await super().run(input_data[START : START + LIMIT])
