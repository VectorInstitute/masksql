"""GROUP BY clause type tags."""

from typing import cast

from src.taxonomy.cat.tag_collector import TagCollector
from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.sql_tag import OrderedTag
from src.taxonomy.parse.node import GroupClauseNode


class GroupType(OrderedTag):
    """Tags for GROUP BY clause variations."""

    UnconditionalGroup = 1
    ConditionalGroup = 2

    @staticmethod
    class Collector(TagCollector):
        """Collector for GROUP BY clause types."""

        def visit_group_clause(self, node: GroupClauseNode) -> TagCollectorResult:
            """Visit a GROUP BY clause node."""
            tags = cast(TagCollectorResult, super().visit_group_clause(node))
            if node.having:
                return tags + TagCollectorResult(GroupType.ConditionalGroup)
            return tags + TagCollectorResult(GroupType.UnconditionalGroup)
