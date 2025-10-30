"""SQL generation evaluation processor."""

from typing import Any

from src.pipe.processor.list_processor import JsonListProcessor


class GenSqlEval(JsonListProcessor):
    """Evaluate SQL generation accuracy and masking coverage."""

    def __init__(self) -> None:
        super().__init__()
        self.total = 0
        self.score = 0
        self.masked = 0

    def _post_run(self) -> None:
        print(f"Score: {self.score}/{self.total}")
        print(f"Masked: {self.masked}/{self.total}")

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        self.total += 1
        self.score += row["pre_eval"]["acc"]
        self.masked += row["symbolic"]["masked"]
        return row
