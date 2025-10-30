"""RESDSQL model integration for SQL generation."""

from typing import Any

from src.pipe.processor.list_transformer import JsonListTransformer
from src.utils.json_io import read_json


class AddResd(JsonListTransformer):
    """
    Add RESDSQL predictions to data rows.

    Parameters
    ----------
    resd_path : str
        Path to RESDSQL predictions JSON file
    """

    def __init__(self, resd_path: str) -> None:
        super().__init__()
        self.resd: Any = read_json(resd_path)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        for r in self.resd:
            if r["question_id"] == row["question_id"]:
                row["tc_original"] = r["tc_original"]
                return row
        raise RuntimeError(f"Row with qid = {row['question_id']} not found")
