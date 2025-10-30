"""SELECT column type tags."""

from enum import auto
from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.node import (
    ColumnNode,
    SelectClauseNode,
)


class SelectColumns(SqlTag):
    """Tags for SELECT column variations."""

    SingleColumn = auto()
    StarColumn = auto()
    MultiColumn = auto()

    @staticmethod
    class Collector(TagCollector):
        """Collector for SELECT column types."""

        def visit_column(self, node: ColumnNode) -> TagCollectorResult:
            """Visit a column node."""
            if node.column_name.value == "*":
                return TagCollectorResult(SelectColumns.StarColumn)
            return TagCollectorResult()

        def visit_select_clause(self, node: SelectClauseNode) -> TagCollectorResult:
            """Visit a SELECT clause node."""
            tags = cast(TagCollectorResult, super().visit_select_clause(node))
            if len(node.result_columns) > 1:
                tags += TagCollectorResult(SelectColumns.MultiColumn)
            elif len(node.result_columns) == 1:
                tags += TagCollectorResult(SelectColumns.SingleColumn)
            return tags

            # if len(node.result_columns) == 1:
            #     col = node.result_columns[0].expr
            #     if isinstance(col, TerminalNode) and col.value == "*":
            #         return TagCollectorResult(SelectColumns.SingleStarColumn)
            #     return TagCollectorResult()
            # else:
            #     return TagCollectorResult(SelectColumns.MultiColumn)
