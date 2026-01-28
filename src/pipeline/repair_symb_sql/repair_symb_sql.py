"""Symbolic SQL query repair and error correction."""

from typing import Any

from src.config import OpenAIConfig
from src.pipeline.base_processor.prompt_processor import PromptProcessor
from src.pipeline.gen_sql.gen_masked_sql import GenerateSymbolicSql, SymbolicSql
from src.pipeline.repair_symb_sql.prompts.v2 import REPAIR_SYMBOLIC_SQL_PROMPT_V2
from src.utils.strings import extract_sql


class RepairedSymbolicSql(SymbolicSql):
    """
    Data model for repaired symbolic SQL queries.

    Extends SymbolicSql with a repaired_sql field to store
    the corrected symbolic SQL query.
    """

    repaired_sql: str


class RepairSymbolicSQL(
    PromptProcessor[GenerateSymbolicSql.Model, "RepairSymbolicSQL.Model"]
):
    """Repair symbolic SQL queries with schema context."""

    class Model(GenerateSymbolicSql.Model):
        """Data model for symbolic SQL repair with repaired symbolic SQL field."""

        symbolic: RepairedSymbolicSql

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(
        self, row: "GenerateSymbolicSql.Model", llm_output: Any
    ) -> Model:
        symbolic = RepairedSymbolicSql(repaired_sql=llm_output, **row.symbolic.dict())
        return self.Model(symbolic=symbolic, **row.dict(exclude={"symbolic"}))

    def _process_output(self, row: "GenerateSymbolicSql.Model", output: str) -> str:
        return extract_sql(output)

    def _get_prompt(self, row: "GenerateSymbolicSql.Model") -> str:
        symbolic_question = row.symbolic.question
        symbolic_schema = row.symbolic.db_schema
        symbolic_sql = row.symbolic.sql
        return REPAIR_SYMBOLIC_SQL_PROMPT_V2.format(
            question=symbolic_question, schema=symbolic_schema, sql=symbolic_sql
        )
