"""Entity detection in natural language questions."""

from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.detect_values_prompts.v3 import DETECT_VALUES_PROMPT_V3
from src.pipe.llm_util import extract_object
from src.pipe.processor.list_transformer import JsonListTransformer


class DetectValues(PromptProcessor):
    """
    Detect and extract values from natural language questions.

    Uses an LLM to identify specific values (numbers, strings, dates) in questions
    that should be linked to database columns.
    """

    def _process_output(self, row: dict[str, Any], output: str) -> list[Any]:
        obj = extract_object(output)
        if obj is None:
            return []
        return obj

    def _get_prompt(self, row: dict[str, Any]) -> str:
        schema_items = row["schema_items"]
        question = row["question"]
        # slm_sql= row['slm_sql']
        return DETECT_VALUES_PROMPT_V3.format(
            question=question, schema_items=schema_items
        )


class DetectValuesDummy(JsonListTransformer):
    """
    Dummy value detector that returns empty values list.

    Used as a placeholder when value detection is disabled or not needed.
    """

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        row["values"] = []
        return row
