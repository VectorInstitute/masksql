"""Nesting level tags."""

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.node import SelectStatementNode


class NestLevel(SqlTag):
    """Tags for query nesting depth."""

    Zero = 0
    One = 1
    Two = 2
    Many = 3

    @staticmethod
    class Collector(TagCollector):
        """Collector for query nesting levels."""

        def __init__(self):
            """Initialize the collector with nesting level tracking."""
            super().__init__()
            self.cur_level = 0
            self.max_level = 0

        def visit_select_statement(self, node: SelectStatementNode):
            """Visit a SELECT statement node."""
            self.cur_level += 1
            self.max_level = max(self.max_level, self.cur_level)
            tags = super().visit_select_statement(node)
            max_level = self.max_level
            match max_level:
                case 1:
                    tags += TagCollectorResult(NestLevel.Zero)
                case 2:
                    tags += TagCollectorResult(NestLevel.One)
                case 3:
                    tags += TagCollectorResult(NestLevel.Two)
                case max_level if max_level > 3:
                    tags += TagCollectorResult(NestLevel.Many)
            self.cur_level -= 1
            return tags
