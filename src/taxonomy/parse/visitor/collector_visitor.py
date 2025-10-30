"""Visitor that automatically collects and merges results from SQL AST nodes."""

from dataclasses import fields
from typing import Any, Type

from src.taxonomy.parse.node import (
    CommonTableExpressionNode,
    LiteralListNode,
    SqlAstNode,
    WithClauseNode,
)
from src.taxonomy.parse.visitor.node_visitor import NodeVisitor
from src.taxonomy.parse.visitor.visitor_result import MergeableVisitorResult


class CollectorVisitor(NodeVisitor):
    """Automatically visits all attributes of a node and merges the results.

    This visitor traverses all attributes of SQL AST nodes and combines
    the results using the merge operation.
    """

    def __init__(self, result_class: Type[MergeableVisitorResult]) -> None:
        super().__init__()
        self.result_class = result_class

    def visit_literal_list(self, node: LiteralListNode) -> MergeableVisitorResult:
        """
        Visit a literal list node.

        Parameters
        ----------
        node : LiteralListNode
            The literal list node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_with_clause(self, node: WithClauseNode) -> MergeableVisitorResult:
        """
        Visit a WITH clause node.

        Parameters
        ----------
        node : WithClauseNode
            The WITH clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_common_table_expression(
        self, node: CommonTableExpressionNode
    ) -> MergeableVisitorResult:
        """
        Visit a common table expression node.

        Parameters
        ----------
        node : CommonTableExpressionNode
            The common table expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_window_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a window expression node.

        Parameters
        ----------
        node : WindowExpressionNode
            The window expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_window_definition(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a window definition node.

        Parameters
        ----------
        node : WindowDefinitionNode
            The window definition node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_cast_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a CAST expression node.

        Parameters
        ----------
        node : CastExpressionNode
            The CAST expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def get_new_result_instance(self, attr: Any) -> MergeableVisitorResult:
        """
        Create a new instance of the result class.

        Parameters
        ----------
        attr : Any
            The attribute (unused in base implementation).

        Returns
        -------
        MergeableVisitorResult
            A new instance of the result class.
        """
        return self.result_class()

    def get_attrs(self, node: SqlAstNode) -> list[Any]:
        """
        Get all attributes from a SQL AST node.

        Parameters
        ----------
        node : SqlAstNode
            The SQL AST node to extract attributes from.

        Returns
        -------
        list
            List of all attributes from the node.
        """
        attrs = []
        for f in fields(node.__class__):  # type: ignore[arg-type]
            attr = node.__getattribute__(f.name)
            if type(attr) is list:
                attrs += attr
            else:
                attrs += [attr]
        return attrs

    def visit_node(self, node: SqlAstNode) -> MergeableVisitorResult:
        """Dynamically visit all attributes of the node."""
        data = self.get_new_result_instance(node)
        attrs = self.get_attrs(node)
        for attr in attrs:
            data += self.visit_attr(attr)
        return data

    def visit_attr(self, attr: Any) -> MergeableVisitorResult:
        """Visit the attribute if it is an instance of AstNode.

        Otherwise return an instance of result class.
        """
        if attr and isinstance(attr, SqlAstNode):
            return attr.accept(self)
        return self.get_new_result_instance(attr)

    def visit_ordering_term(self, node: Any) -> MergeableVisitorResult:
        """
        Visit an ordering term node.

        Parameters
        ----------
        node : OrderingTerm
            The ordering term node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_select_statement(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a SELECT statement node.

        Parameters
        ----------
        node : SelectStatementNode
            The SELECT statement node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_select_core(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a SELECT core node.

        Parameters
        ----------
        node : SelectCoreNode
            The SELECT core node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_select_clause(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a SELECT clause node.

        Parameters
        ----------
        node : SelectClauseNode
            The SELECT clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_from_clause(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a FROM clause node.

        Parameters
        ----------
        node : FromClauseNode
            The FROM clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_join_clause(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a JOIN clause node.

        Parameters
        ----------
        node : JoinClauseNode
            The JOIN clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_table_or_subquery(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a table or subquery node.

        Parameters
        ----------
        node : TableOrSubqueryNode
            The table or subquery node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_result_column(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a result column node.

        Parameters
        ----------
        node : ResultColumnNode
            The result column node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_column(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a column node.

        Parameters
        ----------
        node : ColumnNode
            The column node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_where_clause(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a WHERE clause node.

        Parameters
        ----------
        node : WhereClauseNode
            The WHERE clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_group_clause(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a GROUP BY clause node.

        Parameters
        ----------
        node : GroupClauseNode
            The GROUP BY clause node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_between_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a BETWEEN expression node.

        Parameters
        ----------
        node : BetweenExpressionNode
            The BETWEEN expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_order_by(self, node: Any) -> MergeableVisitorResult:
        """
        Visit an ORDER BY node.

        Parameters
        ----------
        node : OrderByNode
            The ORDER BY node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_limit(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a LIMIT node.

        Parameters
        ----------
        node : LimitNode
            The LIMIT node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_join_constraint(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a JOIN constraint node.

        Parameters
        ----------
        node : JoinConstraintNode
            The JOIN constraint node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_function_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a function expression node.

        Parameters
        ----------
        node : FunctionExpressionNode
            The function expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_bin_op_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a binary operation expression node.

        Parameters
        ----------
        node : BinOpExpressionNode
            The binary operation expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_terminal(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a terminal node.

        Parameters
        ----------
        node : TerminalNode
            The terminal node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_expression(self, node: Any) -> MergeableVisitorResult:
        """
        Visit an expression node.

        Parameters
        ----------
        node : ExpressionNode
            The expression node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)

    def visit_literal(self, node: Any) -> MergeableVisitorResult:
        """
        Visit a literal node.

        Parameters
        ----------
        node : LiteralNode
            The literal node to visit.

        Returns
        -------
        MergeableVisitorResult
            The result of visiting the node.
        """
        return self.visit_node(node)
