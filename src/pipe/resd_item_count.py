"""RESDSQL item counting utilities."""

from typing import Any

# from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.processor.list_transformer import JsonListTransformer


class ResdItemCount(JsonListTransformer):
    """Count schema items from RESDSQL predictions."""

    def __init__(self) -> None:
        super().__init__()
        self.total_tables = 0

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        count = 0
        for items in row["schema_items"]:
            if items.startswith("TABLE"):
                count += 1
        self.total_tables += count
        return row

    def _post_run(self) -> None:
        print(f"After processing all rows total tables = {self.total_tables}")
