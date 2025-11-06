"""Module for adding database schema information to data rows."""

from typing import Any

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.schema_repo import DatabaseSchema, DatabaseSchemaRepo


def _parse_schema_item(item: str) -> str | None:
    """
    Parse and validate a schema item reference.

    Parameters
    ----------
    item : str
        Schema item reference (e.g., 'COLUMN:table.column').

    Returns
    -------
    str or None
        Column reference if valid COLUMN item, None otherwise.
    """
    if not isinstance(item, str) or ":" not in item:
        return None

    parts = item.split(":", 1)
    if len(parts) != 2:
        return None

    item_type, item_ref = parts

    if "[*]" in item_ref or item_type != "COLUMN":
        return None

    return item_ref


def _parse_column_ref(col_ref: str) -> tuple[str, str] | None:
    """
    Parse a column reference into table and column names.

    Parameters
    ----------
    col_ref : str
        Column reference in format 'table.column'.

    Returns
    -------
    tuple[str, str] or None
        (table_name, col_name) if valid, None otherwise.
    """
    if "." not in col_ref:
        return None

    parts = col_ref.split(".", 1)
    if len(parts) != 2:
        return None

    return parts[0], parts[1]


def _get_foreign_key(
    schema: DatabaseSchema, table_name: str, col_name: str
) -> str | None:
    """
    Get foreign key reference for a column if it exists.

    Parameters
    ----------
    schema : DatabaseSchema
        The database schema.
    table_name : str
        Name of the table.
    col_name : str
        Name of the column.

    Returns
    -------
    str or None
        Foreign key reference if exists, None otherwise.
    """
    if table_name not in schema.tables or col_name not in schema.tables[table_name]:
        return None

    col_data = schema.tables[table_name][col_name]
    if isinstance(col_data, dict) and "foreign_key" in col_data:
        fk_ref = col_data["foreign_key"]
        if isinstance(fk_ref, str):
            return fk_ref

    return None


def filter_schema(schema: DatabaseSchema, schema_items: list[str]) -> DatabaseSchema:
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
    if not schema_items:
        return DatabaseSchema()

    # Extract valid column references from schema items
    columns = set()
    for item in schema_items:
        col_ref = _parse_schema_item(item)
        if col_ref:
            columns.add(col_ref)

    # Add foreign key references
    for col_ref in list(columns):
        parsed = _parse_column_ref(col_ref)
        if not parsed:
            continue

        table_name, col_name = parsed
        fk_ref = _get_foreign_key(schema, table_name, col_name)
        if fk_ref:
            columns.add(fk_ref)

    # Build filtered schema
    filtered_schema = DatabaseSchema()
    for table_name, table_columns in schema.tables.items():
        filtered_table_columns = {
            col_name: col_data
            for col_name, col_data in table_columns.items()
            if f"{table_name}.{col_name}" in columns
        }
        if filtered_table_columns:
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

    def __init__(self, tables_path: str) -> None:
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
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

    def __init__(self, tables_path: str) -> None:
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
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

    def __init__(self, tables_path: str) -> None:
        super().__init__(force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        schema = self.schema_repo.dbs[row["db_id"]]
        schema_items = []
        for table, columns in schema.tables.items():
            schema_items.append(f"TABLE:{table}")
            for col, _col_data in columns.items():
                schema_items.append(f"COLUMN:{table}.{col}")
            schema_items.append(f"COLUMN:{table}.[*]")
        row["schema_items"] = schema_items
        return row
