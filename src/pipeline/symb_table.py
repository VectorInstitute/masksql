"""Symbol table for tracking symbolic representations."""

from pydantic import BaseModel

from src.pipeline.add_schema import AddFilteredSchema
from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.utils.schema_repo import DatabaseSchema, DatabaseSchemaRepo


class SymbolTableDicts(BaseModel):
    """
    Data model for bidirectional symbol-name mappings.

    Provides mappings between symbolic representations and their
    corresponding database element names.
    """

    to_name: dict[str, str]
    to_symbol: dict[str, str]


class AddSymbolTable(
    JsonListProcessor[AddFilteredSchema.Model, "AddSymbolTable.Model"]
):
    """
    Create symbol tables mapping database elements to symbolic representations.

    Generates symbolic placeholders for tables and columns in the database schema.

    Parameters
    ----------
    tables_path : str
        Path to the database schema definitions file
    """

    class Model(AddFilteredSchema.Model):
        """Data model for symbol table processing.

        Extends the filtered schema model with symbolic representations
        of database elements.
        """

        symbolic: SymbolTableDicts

    def __init__(self, tables_path: str) -> None:
        super().__init__(self.Model, force=True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    def table_symbol(self, idx: int) -> str:
        """
        Generate a table symbol.

        Parameters
        ----------
        idx : int
            Table index

        Returns
        -------
        str
            Table symbol in format [TN]
        """
        return f"[T{idx}]"

    def col_symbol(self, idx: int) -> str:
        """
        Generate a column symbol.

        Parameters
        ----------
        idx : int
            Column index

        Returns
        -------
        str
            Column symbol in format [CN]
        """
        return f"[C{idx}]"

    async def _process_row(self, row: AddFilteredSchema.Model) -> Model:
        schema = DatabaseSchema.from_yaml(row.db_schema)
        tid = 1
        cid = 1
        symbol_table = {}
        rev_table = {}
        for table_name, columns in schema.tables.items():
            table_symbol = self.table_symbol(tid)
            tid += 1
            symbol_table[table_symbol] = table_name
            rev_table[table_name] = table_symbol
            for col_name in columns:
                col_ref = f"{table_name}.{col_name}"
                col_symbol = f"{self.col_symbol(cid)}"
                cid += 1
                symbol_table[col_symbol] = col_ref
                rev_table[col_ref] = col_symbol
        symbolic_dicts = SymbolTableDicts(to_name=symbol_table, to_symbol=rev_table)
        return self.Model(symbolic=symbolic_dicts, **row.dict())
