"""Filter schema items based on relevance."""

from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.filer_schema_links import CONCEPTS
from src.pipe.llm_util import extract_object
from src.pipe.schema_items_filter_prompts.v1 import FILTER_SCHEMA_ITEMS_PROMPT_V1


class FilterSchemaItems(PromptProcessor):
    """
    Filter schema items based on relevance to predefined concepts.

    Uses LLM prompts to determine which schema items are relevant to
    specific concepts like person names, locations, and occupations.
    """

    def _process_output(self, row: dict[str, Any], output: str) -> Any:
        return extract_object(output)

    def _get_prompt(self, row: dict[str, Any]) -> str:
        schema_items = row["schema_items"]
        return FILTER_SCHEMA_ITEMS_PROMPT_V1.format(
            concepts=CONCEPTS, schema_items=schema_items
        )
