"""Entity detection in natural language questions."""

from src.config import OpenAIConfig
from src.pipeline.base_processor.prompt_processor import PromptProcessor
from src.pipeline.detect_values.prompts.v3 import DETECT_VALUES_PROMPT_V3
from src.pipeline.symb_table import AddSymbolTable
from src.utils.llm_util import extract_object


class DetectValues(PromptProcessor[AddSymbolTable.Model, "DetectValues.Model"]):
    """
    Detect and extract values from natural language questions.

    Uses an LLM to identify specific values (numbers, strings, dates) in questions
    that should be linked to database columns.
    """

    class Model(AddSymbolTable.Model):
        """Data model for value detection results with a list of detected values."""

        values: list[str] = []

    def _get_result_data(
        self, row: AddSymbolTable.Model, llm_output: list[str]
    ) -> Model:
        return self.Model(values=llm_output, **row.dict())

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _process_output(self, row: AddSymbolTable.Model, output: str) -> list[str]:
        obj = extract_object(output)
        if obj is None:
            return []
        return obj

    def _get_prompt(self, row: AddSymbolTable.Model) -> str:
        schema_items = row.schema_items
        question = row.question
        return DETECT_VALUES_PROMPT_V3.format(
            question=question, schema_items=schema_items
        )
