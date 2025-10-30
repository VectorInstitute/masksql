"""Generate SQL queries with masked values."""

from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.gen_sql import extract_sql
from src.pipe.sql_gen_prompts.masked_v4 import MASKED_GEN_SQL_PROMPT_V4


DATA_DIR = "data"


class GenerateSymbolicSql(PromptProcessor):
    """Generate SQL queries from symbolic questions and schemas."""

    def _process_output(self, row: dict[str, Any], output: str) -> dict[str, str]:
        masked_sql = extract_sql(output)
        return {"sql": masked_sql}

    def _get_prompt(self, row: dict[str, Any]) -> str:
        symbolic_question = row["symbolic"]["question"]
        symbolic_schema = row["symbolic"]["schema"]
        return MASKED_GEN_SQL_PROMPT_V4.format(
            question=symbolic_question, schema=symbolic_schema
        )
