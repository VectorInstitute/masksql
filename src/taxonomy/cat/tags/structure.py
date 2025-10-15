"""SQL query structure type tags."""

from enum import auto

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.node import SelectStatementNode


class StructureType(SqlTag):
    """Tags for query structure like compound and nested queries."""

    Compound = auto()
    Nested = auto()

    @staticmethod
    class Collector(TagCollector):
        """Collector for query structure types."""

        cur_level: int
        max_level: int

        def __init__(self):
            """Initialize the collector with structure tracking."""
            super().__init__()
            self.cur_level = 0
            self.max_level = 0

        def visit_select_statement(self, node: SelectStatementNode):
            """Visit a SELECT statement node."""
            self.cur_level += 1
            self.max_level = max(self.max_level, self.cur_level)
            tags = super().visit_select_statement(node)
            if len(node.set_ops) > 0:
                tags += TagCollectorResult(StructureType.Compound)
            if self.cur_level > 1:
                tags += TagCollectorResult(StructureType.Nested)
            self.cur_level -= 1
            return tags
