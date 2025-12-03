"""Schema linking from questions to database schemas."""

from src.config import OpenAIConfig
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.schema_link_prompts.v4 import SCHEMA_LINK_PROMPT_V4
from src.pipe.value_links import FilterValueLinksModel
from src.utils.logging import logger


class LinkSchema(PromptProcessor[FilterValueLinksModel, "LinkSchema.Model"]):
    """Link natural language question terms to database schema items."""

    class Model(FilterValueLinksModel):
        """Data model for schema linking.

        Maps question terms to schema items, connecting natural language
        to database schema elements.
        """

        schema_links: dict[str, str] = {}

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(
        self, row: FilterValueLinksModel, llm_output: dict[str, str]
    ) -> Model:
        return self.Model(schema_links=llm_output, **row.dict())

    def _process_output(
        self, row: FilterValueLinksModel, output: str
    ) -> dict[str, str]:
        schema_links = extract_object(output)
        if schema_links is None:
            schema_links = {}
        question = row.question
        schema_items = row.schema_items
        refined_links = {}
        if isinstance(schema_links, (list, set, str, tuple)):
            logger.error(f"Invalid schema links: {schema_links}")
            schema_links = {}

        for question_term, schema_item in schema_links.items():
            if question_term.lower() not in question.lower():
                logger.error(
                    f"Invalid schema link {question_term} -> {schema_item}, term not found in question"
                )
                continue
            if schema_item.lower() not in [i.lower() for i in schema_items]:
                logger.error(
                    f"Invalid schema link {question_term} -> {schema_item}, schema item not exists"
                )
                continue
            refined_links[question_term] = schema_item
        return refined_links

    def _get_prompt(self, row: FilterValueLinksModel) -> str:
        question = row.question
        schema_items = row.schema_items
        value_list = row.values
        return SCHEMA_LINK_PROMPT_V4.format(
            schema_items=schema_items, question=question, value_List=value_list
        )


class FilterSchemaLinksModel(LinkSchema.Model):
    """
    Data model for filtered schema links.

    Extends LinkSchema.Model with a filtered subset of schema links
    that are relevant for the current query.
    """

    filtered_schema_links: dict[str, str] = {}
