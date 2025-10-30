"""JOIN condition type tags."""

from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import OrderedTag
from src.taxonomy.parse.node import JoinClauseNode


class JoinConditions(OrderedTag):
    """Tags for JOIN clause condition variations."""

    UnconditionalJoin = 1
    ConditionalJoin = 2

    @staticmethod
    class Collector(TagCollector):
        """Collector for JOIN condition types."""

        def visit_join_clause(self, node: JoinClauseNode) -> TagCollectorResult:
            """Visit a JOIN clause node."""
            tags = cast(TagCollectorResult, super().visit_join_clause(node))
            if any(con is not None for con in node.constraints):
                return tags + TagCollectorResult(JoinConditions.ConditionalJoin)
            return tags + TagCollectorResult(JoinConditions.UnconditionalJoin)
