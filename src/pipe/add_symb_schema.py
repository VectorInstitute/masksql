"""Module for converting database schemas to symbolic representations."""

from typing import Any

from src.pipe.link_schema import FilterSchemaLinksModel
from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.schema_repo import DatabaseSchema, DatabaseSchemaRepo
from src.pipe.symb_table import SymbolTableDicts


class SymbolicSchema(SymbolTableDicts):
    """Symbolic representation of a database schema.

    This class extends SymbolTableDicts to include a symbolic representation
    of a database schema, where table and column names are replaced with
    symbolic identifiers (e.g., T1, C1).

    Attributes
    ----------
        db_schema: YAML representation of the symbolic database schema
        reverse_dict: Mapping from symbolic identifiers back to original names
    """

    db_schema: str
    reverse_dict: dict[str, str]


class AddSymbolicSchema(
    JsonListProcessor[FilterSchemaLinksModel, "AddSymbolicSchema.Model"]
):
    """
    Processor for converting database schemas to symbolic representations.

    Replaces table and column names with symbolic identifiers (e.g., T1, C1).

    Parameters
    ----------
    tables_path : str
        Path to the database tables/schemas repository.
    """

    class Model(FilterSchemaLinksModel):
        """Data model with symbolic schema representation.

        This model extends FilterSchemaLinksModel by adding a symbolic
        representation of the database schema.

        Attributes
        ----------
            symbolic: Symbolic representation of the database schema
        """

        symbolic: SymbolicSchema

    def __init__(self, tables_path: str) -> None:
        super().__init__(self.Model, force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row: FilterSchemaLinksModel) -> Model:
        schema = DatabaseSchema.from_yaml(row.db_schema)
        symbol_table = row.symbolic.to_symbol

        symbolic_schema = self.get_symb_schema(schema, symbol_table)

        reverse_dict = self.get_reverse_dict(schema, symbol_table)

        symbolic = SymbolicSchema(
            **row.symbolic.dict(),
            db_schema=symbolic_schema.to_yaml(),
            reverse_dict=reverse_dict,
        )

        return self.Model(**row.dict(exclude={"symbolic"}), symbolic=symbolic)

    def get_col_symbol(
        self, table_name: str, col_name: str, symbol_table: dict[str, str]
    ) -> str:
        """
        Get symbolic representation for a column.

        Parameters
        ----------
        table_name : str
            Name of the table.
        col_name : str
            Name of the column.
        symbol_table : Dict[str, str]
            Mapping from names to symbols.

        Returns
        -------
        str
            Symbolic representation of the column.
        """
        col_ref = f"{table_name}.{col_name}"
        return symbol_table[col_ref]

    def get_table_symbol(self, table_name: str, symbol_table: dict[str, str]) -> str:
        """
        Get symbolic representation for a table.

        Parameters
        ----------
        table_name : str
            Name of the table.
        symbol_table : Dict[str, str]
            Mapping from names to symbols.

        Returns
        -------
        str
            Symbolic representation of the table.
        """
        return symbol_table[table_name]

    def get_symbolic_col_data(
        self, col_data: str | dict[str, Any], symbol_table: dict[str, str]
    ) -> str | dict[str, Any]:
        """
        Convert column data to symbolic representation.

        Parameters
        ----------
        col_data : Union[str, Dict[str, str]]
            Column data including potential foreign key references.
        symbol_table : Dict[str, str]
            Mapping from names to symbols.

        Returns
        -------
        str
            Symbolic representation of column data.
        """
        symbolic_col_data: str | dict[str, Any]
        if isinstance(col_data, dict) and "foreign_key" in col_data:
            symbolic_col_data = col_data.copy()
            foreign_col_ref = symbolic_col_data["foreign_key"]
            table_name = foreign_col_ref.split(".")[0]
            table_symbol = self.get_table_symbol(table_name, symbol_table)
            column_name = foreign_col_ref.split(".")[1]
            column_symbol = self.get_col_symbol(table_name, column_name, symbol_table)
            symbolic_col_data["foreign_key"] = f"{table_symbol}.{column_symbol}"
        else:
            symbolic_col_data = col_data
        return symbolic_col_data

    def get_symb_schema(
        self, schema: DatabaseSchema, symbol_table: dict[str, str]
    ) -> DatabaseSchema:
        """
        Convert entire schema to symbolic representation.

        Parameters
        ----------
        schema : DatabaseSchema
            Database schema to convert.
        symbol_table : Dict[str, str]
            Mapping from names to symbols.

        Returns
        -------
        DatabaseSchema
            Schema with all names replaced by symbols.
        """
        symbolic_schema = DatabaseSchema()

        for table_name, columns in list(schema.tables.items()):
            symbolic_columns = {}
            for col_name, col_data in columns.items():
                col_symbol = self.get_col_symbol(table_name, col_name, symbol_table)
                symbolic_col_data = self.get_symbolic_col_data(col_data, symbol_table)
                symbolic_columns[col_symbol] = symbolic_col_data
            table_symbol = self.get_table_symbol(table_name, symbol_table)
            symbolic_schema.tables[table_symbol] = symbolic_columns
        return symbolic_schema

    def get_reverse_dict(
        self, schema: DatabaseSchema, symbol_table: dict[str, str]
    ) -> dict[str, str]:
        """
        Create reverse mapping from symbols to original names.

        Parameters
        ----------
        schema : DatabaseSchema
            Database schema.
        symbol_table : Dict[str, str]
            Mapping from names to symbols.

        Returns
        -------
        Dict[str, str]
            Reverse mapping from symbols to original names.
        """
        reverse_dict = {}
        for table_name, columns in list(schema.tables.items()):
            table_symbol = symbol_table[table_name]
            reverse_dict[table_symbol] = table_name
            for col_name, _col_data in columns.items():
                col_ref = f"{table_name}.{col_name}"
                col_symbol = symbol_table[col_ref]
                reverse_dict[f"{table_symbol}.{col_symbol}"] = col_ref
                reverse_dict[col_symbol] = col_ref
        return reverse_dict
