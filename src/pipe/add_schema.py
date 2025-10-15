"""Module for adding database schema information to data rows."""

from typing import List

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.schema_repo import DatabaseSchema, DatabaseSchemaRepo


def filter_schema(schema: DatabaseSchema, schema_items: List[str]):
    """
    Filter database schema to include only specified schema items.

    Parameters
    ----------
    schema : DatabaseSchema
        The full database schema to filter.
    schema_items : List[str]
        List of schema item references (e.g., 'COLUMN:table.column').

    Returns
    -------
    DatabaseSchema
        Filtered schema containing only the specified items and their foreign keys.
    """
    columns = set()
    for item in schema_items:
        item_ref = item.split(":")[1]
        if "[*]" in item_ref:
            continue
        if item.split(":")[0] == "COLUMN":
            columns.add(item_ref)

    for col_ref in list(columns):
        table_name = col_ref.split(".")[0]
        col_name = col_ref.split(".")[1]
        col_data = schema.tables[table_name][col_name]
        if isinstance(col_data, dict) and "foreign_key" in col_data:
            fk_ref = col_data["foreign_key"]
            columns.add(fk_ref)

    filtered_schema = DatabaseSchema()
    for table_name, table_columns in schema.tables.items():
        filtered_table_columns = {}
        for col_name, col_data in table_columns.items():
            if f"{table_name}.{col_name}" in columns:
                filtered_table_columns[col_name] = col_data
        if len(filtered_table_columns) > 0:
            filtered_schema.tables[table_name] = filtered_table_columns
    return filtered_schema


class AddSchema(JsonListTransformer):
    """
    Processor for adding full database schema to data rows.

    Parameters
    ----------
    tables_path : str
        Path to the database tables/schemas repository.
    """

    def __init__(self, tables_path):
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row):
        schema = self.schema_repo.dbs[row["db_id"]]
        row["schema"] = schema.to_yaml()
        return row


class AddFilteredSchema(JsonListTransformer):
    """
    Processor for adding filtered database schema to data rows.

    Only includes schema items that are referenced in the row's schema_items list.

    Parameters
    ----------
    tables_path : str
        Path to the database tables/schemas repository.
    """

    def __init__(self, tables_path):
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row):
        schema = self.schema_repo.dbs[row["db_id"]]
        schema_items = row["schema_items"]
        filtered_schema = filter_schema(schema, schema_items)
        row["schema"] = filtered_schema.to_yaml()
        return row


class AddSchemaItems(JsonListTransformer):
    """
    Processor for extracting all schema items from database schema.

    Creates a list of all tables and columns in the database schema.

    Parameters
    ----------
    tables_path : str
        Path to the database tables/schemas repository.
    """

    def __init__(self, tables_path):
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row):
        schema = self.schema_repo.dbs[row["db_id"]]
        schema_items = []
        for table, columns in schema.tables.items():
            schema_items.append(f"TABLE:{table}")
            for col, col_data in columns.items():
                schema_items.append(f"COLUMN:{table}.{col}")
            schema_items.append(f"COLUMN:{table}.[*]")
        row["schema_items"] = schema_items
        return row
