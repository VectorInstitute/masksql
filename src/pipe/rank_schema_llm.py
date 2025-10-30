"""LLM-based schema ranking."""

from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.rank_schema_prompts.v1 import RANK_SCHEMA_ITEMS_V1
from src.pipe.schema_repo import DatabaseSchemaRepo


class RankSchemaItems(PromptProcessor):
    """
    Rank schema items using language model.

    Parameters
    ----------
    prop_name : str
        Property name for output
    tables_path : str
        Path to tables JSON file
    model : str
        Model identifier to use
    """

    def __init__(self, prop_name: str, tables_path: str, model: str) -> None:
        super().__init__(prop_name, model=model)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    def _process_output(self, row: dict[str, Any], output: str) -> Any:
        return extract_object(output)

    def extract_schema_items(self, row: dict[str, Any]) -> list[str]:
        """
        Extract all schema items from database.

        Parameters
        ----------
        row : dict
            Data row with database ID

        Returns
        -------
        list
            List of schema item strings
        """
        db_id = row["db_id"]
        schema = self.schema_repo.dbs[db_id]
        schema_items = []

        for table_name, columns in schema.tables.items():
            schema_items.append(f"TABLE:{table_name}")
            for col_name, _col_data in columns.items():
                schema_items.append(f"COLUMN:{table_name}.{col_name}")
        return schema_items

    def _get_prompt(self, row: dict[str, Any]) -> str:
        question = row["question"]
        schema_items = self.extract_schema_items(row)
        return RANK_SCHEMA_ITEMS_V1.format(question=question, schema_items=schema_items)
