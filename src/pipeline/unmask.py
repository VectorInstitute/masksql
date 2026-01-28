"""Unmasking of symbolic placeholders in generated SQL."""

import re

from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.pipeline.repair_symb_sql.repair_symb_sql import RepairSymbolicSQL
from src.utils.strings import replace_str_punc


class AddConcreteSql(
    JsonListProcessor[RepairSymbolicSQL.Model, "AddConcreteSql.Model"]
):
    """
    Convert symbolic SQL to concrete SQL by replacing symbols with actual names.

    Replaces symbolic placeholders (e.g., [T1], [C2], [V3]) in SQL queries
    with their original table names, column names, and values.
    """

    class Model(RepairSymbolicSQL.Model):
        """Data model for concrete SQL generation.

        Extends the symbolic SQL model with the concrete SQL query
        where all symbols have been replaced with actual database elements.
        """

        concrete_sql: str = ""

    def __init__(self) -> None:
        super().__init__(self.Model, force=True)

    def get_value_variations(self, value_symbol: str) -> list[str]:
        """
        Generate different quote variations of a value symbol.

        Parameters
        ----------
        value_symbol : str
            The value symbol to generate variations for

        Returns
        -------
        List[str]
            List of symbol variations with different quote styles
        """
        return [value_symbol, f'"{value_symbol[1:-1]}"', f"'{value_symbol[1:-1]}'"]

    async def _process_row(self, row: "RepairSymbolicSQL.Model") -> Model:
        reverse_dict = row.symbolic.reverse_dict
        value_table = row.symbolic.to_value

        symbolic_sql = row.symbolic.repaired_sql

        for symbol, name in reverse_dict.items():
            if "." in symbol:
                symbolic_sql = replace_str_punc(symbolic_sql, symbol, name)

        for symbol, name in reverse_dict.items():
            symbolic_sql = replace_str_punc(symbolic_sql, symbol, name)

        for symbol, value in value_table.items():
            for symbol_variation in self.get_value_variations(symbol):
                symbolic_sql = replace_str_punc(symbolic_sql, symbol_variation, value)

        for symbol, name in reverse_dict.items():
            if "." in symbol:
                assert "." in name
                col_symbol = symbol.split(".")[1]
                col = name.split(".")[1]
                symbolic_sql = re.sub(
                    r"(?<=\.){}(?!\w)".format(re.escape(col_symbol)),
                    col,
                    symbolic_sql,
                    flags=re.IGNORECASE,
                )

        concrete_sql = symbolic_sql
        return self.Model(**row.dict(), concrete_sql=concrete_sql)
