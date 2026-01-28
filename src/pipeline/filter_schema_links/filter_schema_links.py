"""Filter schema links based on relevance."""

from src.pipeline.base_processor.prompt_processor import PromptProcessor
from src.pipeline.filter_schema_links.prompts.v2 import FILTER_SCHEMA_LINKS_PROMPT_V2
from src.pipeline.link_schema.link_schema import FilterSchemaLinksModel, LinkSchema
from src.utils.llm_util import extract_object


CONCEPTS = ["Person's name", "Location", "Occupation"]


class FilterSchemaLinks(PromptProcessor[LinkSchema.Model, FilterSchemaLinksModel]):
    """
    Filter schema links based on relevance to predefined concepts.

    Uses LLM prompts to determine which schema links (mappings from question
    terms to schema items) are relevant to specific concepts.
    """

    def _get_result_data(
        self, row: LinkSchema.Model, llm_output: dict[str, str]
    ) -> FilterSchemaLinksModel:
        return FilterSchemaLinksModel(filtered_schema_links=llm_output, **row.dict())

    def _process_output(self, row: LinkSchema.Model, output: str) -> dict[str, str]:
        obj = extract_object(output)
        if obj is None:
            return {}
        return obj

    def _get_prompt(self, row: LinkSchema.Model) -> str:
        schema_links = row.schema_links
        question = row.question
        return FILTER_SCHEMA_LINKS_PROMPT_V2.format(
            concepts=CONCEPTS, question=question, schema_links=schema_links
        )
