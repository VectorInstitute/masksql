"""SQL query repair and error correction."""

from typing import Any

from src.config import OpenAIConfig
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.exec_conc_sql import ExecuteConcreteSql
from src.pipe.gen_sql import extract_sql
from src.pipe.sql_repair_prompts.v3 import REPAIR_SQL_PROMPT_V3
from src.utils.logging import logger


class RepairSQL(PromptProcessor[ExecuteConcreteSql.Model, "RepairSQL.Model"]):
    """Repair SQL queries based on execution errors."""

    class Model(ExecuteConcreteSql.Model):
        """Data model for SQL repair with predicted (corrected) SQL query."""

        pred_sql: str = ""

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(self, row: ExecuteConcreteSql.Model, llm_output: Any) -> Model:
        return self.Model(pred_sql=llm_output, **row.dict())

    def _process_output(self, row: ExecuteConcreteSql.Model, output: str) -> str:
        sql = extract_sql(output)
        if sql == "SELECT":
            logger.error(f"Failed to extract sql from: {output}")
            return row.concrete_sql if hasattr(row, "concrete_sql") else ""
        return sql

    def _get_prompt(self, row: ExecuteConcreteSql.Model) -> str:
        question = row.question
        schema = row.db_schema
        sql = row.concrete_sql
        err = row.pre_eval.err
        pred_res = row.pre_eval.pred_res
        exec_res = f"Execution Result: {pred_res}, Execution Error: {err}"
        return REPAIR_SQL_PROMPT_V3.format(
            question=question, schema=schema, sql=sql, exec_res=exec_res
        )

    async def _process_row(self, row: ExecuteConcreteSql.Model) -> Model:
        if row.pre_eval.acc == 1:
            return self.Model(pred_sql=row.concrete_sql, **row.dict())
        return await super()._process_row(row)
