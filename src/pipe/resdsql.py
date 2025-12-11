"""RESDSQL model integration for SQL generation."""

from src.models.masksql_input import MaskSqlInput
from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.util_processors import InitData
from src.utils.json_io import read_json_raw


class AddResd(JsonListProcessor[MaskSqlInput, "AddResd.Model"]):
    """
    Add RESDSQL predictions to data rows.

    Parameters
    ----------
    resd_path : str
        Path to RESDSQL predictions JSON file
    """

    class Model(InitData.Model):
        """Data model for RESDSQL integration with original table-column predictions."""

        tc_original: list[str] = []

    def __init__(self, resd_path: str) -> None:
        super().__init__(self.Model, force=True)
        self.resd_path = resd_path
        self.resd : list[dict] = []

    def _pre_run(self) -> None:
        """Load RESDSQL predictions before processing rows."""
        self.resd = read_json_raw(self.resd_path)

    async def _process_row(self, row: MaskSqlInput) -> Model:
        for r in self.resd:
            if r["idx"] == row.idx:
                return self.Model(tc_original=r["tc_original"], **row.dict())
        raise RuntimeError(f"Row with idx = {row.idx} not found")
