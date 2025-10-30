"""SQL query estimation and scoring."""

import re
from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor


PROMPT = """
I give you a natural language question and a database schema.
Give me the SQL that can answer the given question.

Example:
NL Question: "What is the name of the instructor who has the lowest salary?"
DB Schema:
tables:
    instructor:
       - id: text
       - name: text
       - dept_name: text
       - salary: number
   department:
       - dept_name: text
       - building: text
       - budget: number

SQL: "SELECT name FROM instructor ORDER BY salary LIMIT 1"

Now generate the SQL for the following data:
NL Question: {question}
DB Schema: {schema}
"""

N = 3


class EstimateSQL(PromptProcessor):
    """
    Estimate SQL queries from natural language questions.

    Uses an LLM to generate SQL queries based on natural language questions
    and database schemas.
    """

    def _process_output(self, row: dict[str, Any], output: str) -> str:
        """
        Extract SQL query from LLM output.

        Parameters
        ----------
        row : dict
            Data row (unused in this implementation)
        output : str
            Raw LLM output containing SQL in markdown code blocks

        Returns
        -------
        str
            Cleaned SQL query
        """
        masked = re.findall(r"```([\s\S]*?)```", output)
        final_answer = masked[0]
        final_answer = final_answer.strip()
        final_answer = final_answer.replace("\n", " ")
        if final_answer.startswith("sql"):
            final_answer = final_answer[3:]
        return final_answer

    def _get_prompt(self, row: dict[str, Any]) -> str:
        """
        Generate prompt for SQL estimation.

        Parameters
        ----------
        row : dict
            Data row containing question and schema

        Returns
        -------
        str
            Formatted prompt for LLM
        """
        schema = row["schema"]
        question = row["question"]
        return PROMPT.format(question=question, schema=schema)
