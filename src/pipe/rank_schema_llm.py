"""LLM-based schema ranking."""

from typing import Any

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.rank_schema_prompts.v1 import RANK_SCHEMA_ITEMS_V1
from src.pipe.schema_repo import DatabaseSchemaRepo
from src.utils.logging import logger


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

    def _sanitize_schema_item(self, item: str) -> str | None:
        """
        Sanitize a schema item reference to ensure proper formatting.

        Parameters
        ----------
        item : str
            Schema item reference (e.g., "TABLE:[name]" or "COLUMN:[table].[col]")

        Returns
        -------
        str or None
            Sanitized schema item or None if invalid
        """
        if not isinstance(item, str) or ":" not in item:
            return None

        parts = item.split(":", 1)
        if len(parts) != 2:
            return None

        item_type, item_ref = parts

        # Skip empty references
        if not item_ref or item_ref.strip() in ["", ".", "[.]"]:
            return None

        # Ensure all opening brackets have closing brackets
        bracket_count = item_ref.count("[") - item_ref.count("]")
        if bracket_count > 0:
            # Add missing closing brackets
            item_ref = item_ref + ("]" * bracket_count)
        elif bracket_count < 0:
            # More closing than opening - invalid
            return None

        return f"{item_type}:{item_ref}"

    def _process_output(self, row: dict[str, Any], output: str) -> list[str]:
        result = extract_object(output)

        # Handle None or invalid output
        if result is None or not isinstance(result, list):
            logger.warning(
                f"LLM returned invalid schema items for question_id={row.get('question_id')}, "
                f"falling back to all schema items"
            )
            # Fallback: return all schema items
            return self.extract_schema_items(row)

        # Sanitize and filter out invalid items
        sanitized_items = []
        for item in result:
            sanitized = self._sanitize_schema_item(item)
            if sanitized:
                sanitized_items.append(sanitized)

        # If sanitization removed everything, fallback to all items
        if not sanitized_items:
            logger.warning(
                f"All LLM schema items were invalid for question_id={row.get('question_id')}, "
                f"falling back to all schema items"
            )
            return self.extract_schema_items(row)

        return sanitized_items

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
