"""Value link data structures and utilities."""

from src.config import OpenAIConfig
from src.pipeline.base_processor.prompt_processor import PromptProcessor
from src.pipeline.detect_values.detect_values import DetectValues
from src.pipeline.link_values.prompts.v1 import VALUE_LINKING_PROMPT_V1
from src.utils.llm_util import extract_object


class LinkValues(PromptProcessor[DetectValues.Model, "LinkValues.Model"]):
    """
    Link detected values in questions to database columns.

    Uses an LLM to determine which database columns each detected value
    in the question should be associated with.
    """

    class Model(DetectValues.Model):
        """Data model for value linking.

        Extends the detected values model with mappings between
        question values and database columns.
        """

        value_links: dict[str, str] = {}

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(
        self, row: DetectValues.Model, llm_processed_output: dict[str, str]
    ) -> Model:
        return self.Model(value_links=llm_processed_output, **row.dict())

    def _process_output(self, row: DetectValues.Model, output: str) -> dict[str, str]:
        obj = extract_object(output)
        if obj is None:
            return {}
        return obj

    def _get_prompt(self, row: DetectValues.Model) -> str:
        schema_items = row.schema_items
        question = row.question
        values = row.values
        columns = [x.split(":")[1] for x in schema_items]
        return VALUE_LINKING_PROMPT_V1.format(
            question=question, values=values, columns=columns
        )


class FilterValueLinksModel(LinkValues.Model):
    """Data model for filtered value links.

    Extends the value links model with a filtered subset of value links
    that are relevant for the current query.
    """

    filtered_value_links: dict[str, str] = {}
