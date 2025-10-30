"""Extra SQL keyword tags."""

from enum import auto
from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.node import (
    BetweenExpressionNode,
    BinOpExpressionNode,
    FunctionExpressionNode,
    LimitNode,
    OrderByNode,
    ResultColumnNode,
    SelectClauseNode,
)
from src.taxonomy.parse.parser import NULL_LITERAL


class ExtraKeywords(SqlTag):
    """Tags for additional SQL keywords like DISTINCT, LIMIT, ORDER BY, etc."""

    Distinct = auto()
    Limit = auto()
    OrderBy = auto()
    ALL = auto()
    LIKE = auto()
    BETWEEN = auto()
    IS_NULL = auto()
    IN = auto()
    EXISTS = auto()
    AGGREGATE = auto()
    CTE = auto
    PARTITION_BY = auto()
    RANK = auto()

    @staticmethod
    class Collector(TagCollector):
        """Collector for extra SQL keywords."""

        def visit_between_expression(
            self, node: BetweenExpressionNode
        ) -> TagCollectorResult:
            """Visit a BETWEEN expression node."""
            tags = cast(TagCollectorResult, super().visit_between_expression(node))
            tags += TagCollectorResult(ExtraKeywords.BETWEEN)
            return tags

        def visit_function_expression(
            self, node: FunctionExpressionNode
        ) -> TagCollectorResult:
            """Visit a function expression node."""
            tags = cast(TagCollectorResult, super().visit_function_expression(node))
            if node.fun_name.value == "exists":
                tags += TagCollectorResult(ExtraKeywords.EXISTS)
            return tags

        def visit_select_clause(self, node: SelectClauseNode) -> TagCollectorResult:
            """Visit a SELECT clause node."""
            tags = cast(TagCollectorResult, super().visit_select_clause(node))
            if node.distinct:
                tags += TagCollectorResult(ExtraKeywords.Distinct)
            return tags

        def visit_result_column(self, node: ResultColumnNode) -> TagCollectorResult:
            """Visit a result column node."""
            tags = cast(TagCollectorResult, super().visit_result_column(node))
            # FIXME: Need to check if its aggregate
            if isinstance(node.expr, FunctionExpressionNode):
                tags += TagCollectorResult(ExtraKeywords.AGGREGATE)
            return tags

        def visit_limit(self, node: LimitNode) -> TagCollectorResult:
            """Visit a LIMIT node."""
            return TagCollectorResult(ExtraKeywords.Limit)

        def visit_order_by(self, node: OrderByNode) -> TagCollectorResult:
            """Visit an ORDER BY node."""
            tags = cast(TagCollectorResult, super().visit_order_by(node))
            return tags + TagCollectorResult(ExtraKeywords.OrderBy)

        def visit_bin_op_expression(
            self, node: BinOpExpressionNode
        ) -> TagCollectorResult:
            """Visit a binary operation expression node."""
            tags = cast(TagCollectorResult, super().visit_bin_op_expression(node))
            # FIXME: Use objects for terminal Literals like these
            if node.op.value.lower() == "like":
                tags += TagCollectorResult(ExtraKeywords.LIKE)
            if node.op.value.lower() == "in":
                tags += TagCollectorResult(ExtraKeywords.IN)
            if node.op.value.lower() in ["is not", "is"] and (
                NULL_LITERAL in (node.left, node.right)
            ):
                tags += TagCollectorResult(ExtraKeywords.IS_NULL)
            return tags
