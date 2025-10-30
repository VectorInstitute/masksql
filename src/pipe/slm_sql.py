"""SLM (Small Language Model) SQL generation module."""

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.gen_sql import extract_sql
from src.pipe.slm_sql_prompt.v1 import GENERATE_SQL_PROMPT_V1


class SlmSQL(PromptProcessor):
    """Generate SQL using a small language model.

    This class processes natural language questions and database schemas
    to generate SQL queries using a small language model.
    """

    def _process_output(self, row, output):
        """Process the LLM output to extract SQL.

        Parameters
        ----------
        row : dict
            The input row data.
        output : str
            The raw output from the language model.

        Returns
        -------
        str
            The extracted SQL query.
        """
        return extract_sql(output)

    def _get_prompt(self, row):
        """Generate the prompt for SQL generation.

        Parameters
        ----------
        row : dict
            The input row containing 'question' and 'schema'.

        Returns
        -------
        str
            The formatted prompt for the language model.
        """
        question = row["question"]
        schema = row["schema"]
        return GENERATE_SQL_PROMPT_V1.format(question=question, schema=schema)
