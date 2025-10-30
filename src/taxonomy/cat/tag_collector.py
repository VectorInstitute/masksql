"""Tag collection visitor for SQL AST."""

from typing import cast

from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.parse.node import FromClauseNode
from src.taxonomy.parse.visitor.collector_visitor import CollectorVisitor


class TagCollector(CollectorVisitor):
    """Visitor that collects SQL tags from an AST."""

    def __init__(self) -> None:
        super().__init__(TagCollectorResult)


class TableCountCollector(TagCollector):
    """Visitor that counts unique table names in SQL queries."""

    def __init__(self) -> None:
        super().__init__()
        self.uniq_table_names: set[str] = set()

    def visit_from_clause(self, node: FromClauseNode) -> TagCollectorResult:
        """Visit a FROM clause node."""
        for table in node.tables:
            if table.table_name:
                self.uniq_table_names.add(str(table.table_name.value))
        return cast(TagCollectorResult, super().visit_from_clause(node))
