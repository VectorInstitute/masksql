"""Symbol table for tracking symbolic representations."""

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.schema_repo import DatabaseSchema, DatabaseSchemaRepo


class AddSymbolTable(JsonListTransformer):
    """
    Create symbol tables mapping database elements to symbolic representations.

    Generates symbolic placeholders for tables and columns in the database schema.

    Parameters
    ----------
    tables_path : str
        Path to the database schema definitions file
    """

    def __init__(self, tables_path):
        super().__init__(True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    def table_symbol(self, idx):
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

    def col_symbol(self, idx):
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

    async def _process_row(self, row):
        schema = DatabaseSchema.from_yaml(row["schema"])
        tid = 1
        cid = 1
        symbol_table = {}
        rev_table = {}
        for table_name, columns in schema.tables.items():
            table_symbol = self.table_symbol(tid)
            tid += 1
            symbol_table[table_symbol] = table_name
            rev_table[table_name] = table_symbol
            for col_name in columns.keys():
                col_ref = f"{table_name}.{col_name}"
                col_symbol = f"{self.col_symbol(cid)}"
                cid += 1
                symbol_table[col_symbol] = col_ref
                rev_table[col_ref] = col_symbol
        row["symbolic"] = {"to_name": symbol_table, "to_symbol": rev_table}
        return row


class AddValueSymbolTable(JsonListTransformer):
    """
    Add symbolic representations for values to the symbol table.

    Extends the symbol table with value symbols for values detected in questions.

    Parameters
    ----------
    tables_path : str
        Path to the database schema definitions file
    """

    def __init__(self, tables_path):
        super().__init__(True)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    async def _process_row(self, row):
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
