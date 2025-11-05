"""SQL query repair and error correction."""

from typing import Any

from src.utils.logging import logger

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.gen_sql import extract_sql
from src.pipe.sql_repair_prompts.v3 import REPAIR_SQL_PROMPT_V3


class RepairSQL(PromptProcessor):
    """Repair SQL queries based on execution errors."""

    def _process_output(self, row: dict[str, Any], output: str) -> str:
        sql = extract_sql(output)
        if sql == "SELECT":
            logger.error(f"Failed to extract sql from: {output}")
            return row["concrete_sql"]
        return sql

    def _get_prompt(self, row: dict[str, Any]) -> str:
        question = row["question"]
        schema = row["schema"]
        sql = row["concrete_sql"]
        err = row["pre_eval"]["err"]
        pred_res = row["pre_eval"]["pred_res"]
        exec_res = f"Execution Result: {pred_res}, Execution Error: {err}"
        return REPAIR_SQL_PROMPT_V3.format(
            question=question, schema=schema, sql=sql, exec_res=exec_res
        )

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if row["pre_eval"]["acc"] == 1:
            row["pred_sql"] = row["concrete_sql"]
            return row
        return await super()._process_row(row)
