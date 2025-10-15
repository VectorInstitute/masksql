"""Module for adding foreign key relationships to database schemas."""

from src.pipe import JsonProcessor
from src.pipe.schema_repo import DatabaseSchemaRepo


class AddForeignKeys(JsonProcessor):
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

    def __init__(self, prop_name, tables_path):
        super().__init__(prop_name, force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row):
        fks = []
        schema = self.schema_repo.dbs[row["db_id"]]
        for table_name, table_columns in schema.tables.items():
            for col_name, col_data in table_columns.items():
                if isinstance(col_data, dict) and "foreign_key" in col_data:
                    fks.append(f"{table_name}.{col_name}={col_data['foreign_key']}")
        return fks
