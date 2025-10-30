"""Complex SQL keyword tags."""

from enum import auto
from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.node import (
    FunctionExpressionNode,
    WindowExpressionNode,
    WithClauseNode,
)


class ComplexKeywords(SqlTag):
    """Tags for complex SQL keywords like CTE and window functions."""

    CTE = auto()
    WindowFunction = auto()
    CaseExpr = auto()

    @staticmethod
    class Collector(TagCollector):
        """Collector for complex SQL keywords."""

        def visit_with_clause(self, node: WithClauseNode) -> TagCollectorResult:
            """Visit a WITH clause node."""
            tags = cast(TagCollectorResult, super().visit_with_clause(node))
            tags += TagCollectorResult(ComplexKeywords.CTE)
            return tags

        def visit_window_expression(
            self, node: WindowExpressionNode
        ) -> TagCollectorResult:
            """Visit a window expression node."""
            tags = cast(TagCollectorResult, super().visit_window_expression(node))
            tags += TagCollectorResult(ComplexKeywords.WindowFunction)
            return tags

        def visit_function_expression(
            self, node: FunctionExpressionNode
        ) -> TagCollectorResult:
            """Visit a function expression node."""
            tags = cast(TagCollectorResult, super().visit_function_expression(node))
            if node.fun_name.value.lower() == "case":
                tags += TagCollectorResult(ComplexKeywords.CaseExpr)
            return tags
