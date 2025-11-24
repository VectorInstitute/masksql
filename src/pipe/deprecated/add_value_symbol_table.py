# mypy: ignore-errors

"""Module for adding symbolic representations of values to the symbol table."""

from typing import Any

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.schema_repo import DatabaseSchemaRepo


class AddValueSymbolTable(JsonListTransformer):
    """
    Add symbolic representations for values to the symbol table.

    Extends the symbol table with value symbols for values detected in questions.

    Parameters
    ----------
    tables_path : str
        Path to the database schema definitions file
    """

    def __init__(self, tables_path: str) -> None:
        super().__init__(True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def __process_row_internal(self, row: dict[str, Any]) -> dict[str, Any]:
        vid = 1
        value_links = row["value_links"]
        symbol_table = row["symbolic"]["to_symbol"]
        to_value = {}
        for value in value_links:
            symbol = f"[V{vid}]"
            symbol_table[value] = symbol
            to_value[symbol] = value
            vid += 1
        row["symbolic"]["to_symbol"] = symbol_table
        row["symbolic"]["to_value"] = to_value
        return row
