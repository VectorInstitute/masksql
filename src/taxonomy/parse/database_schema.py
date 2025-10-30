"""Database schema representation for SQL parsing and analysis."""

from difflib import SequenceMatcher
from typing import Dict, FrozenSet, List, Set, Tuple

from loguru import logger


def str_similarity(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings (case-insensitive).

    Parameters
    ----------
    s1 : str
        First string to compare.
    s2 : str
        Second string to compare.

    Returns
    -------
    float
        Similarity ratio between 0 and 1.
    """
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


class DatabaseSchemaSqlyzr:
    """Database schema container for SQL analysis.

    Attributes
    ----------
    tables : Dict[str, Dict[str, str]]
        Mapping of table names to their columns and types.
    foreign_keys : Set[FrozenSet[Tuple[str, str]]]
        Set of foreign key relationships between tables.
    """

    tables: Dict[str, Dict[str, str]]  # {table_name -> {col_name -> col_type}}
    foreign_keys: Set[FrozenSet[Tuple[str, str]]]

    def __init__(self):
        """Initialize empty database schema."""
        self.tables = {}
        self.foreign_keys = set()

    def find_most_similar_column(
        self, table_name: str, col_name: str, cand_cols: Set[str]
    ) -> str | None:
        """Find the most similar column name in a table.

        Searches first in candidate columns, then in all table columns.

        Parameters
        ----------
        table_name : str
            Name of the table to search in.
        col_name : str
            Column name to match.
        cand_cols : Set[str]
            Candidate columns to search first.

        Returns
        -------
        str or None
            Best matching column name if similarity > 0.5, otherwise None.
        """
        if table_name not in self.tables:
            logger.debug(f"Table not found: {table_name}")
            return None
        table = self.tables[table_name]
        max_sim = 0
        best_col = None
        for col in cand_cols:
            sim = str_similarity(col, col_name)
            if sim >= max_sim:
                max_sim = sim
                best_col = col
        if max_sim > 0.5:
            return best_col
        for col in table:
            sim = str_similarity(col, col_name)
            if sim >= max_sim:
                max_sim = sim
                best_col = col
        if max_sim > 0.5:
            return best_col
        return None

    def get_col_type(self, table_name: str, col_name: str) -> str:
        """Get the type of a column in a table.

        Parameters
        ----------
        table_name : str
            Name of the table.
        col_name : str
            Name of the column.

        Returns
        -------
        str
            Column type or "NA" if not found.
        """
        if table_name not in self.tables:
            logger.debug(f"Table not found: {table_name}")
            return "NA"
        table = self.tables[table_name]
        if col_name in table:
            return table[col_name]
        logger.debug(f"Column not found: {col_name}")
        return "NA"

    def get_table_name(self, col_name: str, candidate_tables: List[str]) -> str:
        """Find the table that has a column with the given name.

        Searches only in tables given as candidate_tables.

        Parameters
        ----------
        col_name : str
            Column name to search for.
        candidate_tables : List[str]
            List of candidate table names to search in.

        Returns
        -------
        str
            Table name containing the column, or "NA" if not found/ambiguous.
        """
        matched_tables = []
        for table in candidate_tables:
            if table not in self.tables:
                logger.debug(
                    f"Candidate table not found: {table}, Available tables: {self.tables.keys()}"
                )
                return "NA"
            if col_name in self.tables[table]:
                matched_tables.append(table)
        if len(matched_tables) == 1:
            return matched_tables[0]
        if len(matched_tables) == 0:
            logger.debug(
                f"Column not found in candidate tables: {col_name}, {candidate_tables}"
            )
        for table in self.tables:
            if col_name in self.tables[table]:
                matched_tables.append(table)
        if len(matched_tables) == 1:
            return matched_tables[0]
        if len(matched_tables) == 0:
            logger.debug(
                f"Column not found in candidate tables: {col_name}, {candidate_tables}"
            )
            return "NA"
        if len(matched_tables) > 1:
            logger.debug(
                f"Ambiguous column name: {col_name}, matched tables: {matched_tables}"
            )
            return matched_tables[0]
        return "NA"

    def __str__(self):
        """Return string representation of the database schema."""
        res = "\nTables: \n"
        for table, columns in self.tables.items():
            res += f"\tTable Name: {table}\n"
            res += "\t\tColumns:\n"
            for col, col_type in columns.items():
                res += f"\t\t\tColumn Name: {col}, Column type: {col_type}\n"
        return res
