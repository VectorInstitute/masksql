"""Abstract base class for visiting SQL AST nodes."""

from abc import ABC, abstractmethod
from typing import Any

from src.taxonomy.parse.node import (
    BetweenExpressionNode,
    BinOpExpressionNode,
    CastExpressionNode,
    ColumnNode,
    CommonTableExpressionNode,
    ExpressionNode,
    FromClauseNode,
    FunctionExpressionNode,
    GroupClauseNode,
    JoinClauseNode,
    JoinConstraintNode,
    LimitNode,
    LiteralListNode,
    LiteralNode,
    OrderByNode,
    OrderingTerm,
    ResultColumnNode,
    SelectClauseNode,
    SelectCoreNode,
    SelectStatementNode,
    TableOrSubqueryNode,
    TerminalNode,
    WhereClauseNode,
    WindowDefinitionNode,
    WindowExpressionNode,
    WithClauseNode,
)


class NodeVisitor(ABC):
    """Abstract base class for visiting SQL AST nodes."""

    @abstractmethod
    def visit_select_statement(self, node: SelectStatementNode) -> Any:
        """
        Visit a SELECT statement node.

        Parameters
        ----------
        node : SelectStatementNode
            The SELECT statement node to visit.
        """
        pass

    @abstractmethod
    def visit_select_core(self, node: SelectCoreNode) -> Any:
        """
        Visit a SELECT core node.

        Parameters
        ----------
        node : SelectCoreNode
            The SELECT core node to visit.
        """
        pass

    @abstractmethod
    def visit_select_clause(self, node: SelectClauseNode) -> Any:
        """
        Visit a SELECT clause node.

        Parameters
        ----------
        node : SelectClauseNode
            The SELECT clause node to visit.
        """
        pass

    @abstractmethod
    def visit_group_clause(self, node: GroupClauseNode) -> Any:
        """
        Visit a GROUP BY clause node.

        Parameters
        ----------
        node : GroupClauseNode
            The GROUP BY clause node to visit.
        """
        pass

    @abstractmethod
    def visit_from_clause(self, node: FromClauseNode) -> Any:
        """
        Visit a FROM clause node.

        Parameters
        ----------
        node : FromClauseNode
            The FROM clause node to visit.
        """
        pass

    @abstractmethod
    def visit_where_clause(self, node: WhereClauseNode) -> Any:
        """
        Visit a WHERE clause node.

        Parameters
        ----------
        node : WhereClauseNode
            The WHERE clause node to visit.
        """
        pass

    @abstractmethod
    def visit_between_expression(self, node: BetweenExpressionNode) -> Any:
        """
        Visit a BETWEEN expression node.

        Parameters
        ----------
        node : BetweenExpressionNode
            The BETWEEN expression node to visit.
        """
        pass

    @abstractmethod
    def visit_order_by(self, node: OrderByNode) -> Any:
        """
        Visit an ORDER BY node.

        Parameters
        ----------
        node : OrderByNode
            The ORDER BY node to visit.
        """
        pass

    @abstractmethod
    def visit_ordering_term(self, node: OrderingTerm) -> Any:
        """
        Visit an ordering term node.

        Parameters
        ----------
        node : OrderingTerm
            The ordering term node to visit.
        """
        pass

    @abstractmethod
    def visit_limit(self, node: LimitNode) -> Any:
        """
        Visit a LIMIT node.

        Parameters
        ----------
        node : LimitNode
            The LIMIT node to visit.
        """
        pass

    @abstractmethod
    def visit_join_clause(self, node: JoinClauseNode) -> Any:
        """
        Visit a JOIN clause node.

        Parameters
        ----------
        node : JoinClauseNode
            The JOIN clause node to visit.
        """
        pass

    @abstractmethod
    def visit_join_constraint(self, node: JoinConstraintNode) -> Any:
        """
        Visit a JOIN constraint node.

        Parameters
        ----------
        node : JoinConstraintNode
            The JOIN constraint node to visit.
        """
        pass

    @abstractmethod
    def visit_table_or_subquery(self, node: TableOrSubqueryNode) -> Any:
        """
        Visit a table or subquery node.

        Parameters
        ----------
        node : TableOrSubqueryNode
            The table or subquery node to visit.
        """
        pass

    @abstractmethod
    def visit_result_column(self, node: ResultColumnNode) -> Any:
        """
        Visit a result column node.

        Parameters
        ----------
        node : ResultColumnNode
            The result column node to visit.
        """
        pass

    @abstractmethod
    def visit_column(self, node: ColumnNode) -> Any:
        """
        Visit a column node.

        Parameters
        ----------
        node : ColumnNode
            The column node to visit.
        """
        pass

    @abstractmethod
    def visit_function_expression(self, node: FunctionExpressionNode) -> Any:
        """
        Visit a function expression node.

        Parameters
        ----------
        node : FunctionExpressionNode
            The function expression node to visit.
        """
        pass

    @abstractmethod
    def visit_bin_op_expression(self, node: BinOpExpressionNode) -> Any:
        """
        Visit a binary operation expression node.

        Parameters
        ----------
        node : BinOpExpressionNode
            The binary operation expression node to visit.
        """
        pass

    @abstractmethod
    def visit_terminal(self, node: TerminalNode) -> Any:
        """
        Visit a terminal node.

        Parameters
        ----------
        node : TerminalNode
            The terminal node to visit.
        """
        pass

    @abstractmethod
    def visit_expression(self, node: ExpressionNode) -> Any:
        """
        Visit an expression node.

        Parameters
        ----------
        node : ExpressionNode
            The expression node to visit.
        """
        pass

    @abstractmethod
    def visit_literal(self, node: LiteralNode) -> Any:
        """
        Visit a literal node.

        Parameters
        ----------
        node : LiteralNode
            The literal node to visit.
        """
        pass

    @abstractmethod
    def visit_cast_expression(self, node: CastExpressionNode) -> Any:
        """
        Visit a CAST expression node.

        Parameters
        ----------
        node : CastExpressionNode
            The CAST expression node to visit.
        """
        pass

    @abstractmethod
    def visit_window_expression(self, node: WindowExpressionNode) -> Any:
        """
        Visit a window expression node.

        Parameters
        ----------
        node : WindowExpressionNode
            The window expression node to visit.
        """
        pass

    @abstractmethod
    def visit_window_definition(self, node: WindowDefinitionNode) -> Any:
        """
        Visit a window definition node.

        Parameters
        ----------
        node : WindowDefinitionNode
            The window definition node to visit.
        """
        pass

    @abstractmethod
    def visit_literal_list(self, node: LiteralListNode) -> Any:
        """
        Visit a literal list node.

        Parameters
        ----------
        node : LiteralListNode
            The literal list node to visit.
        """
        pass

    @abstractmethod
    def visit_with_clause(self, node: WithClauseNode) -> Any:
        """
        Visit a WITH clause node.

        Parameters
        ----------
        node : WithClauseNode
            The WITH clause node to visit.
        """
        pass

    @abstractmethod
    def visit_common_table_expression(self, node: CommonTableExpressionNode) -> Any:
        """
        Visit a common table expression node.

        Parameters
        ----------
        node : CommonTableExpressionNode
            The common table expression node to visit.
        """
        pass
