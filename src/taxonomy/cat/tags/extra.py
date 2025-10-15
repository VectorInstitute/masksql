"""Extra SQL keyword tags."""

from enum import auto

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

        def visit_between_expression(self, node: BetweenExpressionNode):
            """Visit a BETWEEN expression node."""
            tags = super().visit_between_expression(node)
            tags += TagCollectorResult(ExtraKeywords.BETWEEN)
            return tags

        def visit_function_expression(self, node: FunctionExpressionNode):
            """Visit a function expression node."""
            tags = super().visit_function_expression(node)
            if node.fun_name.value == "exists":
                tags += TagCollectorResult(ExtraKeywords.EXISTS)
            return tags

        def visit_select_clause(self, node: SelectClauseNode):
            """Visit a SELECT clause node."""
            tags = super().visit_select_clause(node)
            if node.distinct:
                tags += TagCollectorResult(ExtraKeywords.Distinct)
            return tags

        def visit_result_column(self, node: ResultColumnNode):
            """Visit a result column node."""
            tags = super().visit_result_column(node)
            # FIXME: Need to check if its aggregate
            if isinstance(node.expr, FunctionExpressionNode):
                tags += TagCollectorResult(ExtraKeywords.AGGREGATE)
            return tags

        def visit_limit(self, node: LimitNode):
            """Visit a LIMIT node."""
            return TagCollectorResult(ExtraKeywords.Limit)

        def visit_order_by(self, node: OrderByNode):
            """Visit an ORDER BY node."""
            tags = super().visit_order_by(node)
            return tags + TagCollectorResult(ExtraKeywords.OrderBy)

        def visit_bin_op_expression(self, node: BinOpExpressionNode):
            """Visit a binary operation expression node."""
            tags = super().visit_bin_op_expression(node)
            # FIXME: Use objects for terminal Literals like these
            if node.op.value.lower() == "like":
                tags += TagCollectorResult(ExtraKeywords.LIKE)
            if node.op.value.lower() == "in":
                tags += TagCollectorResult(ExtraKeywords.IN)
            if node.op.value.lower() in ["is not", "is"] and (
                node.left == NULL_LITERAL or node.right == NULL_LITERAL
            ):
                tags += TagCollectorResult(ExtraKeywords.IS_NULL)
            return tags
