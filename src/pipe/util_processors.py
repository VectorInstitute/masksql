"""Utility processors for MaskSQL pipeline."""

from src.models.masksql_input import MaskSqlInput
from src.pipe.processor.list_processor import JsonListProcessor


class InitData(JsonListProcessor[MaskSqlInput, "InitData.Model"]):
    """Initialize data for processing in the MaskSQL pipeline.

    Prepares input data by adding tracking fields for metrics collection.
    """

    class Model(MaskSqlInput):
        """Data model for initialized processing data.

        Extends the base input model with fields for tracking
        processing metrics like latency and token usage.
        """

        total_latency: float = 0.0
        total_toks: float = 0.0

    def __init__(self) -> None:
        super().__init__(self.Model, force=True)

    async def _process_row(self, row: MaskSqlInput) -> Model:
        return self.Model(total_toks=0, total_latency=0, **row.dict())
