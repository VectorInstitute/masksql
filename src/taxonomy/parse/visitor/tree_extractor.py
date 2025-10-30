"""Extract diagram tree representation from SQL AST nodes."""

from typing import Any

from src.taxonomy.parse.node import (
    JoinClauseNode,
    SelectStatementNode,
    SqlAstNode,
    TerminalNode,
)
from src.taxonomy.parse.tree_node import DiagramTreeNode
from src.taxonomy.parse.visitor.collector_visitor import CollectorVisitor
from src.util.str_utils import split_pascal


class AstDiagramTreeExtractor(CollectorVisitor):
    """Extract a diagram tree structure from SQL AST nodes for visualization."""

    def __init__(self) -> None:
        super().__init__(DiagramTreeNode)

    def get_new_result_instance(self, attr: Any) -> DiagramTreeNode | None:
        """
        Create a new diagram tree node instance from an attribute.

        Parameters
        ----------
        attr : Any
            The attribute to convert to a diagram tree node.

        Returns
        -------
        DiagramTreeNode or None
            A diagram tree node representing the attribute, or None if attr is None.
        """
        if attr:
            if isinstance(attr, SqlAstNode):
                name = attr.__class__.__name__
                name = name.replace("Node", "")
                name = split_pascal(name)
                return DiagramTreeNode(name)
            return DiagramTreeNode(str(attr))
        return None

    def get_join_attrs(self, node: JoinClauseNode) -> list[Any]:
        """
        Get join clause attributes.

        Returns attributes as a list with the pattern:
        (table [op] [constraint])*

        Parameters
        ----------
        node : JoinClauseNode
            The join clause node.

        Returns
        -------
        list
            List of attributes from the join clause.
        """
        attrs = []
        if len(node.tables) > 0:
            attrs.append(node.tables[0])
            for table, op, constraint in zip(
                node.tables[1:], node.ops, node.constraints
            ):
                attrs.append(op)
                attrs.append(table)
                if constraint:
                    attrs.append(constraint)
        return attrs

    def get_select_stmt_attrs(self, node: SelectStatementNode):
        """
        Get select statement attributes.

        Returns attributes as a list with the pattern:
        select_core (op select_core)*

        Parameters
        ----------
        node : SelectStatementNode
            The select statement node.

        Returns
        -------
        list
            List of attributes from the select statement.
        """
        attrs = []
        if len(node.select_cores) > 0:
            attrs.append(node.select_cores[0])
            for core, op in zip(node.select_cores[1:], node.set_ops):
                attrs.append(op)
                attrs.append(core)
        if node.orderby:
            attrs.append(node.orderby)
        if node.limit:
            attrs.append(node.limit)
        return attrs

    def get_attrs(self, node: SqlAstNode) -> list[Any]:
        """
        Get attributes for a SQL AST node.

        Parameters
        ----------
        node : SqlAstNode
            The SQL AST node.

        Returns
        -------
        list
            List of node attributes.
        """
        if isinstance(node, JoinClauseNode):
            return self.get_join_attrs(node)
        if isinstance(node, SelectStatementNode):
            return self.get_select_stmt_attrs(node)
        return super().get_attrs(node)

    def visit_terminal(self, node: TerminalNode):
        """
        Visit a terminal node and create a diagram tree node.

        Parameters
        ----------
        node : TerminalNode
            The terminal node to visit.

        Returns
        -------
        DiagramTreeNode
            A diagram tree node representing the terminal with an ellipse shape.
        """
        return DiagramTreeNode("{}:{}".format(node.name, node.value), "ellipse")
