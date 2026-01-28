"""Module for adding database schema information to data rows."""

from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.pipeline.rank_schema import RankSchemaResd
from src.utils.schema_repo import DatabaseSchema, DatabaseSchemaRepo


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
            if isinstance(fk_ref, str):
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


class AddFilteredSchema(
    JsonListProcessor[RankSchemaResd.Model, "AddFilteredSchema.Model"]
):
    """
    Processor for adding filtered database schema to data rows.

    Only includes schema items that are referenced in the row's schema_items list.

    Parameters
    ----------
    tables_path : str
        Path to the database tables/schemas repository.
    """

    class Model(RankSchemaResd.Model):
        """Data model with filtered database schema.

        This model extends the RankSchemaResd.Model by adding a filtered
        database schema that only includes relevant schema items.

        Attributes
        ----------
            db_schema: YAML representation of the filtered database schema
        """

        db_schema: str

    def __init__(self, tables_path: str) -> None:
        super().__init__(self.Model, force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: RankSchemaResd.Model) -> Model:
        schema = self.schema_repo.dbs[row.db_id]
        schema_items = row.schema_items
        filtered_schema = filter_schema(schema, schema_items)
        return self.Model(db_schema=filtered_schema.to_yaml(), **row.dict())
