"""Number of joins tags (currently unused)."""

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tags.sql_tag import SqlTag


class NumJoins(SqlTag):
    """Tags for counting number of joins in a query."""

    Zero = 0
    One = 1
    Two = 2
    Many = 3

    @staticmethod
    class Collector(TagCollector):
        """Collector for join count (currently not fully implemented)."""

        def __init__(self) -> None:
            super().__init__()
            self.cur_level: int = 0
            self.max_level: int = 0

        # def visit_join_clause(self, node: JoinClauseNode):
        # def visit_select_statement(self, node: SelectStatementNode):
        #     self.cur_level += 1
        #     if self.cur_level > self.max_level:
        #         self.max_level = self.cur_level
        #     tags = super().visit_select_statement(node)
        #     max_level = self.max_level
        #     match max_level:
        #         case 1:
        #             tags += TagCollectorResult(NestLevel.Zero)
        #         case 2:
        #             tags += TagCollectorResult(NestLevel.One)
        #         case 3:
        #             tags += TagCollectorResult(NestLevel.Two)
        #         case max_level if max_level > 3:
        #             tags += TagCollectorResult(NestLevel.Many)
        #     self.cur_level -= 1
        #     return tags
