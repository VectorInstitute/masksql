"""Generate SQL queries with masked values."""

from typing import Any

from src.config import OpenAIConfig
from src.pipe.det_mask import AddSymbolicQuestion, SymbolicQuestion
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.gen_sql import extract_sql
from src.pipe.sql_gen_prompts.masked_v4 import MASKED_GEN_SQL_PROMPT_V4


DATA_DIR = "data"


class SymbolicSql(SymbolicQuestion):
    """
    Data model for symbolic SQL queries.

    Extends SymbolicQuestion with an SQL query field to store
    the generated symbolic SQL query.
    """

    sql: str


class GenerateSymbolicSql(
    PromptProcessor[AddSymbolicQuestion.Model, "GenerateSymbolicSql.Model"]
):
    """Generate SQL queries from symbolic questions and schemas."""

    class Model(AddSymbolicQuestion.Model):
        """Data model for symbolic SQL generation with symbolic SQL field."""

        symbolic: SymbolicSql

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(
        self, row: "AddSymbolicQuestion.Model", llm_output: Any
    ) -> Model:
        symbolic = SymbolicSql(sql=llm_output, **row.symbolic.dict())
        return self.Model(**row.dict(exclude={"symbolic"}), symbolic=symbolic)

    def _process_output(self, row: "AddSymbolicQuestion.Model", output: str) -> str:
        return extract_sql(output)

    def _get_prompt(self, row: "AddSymbolicQuestion.Model") -> str:
        symbolic_question = row.symbolic.question
        symbolic_schema = row.symbolic.db_schema
        return MASKED_GEN_SQL_PROMPT_V4.format(
            question=symbolic_question, schema=symbolic_schema
        )
