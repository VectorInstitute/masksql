"""Tag extraction from SQL AST."""

from src.taxonomy.cat.tag_collector_result import TagCollectorResult
from src.taxonomy.cat.tags.complex_keys import ComplexKeywords
from src.taxonomy.cat.tags.expr_type import ExprType
from src.taxonomy.cat.tags.extra import ExtraKeywords
from src.taxonomy.cat.tags.group_cond import GroupType
from src.taxonomy.cat.tags.join_cond import JoinConditions
from src.taxonomy.cat.tags.join_tables import JoinTables
from src.taxonomy.cat.tags.join_type import JoinType
from src.taxonomy.cat.tags.nest_level import NestLevel
from src.taxonomy.cat.tags.select_columns import SelectColumns
from src.taxonomy.cat.tags.structure import StructureType
from src.taxonomy.cat.tags.where_exprs import WhereType
from src.taxonomy.parse.node import SqlAstNode


class TagExtractor:
    """Extracts SQL tags from an abstract syntax tree."""

    def extract_tags(self, ast: SqlAstNode) -> TagCollectorResult:
        """Extract all SQL tags from an AST.

        Parameters
        ----------
        ast : SqlAstNode
            The SQL abstract syntax tree to extract tags from.

        Returns
        -------
        TagCollectorResult
            The collected tags from the AST.
        """
        collectors = [
            SelectColumns.Collector(),
            ExprType.Collector(),
            GroupType.Collector(),
            JoinConditions.Collector(),
            JoinTables.Collector(),
            ExtraKeywords.Collector(),
            ComplexKeywords.Collector(),
            JoinType.Collector(),
            NestLevel.Collector(),
            StructureType.Collector(),
            WhereType.Collector(),
        ]

        tags = TagCollectorResult()
        for collector in collectors:
            if ast is not None:
                tags += ast.accept(collector)

        return tags
