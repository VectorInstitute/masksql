"""Lexer for SQL parsing using PLY (Python Lex-Yacc).

This module defines tokens and lexical rules for SQL tokenization.

Note: Function names like t_TOKEN follow PLY's required naming convention
and cannot be changed to lowercase (ruff: noqa: N802).
"""

import re
from typing import Any

from ply import lex


fun_names = {"avg": "AVG", "sum": "SUM", "min": "MIN", "max": "MAX", "count": "COUNT"}

sort_orders = {"asc": "ASC", "desc": "DESC"}

set_ops = {
    "union": "UNION",
    "minus": "SET_MINUS",
    "except": "EXCEPT",
    "intersect": "INTERSECT",
}

logic_ops = {"and": "AND", "or": "OR"}

keywords = {
    "select": "SELECT",
    "from": "FROM",
    "where": "WHERE",
    "group": "GROUP",
    "join": "JOIN",
    "order": "ORDER",
    "limit": "LIMIT",
    "like": "LIKE",
    "regexp": "REGEXP",
    "having": "HAVING",
    "on": "ON",
    "by": "BY",
    "as": "AS",
    "in": "IN",
    "is": "IS",
    "null": "NULL",
    "not": "NOT",
    "between": "BETWEEN",
    "distinct": "DISTINCT",
    "exists": "EXISTS",
    "inner": "INNER",
    "cast": "CAST",
    "left": "LEFT",
    "full": "FULL",
    "outer": "OUTER",
    "cross": "CROSS",
    "rollup": "ROLLUP",
    "right": "RIGHT",
    "rank": "RANK",
    "row_number": "ROW_NUMBER",
    "dense_rank": "DENSE_RANK",
    "partition": "PARTITION",
    "over": "OVER",
    "end": "END",
    "then": "THEN",
    "else": "ELSE",
    "case": "CASE",
    "when": "WHEN",
    "with": "WITH",
    "recursive": "RECURSIVE",
    "all": "ALL",
    "using": "USING",
}

reserved = keywords | sort_orders | set_ops | logic_ops

tokens = [
    "ID",
    "NUMBER",
    "COMMA",
    "LPAREN",
    "RPAREN",
    "COMP_OP",
    "ARITH_OP",
    "DOT",
    "STRING",
    "STAR",
    "ORR",
    "MINUS",
    "DATE_LITERAL",
    "TYPE_NAME",
] + list(reserved.values())


def t_NUMBER(t: Any) -> Any:  # noqa: N802
    r"""Match numeric literals (integers and floats)."""
    if t.value.isdigit():
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    return t


t_COMMA = r","  # noqa: N816
t_LPAREN = r"\("  # noqa: N816
t_RPAREN = r"\)"  # noqa: N816
t_STAR = r"\*"  # noqa: N816
t_DOT = r"\."  # noqa: N816
t_ORR = r"\|\|"  # noqa: N816
t_MINUS = r"-"  # noqa: N816


def t_TYPE_NAME(t: Any) -> Any:  # noqa: N802
    r"""Match SQL type names (integer, varchar, datetime, etc.)."""
    t.value = t.value.lower()
    return t


def t_DATE_LITERAL(t: Any) -> Any:  # noqa: N802
    r"""Match date literals in YYYY-MM-DD format."""
    return t


# r'\'[^\']*\'|\"[^\"]*\"'
def t_STRING(t: Any) -> Any:  # noqa: N802
    r"""Match string literals enclosed in quotes."""
    val = str(t.value)
    val = val.replace('"', "")
    val = val.replace("'", "")
    val = val.replace("''", "")
    val = val.replace("`", "")
    # val = val.lower()
    t.value = val
    return t


def t_ARITH_OP(t: Any) -> Any:  # noqa: N802
    r"""Match arithmetic operators (+, /, %, ^)."""
    return t


def t_COMP_OP(t: Any) -> Any:  # noqa: N802
    r"""Match comparison operators (=, !=, <, >, <=, >=, <>)."""
    return t


def t_ID(t: Any) -> Any:  # noqa: N802
    r"""Match identifiers and reserved keywords."""
    if t.value.lower() in reserved:
        t.value = t.value.lower()
        t.type = reserved[t.value.lower()]
    else:
        t.value = t.value.lower()
        t.type = "ID"  # Check for reserved words
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = " "  # noqa: N816


# Error handling rule
def t_error(t: Any) -> None:
    """Handle lexer errors by skipping illegal characters."""
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def get_lexer() -> Any:
    """Create and return a lexer instance with case-insensitive matching."""
    return lex.lex(reflags=re.IGNORECASE)
