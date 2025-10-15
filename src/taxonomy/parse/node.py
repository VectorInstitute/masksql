"""SQL Abstract Syntax Tree (AST) node definitions for parsing SQL queries."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import List, Optional, Set, Union

from src.taxonomy.parse.database_schema import DatabaseSchemaSqlyzr


class SqlAstNode(ABC):
    """Abstract base class for all SQL AST nodes.

    Attributes
    ----------
    id : int
        Node identifier.
    db_id : str
        Database identifier.
    raw_sql : str
        Raw SQL query string.
    question : str
        Natural language question associated with the query.
    db_schema : DatabaseSchemaSqlyzr
        Database schema information.
    cols : Set[str]
        Set of columns referenced in the node.
    """

    id: int
    db_id: str
    raw_sql: str
    question: str
    db_schema: DatabaseSchemaSqlyzr
    cols: Set[str]

    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        pass

    def log_self(self):
        """Log this node for debugging purposes."""
        # logger.debug(f"{self.__class__.__name__}: {str(self)}")
        pass

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class TerminalNode(SqlAstNode):
    """Terminal node representing a leaf in the SQL AST.

    Represents keywords, identifiers, and literals.

    Attributes
    ----------
    name : str
        Name/type of the terminal.
    value : str
        The actual value of the terminal.
    """

    name: str
    value: str

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_terminal(self)

    def __eq__(self, other):
        """Check equality based on name and value."""
        if not isinstance(other, TerminalNode):
            return False
        if self.name == other.name and self.value == other.value:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


class ExpressionNode(SqlAstNode, ABC):
    """Abstract base class for SQL expression nodes."""

    def has_sub_expr(self):
        """Check if this expression contains sub-expressions."""
        return False


@dataclass
class BinOpExpressionNode(ExpressionNode):
    """Binary operation expression node (e.g., a + b, x = y).

    Attributes
    ----------
    left : ExpressionNode
        Left operand.
    op : TerminalNode
        Binary operator.
    right : ExpressionNode
        Right operand.
    """

    left: ExpressionNode
    op: TerminalNode
    right: ExpressionNode

    def has_sub_expr(self):
        """Check if this expression contains sub-expressions."""
        return True

    def left_and_right_terminal(self):
        """Check if both left and right operands are terminal expressions."""
        return (isinstance(self.left, str) or not self.left.has_sub_expr()) and (
            isinstance(self.right, str) or not self.right.has_sub_expr()
        )

    def is_arith_expr(self):
        """Check if this is an arithmetic expression."""
        if self.left_and_right_terminal() and self.op.value in "/*+-":
            return True
        return (
            isinstance(self.left, BinOpExpressionNode) and self.left.is_arith_expr()
        ) or (
            isinstance(self.right, BinOpExpressionNode) and self.right.is_arith_expr()
        )

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_bin_op_expression(self)

    def __eq__(self, other):
        """Check equality with operator commutativity support.

        Supports commutative operators (=, !=) and flipped comparisons (<, >, <=, >=).
        """
        if not isinstance(other, BinOpExpressionNode):
            return False

        if (
            (self.op.value == ">" and other.op.value == "<")
            or (self.op.value == ">=" and other.op.value == "<=")
            or (self.op.value == "<" and other.op.value == ">")
            or (self.op.value == "<=" and other.op.value == ">=")
        ):
            return (self.left == other.right) and (self.right == other.left)
        if (self.op.value == "=" and other.op.value == "=") or (
            self.op.value == "!=" and other.op.value == "!="
        ):
            return ((self.left == other.left) and (self.right == other.right)) or (
                (self.left == other.right) and (self.right == other.left)
            )
        if self.op.value == other.op.value:
            return (self.left == other.left) and (self.right == other.right)
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
# TODO : adding NOT BETWEEN
class BetweenExpressionNode(ExpressionNode):
    """BETWEEN expression node (e.g., expr BETWEEN lower AND upper).

    Attributes
    ----------
    expr : ExpressionNode
        The expression to test.
    lower : ExpressionNode
        Lower bound of the range.
    upper : ExpressionNode
        Upper bound of the range.
    """

    expr: ExpressionNode
    lower: ExpressionNode
    upper: ExpressionNode

    def has_sub_expr(self):
        """Check if this expression contains sub-expressions."""
        return True

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_between_expression(self)

    def __eq__(self, other):
        """Check equality based on expression and bounds."""
        if not isinstance(other, BetweenExpressionNode):
            return False
        if self.expr == other.expr:
            return self.lower == other.lower and self.upper == other.upper
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class FunctionExpressionNode(ExpressionNode):
    """Function call expression node (e.g., COUNT(*), SUM(x), EXISTS(...)).

    Attributes
    ----------
    fun_name : TerminalNode
        Function name.
    expr : List[ExpressionNode]
        Function arguments.
    negation : bool
        Whether function is negated (e.g., NOT EXISTS).
    distinct : bool
        Whether DISTINCT is specified.
    """

    fun_name: TerminalNode
    expr: List[ExpressionNode]
    negation: bool = False  # Used when not of function used NOT EXISTS
    distinct: bool = False

    def has_sub_expr(self):
        """Check if this expression contains sub-expressions."""
        return True

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_function_expression(self)

    def __eq__(self, other):
        """Check equality based on function name, arguments, and negation."""
        if not isinstance(other, FunctionExpressionNode):
            return False
        if (
            self.fun_name == other.fun_name
            and self.expr == other.expr
            and self.negation == other.negation
        ):  # and self.distinct == other.distinct:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class ColumnNode(ExpressionNode):
    """Column reference node (e.g., table.column or column).

    Attributes
    ----------
    column_name : TerminalNode
        Column name.
    table_name : Optional[TerminalNode]
        Table name if qualified.
    """

    column_name: TerminalNode
    table_name: Optional[TerminalNode] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_column(self)

    def exists_in_foreign_keys(self, node: "ColumnNode"):
        """Check if the node's column exists in foreign key relationships."""
        for foreign_key_set in self.db_schema.foreign_keys:
            if (
                node.table_name
                and (node.table_name.value, node.column_name.value) in foreign_key_set
            ):
                return True
        return False

    def __eq__(self, other):
        """Check equality based on column and table names.

        Also checks foreign key relationships.
        """
        if not isinstance(other, ColumnNode):
            return False
        if (
            self.column_name == other.column_name
            and self.table_name == other.table_name
        ) or (self.exists_in_foreign_keys(self) and self.exists_in_foreign_keys(other)):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class LiteralNode(ExpressionNode):
    """Literal value node (e.g., 42, 'string', 3.14).

    Attributes
    ----------
    value : Union[int, str, ExpressionNode]
        The literal value.
    """

    value: Union[int, str, ExpressionNode]

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_literal(self)

    def __eq__(self, other):
        """Check equality - always returns True for literal comparison."""
        return True
        # if not isinstance(other, LiteralNode):
        #     return True
        # # if self.value == other.value:
        # #     return True
        # else:
        #     return True

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class LiteralListNode(ExpressionNode):
    """List of literal values node (e.g., IN (1, 2, 3)).

    Attributes
    ----------
    literals : List[LiteralNode]
        List of literal values.
    """

    literals: List[LiteralNode]

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_literal_list(self)

    def __add__(self, other):
        """Add a literal to this list."""
        if isinstance(other, LiteralNode):
            return replace(self, literals=self.literals + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on set of literals."""
        if not isinstance(other, LiteralListNode):
            return False
        return set(self.literals) == set(other.literals)

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
# 4
class ResultColumnNode(SqlAstNode):
    """Result column in SELECT clause (e.g., expr AS alias).

    Attributes
    ----------
    expr : ExpressionNode
        The expression for this result column.
    column_alias : Optional[TerminalNode]
        Optional alias for the column.
    """

    expr: ExpressionNode
    column_alias: Optional[TerminalNode] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_result_column(self)

    def __eq__(self, other):
        """Check equality based on expression and alias."""
        if not isinstance(other, ResultColumnNode):
            return False
        if self.expr == other.expr and self.column_alias == other.column_alias:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
# 3
class SelectClauseNode(SqlAstNode):
    """SELECT clause node with result columns.

    Attributes
    ----------
    result_columns : List[ResultColumnNode]
        List of result columns to select.
    distinct : bool
        Whether DISTINCT is specified.
    """

    result_columns: List[ResultColumnNode]
    distinct: bool = False

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_select_clause(self)

    def __add__(self, other):
        """Add a result column to this SELECT clause."""
        if isinstance(other, ResultColumnNode):
            return replace(self, result_columns=self.result_columns + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on set of result columns."""
        if not isinstance(other, SelectClauseNode):
            return False
        if set(self.result_columns) == set(
            other.result_columns
        ):  # and self.distinct == other.distinct:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class TableOrSubqueryNode(SqlAstNode):
    """Table or subquery node for FROM clause.

    Attributes
    ----------
    schema_name : Optional[TerminalNode]
        Schema name if specified.
    table_name : Optional[TerminalNode]
        Table name.
    select_statement : Optional[SelectStatementNode]
        Subquery if this is a subquery.
    table_alias : Optional[TerminalNode]
        Alias for the table or subquery.
    join_clause : Optional[JoinClauseNode]
        JOIN clause if present.
    """

    schema_name: Optional[TerminalNode] = None
    table_name: Optional[TerminalNode] = None  # none or one object
    select_statement: Optional["SelectStatementNode"] = None
    table_alias: Optional[TerminalNode] = None
    join_clause: Optional["JoinClauseNode"] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_table_or_subquery(self)

    def __eq__(self, other):
        """Check equality based on schema, table, subquery, and join clause."""
        if not isinstance(other, TableOrSubqueryNode):
            return False
        if (
            self.table_name == other.table_name
            and self.schema_name == other.schema_name
            and self.select_statement == other.select_statement
            and self.join_clause == other.join_clause
        ):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class JoinConstraintNode(SqlAstNode):
    """JOIN constraint node (e.g., ON condition).

    Attributes
    ----------
    expr : ExpressionNode
        The join condition expression.
    """

    expr: ExpressionNode

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_join_constraint(self)

    def __eq__(self, other):
        """Check equality based on join condition expression."""
        if not isinstance(other, JoinConstraintNode):
            return False
        if self.expr == other.expr:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class JoinClauseNode(SqlAstNode):
    """JOIN clause node with tables, operators, and constraints.

    Attributes
    ----------
    tables : List[TableOrSubqueryNode]
        List of tables in the join.
    ops : List[TerminalNode]
        Join operators (JOIN, LEFT JOIN, etc.).
    constraints : List[Optional[JoinConstraintNode]]
        Join constraints (ON conditions).
    """

    tables: List[TableOrSubqueryNode]
    ops: List[TerminalNode]
    constraints: List[Optional[JoinConstraintNode]]

    def add_table(
        self,
        table_or_subquery: TableOrSubqueryNode,
        op: TerminalNode,
        constraint: Optional[JoinConstraintNode],
    ):
        """Add a table to the join with its operator and constraint."""
        return replace(
            self,
            tables=self.tables + [table_or_subquery],
            ops=self.ops + [op],
            constraints=self.constraints + [constraint],
        )

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_join_clause(self)

    def __eq__(self, other):
        """Check equality based on tables, operators, and constraints."""
        if not isinstance(other, JoinClauseNode):
            return False
        if (
            set(self.tables) == set(other.tables)
            and self.ops == other.ops
            and self.constraints == other.constraints
        ):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class OrderingTerm(SqlAstNode):
    """Ordering term in ORDER BY clause (e.g., column ASC/DESC).

    Attributes
    ----------
    expr : ExpressionNode
        The expression to order by.
    sort_order : Optional[TerminalNode]
        Sort direction (ASC or DESC).
    """

    expr: ExpressionNode
    sort_order: Optional[TerminalNode] = None  # ascending or descending

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_ordering_term(self)

    def __eq__(self, other):
        """Check equality based on expression and sort order."""
        if not isinstance(other, OrderingTerm):
            return False
        if self.expr == other.expr:
            # handling the case of having asc in pred and None in gold or reverse
            if (
                (self.sort_order != None and other.sort_order != None)
                and self.sort_order.value != other.sort_order.value
                or (self.sort_order != None and other.sort_order == None)
                and self.sort_order.value == "desc"
            ):
                return False
            return not (
                (self.sort_order == None and other.sort_order != None)
                and other.sort_order.value == "desc"
            )
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class OrderByNode(SqlAstNode):
    """ORDER BY clause node specifying sort order for query results.

    Attributes
    ----------
    ordering_terms : List[OrderingTerm]
        List of ordering terms specifying sort expressions and directions.
    """

    ordering_terms: List[OrderingTerm]

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_order_by(self)

    def __add__(self, other):
        """Add an ordering term to this ORDER BY clause."""
        if isinstance(other, OrderingTerm):
            return replace(self, ordering_terms=self.ordering_terms + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on ordering terms."""
        if not isinstance(other, OrderByNode):
            return False
        if self.ordering_terms == other.ordering_terms:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class LimitNode(SqlAstNode):
    """LIMIT clause node for restricting result set size.

    Attributes
    ----------
    expr : List[ExpressionNode]
        List of expressions for LIMIT and optional OFFSET.
    """

    expr: List[ExpressionNode]

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_limit(self)

    def __eq__(self, other):
        """Check equality based on limit expressions."""
        if not isinstance(other, LimitNode):
            return False
        if self.expr == other.expr:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class FromClauseNode(SqlAstNode):
    """FROM clause node specifying tables and joins.

    Attributes
    ----------
    tables : List[TableOrSubqueryNode]
        List of tables or subqueries in the FROM clause.
    join_clause : Optional[JoinClauseNode]
        JOIN clause if present.
    """

    tables: List[TableOrSubqueryNode]
    join_clause: Optional[JoinClauseNode] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_from_clause(self)

    def __add__(self, other):
        """Add a table or subquery to this FROM clause."""
        if isinstance(other, TableOrSubqueryNode):
            return replace(self, tables=self.tables + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on tables and join clause."""
        if not isinstance(other, FromClauseNode):
            return False
        if (
            set(self.tables) == set(other.tables)
            and self.join_clause == other.join_clause
        ):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class WhereClauseNode(SqlAstNode):
    """WHERE clause node containing filter conditions.

    Attributes
    ----------
    expr : ExpressionNode
        The filter expression.
    """

    expr: ExpressionNode

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_where_clause(self)

    def __eq__(self, other):
        """Check equality based on extracted variables from the expression."""
        if not isinstance(other, WhereClauseNode):
            return False
        ve = variable_extractor(self.expr)
        vo = variable_extractor(other.expr)
        if ve == vo:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class GroupClauseNode(SqlAstNode):
    """GROUP BY clause node with grouping expressions and HAVING clause.

    Attributes
    ----------
    exprs : List[ExpressionNode]
        Grouping expressions.
    having : Optional[ExpressionNode]
        HAVING clause filter condition.
    rollup : bool
        Whether WITH ROLLUP is specified.
    """

    exprs: List[ExpressionNode]
    having: Optional[ExpressionNode] = None
    rollup: bool = False

    def __add__(self, other):
        """Add a grouping expression to this GROUP BY clause."""
        if isinstance(other, ExpressionNode):
            return replace(self, exprs=self.exprs + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_group_clause(self)

    def __eq__(self, other):
        """Check equality based on grouping expressions and HAVING clause."""
        if not isinstance(other, GroupClauseNode):
            return False
        if set(self.exprs) == set(other.exprs) and self.having == other.having:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
# 2: the select
class SelectCoreNode(SqlAstNode):
    """Core SELECT clause node containing SELECT, FROM, WHERE, and GROUP BY.

    Attributes
    ----------
    select_clause : SelectClauseNode
        The SELECT clause with result columns.
    from_clause : Optional[FromClauseNode]
        The FROM clause with tables/subqueries.
    where_clause : Optional[WhereClauseNode]
        The WHERE clause with filter conditions.
    group_clause : Optional[GroupClauseNode]
        The GROUP BY clause with grouping expressions.
    """

    select_clause: SelectClauseNode
    from_clause: Optional[FromClauseNode] = None
    where_clause: Optional[WhereClauseNode] = None
    group_clause: Optional[GroupClauseNode] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_select_core(self)

    def __eq__(self, other):
        """Check equality based on all clauses."""
        if not isinstance(other, SelectCoreNode):
            return False
        if (
            self.select_clause == other.select_clause
            and self.from_clause == other.from_clause
            and self.where_clause == other.where_clause
            and self.group_clause == other.group_clause
        ):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class CommonTableExpressionNode(SqlAstNode):
    """Common Table Expression (CTE) node for WITH clause subqueries.

    Attributes
    ----------
    table_name : LiteralNode
        Name of the CTE.
    columns : List[ColumnNode]
        Column list for the CTE (optional).
    select_stmt : SelectStatementNode
        The SELECT statement defining the CTE.
    """

    table_name: LiteralNode
    columns: List[ColumnNode]
    select_stmt: "SelectStatementNode"

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_common_table_expression(self)

    def __add__(self, other):
        """Add a column to this CTE."""
        if isinstance(other, ColumnNode):
            return replace(self, columns=self.columns + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on table name, columns, and select statement."""
        if not isinstance(other, CommonTableExpressionNode):
            return False
        return (
            self.table_name == other.table_name
            and self.columns == other.columns
            and self.select_stmt == other.select_stmt
        )

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class WithClauseNode(SqlAstNode):
    """WITH clause node for common table expressions (CTEs).

    Attributes
    ----------
    common_table_expr : List[CommonTableExpressionNode]
        List of common table expressions in the WITH clause.
    """

    common_table_expr: List[CommonTableExpressionNode]

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_with_clause(self)

    def __add__(self, other):
        """Add a common table expression to this WITH clause."""
        if isinstance(other, CommonTableExpressionNode):
            return replace(self, common_table_expr=self.common_table_expr + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __hash__(self):
        """Return hash value for this node."""
        return 1

    def __eq__(self, other):
        """Check equality based on common table expressions."""
        if not isinstance(other, WithClauseNode):
            return False
        if self.common_table_expr == other.common_table_expr:
            return True
        self.log_self()
        return False


@dataclass
# 1: all the sql statement
class SelectStatementNode(ExpressionNode):
    """Complete SELECT statement node representing a full SQL query.

    Attributes
    ----------
    select_cores : List[SelectCoreNode]
        List of SELECT cores (can be multiple with set operations).
    set_ops : List[TerminalNode]
        Set operations connecting select cores (UNION, INTERSECT, etc.).
    orderby : Optional[OrderByNode]
        ORDER BY clause for the statement.
    limit : Optional[LimitNode]
        LIMIT clause for the statement.
    with_clause : Optional[WithClauseNode]
        WITH clause (CTEs) for the statement.
    """

    select_cores: List[SelectCoreNode]
    set_ops: List[TerminalNode]
    orderby: Optional[OrderByNode] = None
    limit: Optional[LimitNode] = None
    with_clause: Optional[WithClauseNode] = None

    def has_sub_expr(self):
        """Check if this expression contains sub-expressions."""
        return True

    def add_core(self, set_op: TerminalNode, select_core: SelectCoreNode):
        """Add a select core with a set operation (UNION, INTERSECT, etc.)."""
        return replace(
            self,
            select_cores=self.select_cores + [select_core],
            set_ops=self.set_ops + [set_op],
        )

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_select_statement(self)

    def __eq__(self, other):
        """Check equality based on select cores, set operations, and clauses."""
        if not isinstance(other, SelectStatementNode):
            return False
        if (
            set(self.select_cores) == set(other.select_cores)
            and set(self.set_ops) == set(other.set_ops)
            and self.orderby == other.orderby
            and self.with_clause == other.with_clause
            and self.limit == other.limit
        ):
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class CastExpressionNode(ExpressionNode):
    """CAST expression node (e.g., CAST(expr AS type)).

    Attributes
    ----------
    expr : ExpressionNode
        Expression to be cast.
    type_name : TerminalNode
        Target type name.
    """

    expr: ExpressionNode
    type_name: TerminalNode  # all things that we don't know to use which func!

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_cast_expression(self)

    def __eq__(self, other):
        """Check equality based on expression and type name."""
        if not isinstance(other, CastExpressionNode):
            return False
        if self.expr == other.expr and self.type_name == other.type_name:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class WindowDefinitionNode(SqlAstNode):
    """Window definition node for OVER clauses (PARTITION BY and ORDER BY).

    Attributes
    ----------
    cols : List[ResultColumnNode]
        Columns for PARTITION BY clause.
    orderby : Optional[OrderByNode]
        ORDER BY clause within the window.
    """

    cols: List[ResultColumnNode]
    orderby: Optional[OrderByNode] = None

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_window_definition(self)

    def __add__(self, other):
        """Add a result column to this window definition."""
        if isinstance(other, ResultColumnNode):
            return replace(self, cols=self.cols + [other])
        raise RuntimeError("Invalid operand type: {}".format(type(other)))

    def __eq__(self, other):
        """Check equality based on columns and order by clause."""
        if not isinstance(other, WindowDefinitionNode):
            return False
        if self.orderby == other.orderby and self.col == other.col:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


@dataclass
class WindowExpressionNode(ExpressionNode):
    """Window function expression node (e.g., RANK() OVER (...)).

    Attributes
    ----------
    win_fun : TerminalNode
        Window function name.
    win_fun_exprs : List[ExpressionNode]
        Arguments to the window function.
    win_def : WindowDefinitionNode
        Window definition (PARTITION BY and ORDER BY clauses).
    distinct : bool
        Whether DISTINCT is applied.
    """

    win_fun: TerminalNode
    win_fun_exprs: List[ExpressionNode]
    win_def: WindowDefinitionNode
    distinct: bool = False

    def accept(self, visitor):
        """Accept a visitor for the visitor pattern implementation."""
        return visitor.visit_window_expression(self)

    def __eq__(self, other):
        """Check equality based on window function and definition."""
        if not isinstance(other, WindowExpressionNode):
            return False
        if self.win_fun == other.win_fun and self.win_def == other.win_fun:
            return True
        self.log_self()
        return False

    def __hash__(self):
        """Return hash value for this node."""
        return 1


def variable_extractor(expr: ExpressionNode) -> Set[SqlAstNode]:
    """Extract variables from binary operation expressions.

    Parameters
    ----------
    expr : ExpressionNode
        The expression node to extract variables from.

    Returns
    -------
    Set[SqlAstNode]
        Set of extracted variable nodes.
    """
    if not isinstance(expr, BinOpExpressionNode):
        return set()
    if expr.op.value in {"and", "or"}:
        return (
            variable_extractor(expr.left)
            .union(variable_extractor(expr.right))
            .union([expr.op])
        )
    return {expr}
