"""Entity detection in natural language questions."""

from typing import List

from src.config import OpenAIConfig
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor, T
from src.pipe.detect_values_prompts.v3 import DETECT_VALUES_PROMPT_V3
from src.pipe.llm_util import extract_object
from src.pipe.symb_table import AddSymbolTable


class DetectValues(PromptProcessor[AddSymbolTable.Model, "DetectValues.Model"]):
    """
    Detect and extract values from natural language questions.

    Uses an LLM to identify specific values (numbers, strings, dates) in questions
    that should be linked to database columns.
    """

    class Model(AddSymbolTable.Model):
        """Data model for value detection results with a list of detected values."""

        values: List[str] = []

    def _get_result_data(
        self, row: AddSymbolTable.Model, llm_output: List[str]
    ) -> Model:
        return self.Model(values=llm_output, **row.dict())

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _process_output(self, row: T, output: str) -> List[str]:
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
