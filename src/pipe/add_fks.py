"""Module for adding foreign key relationships to database schemas."""

from typing import Any

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.schema_repo import DatabaseSchemaRepo


class AddForeignKeys(JsonListTransformer):
    """
    Processor for adding foreign key relationships to database schemas.

    This class extracts and formats foreign key relationships from database schemas,
    making them available for downstream processing.

    Parameters
    ----------
    prop_name : str
        The property name where foreign keys will be stored in the row.
    tables_path : str
        Path to the database tables/schemas repository.
    """

    def __init__(self, prop_name: str, tables_path: str) -> None:
        super().__init__(force=True)
        self.prop_name = prop_name
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        fks = []
        schema = self.schema_repo.dbs[row["db_id"]]
        for table_name, table_columns in schema.tables.items():
            for col_name, col_data in table_columns.items():
                if isinstance(col_data, dict) and "foreign_key" in col_data:
                    fks.append(f"{table_name}.{col_name}={col_data['foreign_key']}")
        row[self.prop_name] = fks
        return row
