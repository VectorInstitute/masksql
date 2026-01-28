"""Filter value links based on relevance."""

from src.pipeline.base_processor.prompt_processor import PromptProcessor
from src.pipeline.filter_schema_links.filter_schema_links import CONCEPTS
from src.pipeline.filter_value_links.prompts.v1 import VALUE_LINKS_FILTER_PROMPT_V1
from src.pipeline.link_values.link_values import FilterValueLinksModel, LinkValues
from src.utils.llm_util import extract_object


class FilterValueLinks(PromptProcessor[LinkValues.Model, FilterValueLinksModel]):
    """
    Filter value links based on relevance to predefined concepts.

    Uses LLM prompts to determine which value links (mappings from question
    values to database columns) are relevant to specific concepts.
    """

    def _get_result_data(
        self, row: LinkValues.Model, llm_output: dict[str, str]
    ) -> FilterValueLinksModel:
        return FilterValueLinksModel(filtered_value_links=llm_output, **row.dict())

    def _process_output(self, row: LinkValues.Model, output: str) -> dict[str, str]:
        result = extract_object(output)
        if result is None:
            return {}
        return result

    def _get_prompt(self, row: LinkValues.Model) -> str:
        question = row.question
        value_links = row.values
        return VALUE_LINKS_FILTER_PROMPT_V1.format(
            concepts=CONCEPTS, question=question, value_links=value_links
        )
