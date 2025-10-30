"""SQL query result analysis utilities."""

from typing import Any

from src.pipe.processor.list_processor import JsonListProcessor
from src.taxonomy.cat.catter import Catter


class AnalyzeResults(JsonListProcessor):
    """Analyze and categorize SQL query results."""

    def __init__(self) -> None:
        super().__init__()
        self.catter = Catter()

    def _post_run(self) -> None:
        print("done")

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        sql = row["query"]
        cat = self.catter.get_category(sql)
        sub = self.catter.get_sub_category(sql)
        print(f"{cat}:{sub}")
        # print(f"GOLD: {sql}")
        return row
