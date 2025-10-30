"""JOIN table count tags."""

from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import OrderedTag
from src.taxonomy.parse.node import JoinClauseNode


class JoinTables(OrderedTag):
    """Tags for number of tables in JOIN clauses."""

    SingleJoin = 1
    TwoJoin = 2
    MultiJoin = 3

    @staticmethod
    class Collector(TagCollector):
        """Collector for JOIN table counts."""

        def visit_join_clause(self, node: JoinClauseNode) -> TagCollectorResult:
            """Visit a JOIN clause node."""
            tags = cast(TagCollectorResult, super().visit_join_clause(node))
            if len(node.tables) == 2:
                return tags + TagCollectorResult(JoinTables.SingleJoin)
            return tags + TagCollectorResult(JoinTables.MultiJoin)
