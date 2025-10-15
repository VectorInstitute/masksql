"""Filter schema links based on relevance."""

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.schema_filter_prompts.v2 import FILTER_SCHEMA_LINKS_PROMPT_V2


CONCEPTS = ["Person's name", "Location", "Occupation"]


class FilterSchemaLinks(PromptProcessor):
    """
    Filter schema links based on relevance to predefined concepts.

    Uses LLM prompts to determine which schema links (mappings from question
    terms to schema items) are relevant to specific concepts.
    """

    def _process_output(self, row, output):
        obj = extract_object(output)
        if obj is None:
            return {}
        return obj

    def _get_prompt(self, row):
        schema_links = row["schema_links"]
        question = row["question"]
        return FILTER_SCHEMA_LINKS_PROMPT_V2.format(
            concepts=CONCEPTS, question=question, schema_links=schema_links
        )
