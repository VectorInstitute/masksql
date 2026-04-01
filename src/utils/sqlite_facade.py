"""Facade for SQLite database operations."""

import os.path
import sqlite3
import time
from collections.abc import Generator
from contextlib import contextmanager
from sqlite3 import Connection
from typing import Any

from loguru import logger


DB_TIMEOUT = 10000


@contextmanager
def sqlite_timelimit(conn: Connection, ms: int) -> Generator[None, None, None]:
    """
    Context manager for enforcing SQLite query time limits.

    Parameters
    ----------
    conn : Connection
        SQLite database connection
    ms : int
        Timeout in milliseconds

    Yields
    ------
    None
        Yields control to execute query within timeout
    """
    deadline = time.perf_counter() + (ms / 1000)
    n = 1000
    if ms <= 20:
        n = 1

    def handler() -> int:
        if time.perf_counter() >= deadline:
            return 1
        return 0

    conn.set_progress_handler(handler, n)
    try:
        yield
    finally:
        conn.set_progress_handler(None, n)
        conn.close()


class SqliteFacade:
    """
    Facade for interacting with SQLite databases.

    Provides convenient methods for querying schema information and executing
    SQL queries with timeout support.

    Parameters
    ----------
    db_dir : str
        Directory containing database subdirectories
    """

    def __init__(self, db_dir: str) -> None:
        self.db_dir = db_dir

    def get_schema_str(self, db_id: str) -> str:
        """
        Get complete schema string for a database.

        Parameters
        ----------
        db_id : str
            Database identifier

        Returns
        -------
        str
            Complete schema description for all tables
        """
        tables_str = []
        for table in self.get_tables(db_id):
            tables_str.append(self.get_table_schema_str(db_id, table))
        return "\n".join(tables_str)

    def get_table_schema_str(self, db_id: str, table: str) -> str:
        """
        Get schema string for a specific table with sample rows.

        Parameters
        ----------
        db_id : str
            Database identifier
        table : str
            Table name

        Returns
        -------
        str
            Schema description with CREATE statement and sample rows
        """
        schema_str = ""
        create_sql = self.get_create_sql(db_id, table)  # type: ignore[attr-defined]
        cols = self.get_col_names(db_id, table)
        cols_str = "\t".join(cols)
        sample_rows, _ = self.exec_query_sync(db_id, f"SELECT * FROM {table} LIMIT 3")
        if sample_rows:
            rows_str = "\n".join(
                "\t".join([str(cv)[:50] for cv in r]) for r in sample_rows
            )
        else:
            rows_str = "\n"
        schema_str += f"\n {create_sql}\n"
        schema_str += f"\n/*\n3 rows from {table}:\n{cols_str}\n{rows_str}\n*/\n"
        return schema_str

    def get_col_names(self, db_id: str, table_name: str) -> list[str]:
        """
        Get column names for a table.

        Parameters
        ----------
        db_id : str
            Database identifier
        table_name : str
            Table name

        Returns
        -------
        list
            List of column names
        """
        res, _ = self.exec_query_sync(db_id, f'PRAGMA table_info("{table_name}")')
        return [_[1] for _ in res] if res else []

    def get_foreign_key(self, db_id: str, table_name: str) -> list[str]:
        """
        Get foreign key relationships for a table.

        Parameters
        ----------
        db_id : str
            Database identifier
        table_name : str
            Table name

        Returns
        -------
        list
            List of foreign key relationship strings
        """
        res_raw, _ = self.exec_query_sync(
            db_id, f'PRAGMA foreign_key_list("{table_name}")'
        )
        res_clean = []
        if res_raw:
            for row in res_raw:
                table, source, to = row[2:5]
                row_clean = f"({table_name}.{source}, {table}.{to})"
                res_clean.append(row_clean)
        return res_clean

    def get_primary_key(self, db_id: str, table_name: str) -> list[str]:
        """
        Get primary key columns for a table.

        Parameters
        ----------
        db_id : str
            Database identifier
        table_name : str
            Table name

        Returns
        -------
        list
            List of primary key column names
        """
        res_raw, _ = self.exec_query_sync(db_id, f'PRAGMA table_info("{table_name}");')
        pks = []
        if res_raw:
            for row in res_raw:
                if row[5] == 1:
                    pks.append(row[1])
        return pks

    def get_tables(self, db_id: str) -> list[str]:
        """
        Get list of table names in database.

        Parameters
        ----------
        db_id : str
            Database identifier

        Returns
        -------
        list
            List of table names
        """
        result, _ = self.exec_query_sync(
            db_id, "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [_[0] for _ in result] if result else []

    def exec_query_sync(
        self, db_id: str, sql: str, timeout: int = DB_TIMEOUT
    ) -> tuple[list[Any] | None, str | None]:
        """
        Execute SQL query synchronously with timeout.

        Parameters
        ----------
        db_id : str
            Database identifier
        sql : str
            SQL query to execute
        timeout : int, optional
            Timeout in milliseconds, default is DB_TIMEOUT

        Returns
        -------
        tuple
            (rows, error) where rows is query result and error is error message if any
        """
        db_file = os.path.join(self.db_dir, db_id, db_id + ".sqlite")
        conn = sqlite3.connect(f"file:{db_file}?mode=ro")
        error = None
        with sqlite_timelimit(conn, DB_TIMEOUT):
            cursor = conn.cursor()
            try:
                cursor.execute(sql)

                rows = cursor.fetchall()
            except Exception as e:
                if e.args == ("interrupted",):
                    logger.debug(f"SQLite Timed out: {db_id} {sql}")
                else:
                    logger.debug(f"SQLite Error: {e}, {sql}")
                rows = None
                error = str(e)
            finally:
                cursor.close()
            return rows, error
