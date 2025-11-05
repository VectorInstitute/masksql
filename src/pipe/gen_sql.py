"""SQL query generation from natural language."""

import re
from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.sql_gen_prompts.masked_v3 import MASKED_GEN_SQL_PROMPT_V3
from src.utils.logging import logger


DATA_DIR = "data"


def extract_sql(output: str) -> str:
    """
    Extract SQL query from LLM output.

    Parameters
    ----------
    output : str
        Raw LLM output containing SQL

    Returns
    -------
    str
        Extracted SQL query
    """
    output = output.strip()
    output = output.strip('"')
    sql = "SELECT"
    if output.startswith("SELECT"):
        sql = output
    elif "```sql" in output:
        res = re.findall(r"```sql([\s\S]*?)```", output)
        if res:
            sql = res[0]
        else:
            logger.error(
                f"Failed to extract sql from output with ```sql marker: {output}"
            )
    elif "```" in output:
        res = re.findall(r"```([\s\S]*?)```", output)
        if res:
            sql = res[0]
        else:
            logger.error(f"Failed to extract sql from output with ``` marker: {output}")
    elif "`" in output:
        res = re.findall(r"`([\s\S]*?)`", output)
        if res:
            sql = res[0]
        else:
            logger.error(f"Failed to extract sql from output with ` marker: {output}")
    else:
        logger.error(f"Failed to extract sql from output: {output}")
    sql = sql.strip()
    return sql.replace("\n", " ")


class GenSql(PromptProcessor):
    """Generate SQL queries from natural language questions."""

    def _process_output(self, row: dict[str, Any], output: str) -> str:
        return extract_sql(output)

    def _get_prompt(self, row: dict[str, Any]) -> str:
        question = row["question"]
        # schema_items = row['schema_items']
        # return GEN_SQL_PROMPT_V1.format(question=question, schema_items=schema_items)
        schema = row["schema"]
        return MASKED_GEN_SQL_PROMPT_V3.format(question=question, schema=schema)
