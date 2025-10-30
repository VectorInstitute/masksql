"""Result object for tag collection."""

from typing import Set

from src.taxonomy.cat.sub_category import SubCategory
from src.taxonomy.cat.tags.sql_tag import SqlTag
from src.taxonomy.parse.visitor.visitor_result import MergeableVisitorResult


class TagCollectorResult(MergeableVisitorResult):
    """Stores collected SQL tags and allows merging of results."""

    tag_set: SubCategory
    extras: Set[str]

    def __init__(self, *tags: SqlTag):
        self.tag_set = SubCategory("", frozenset([*tags]))
        self.extras = set()

    def merge(self, other: "TagCollectorResult") -> "TagCollectorResult":
        """Merge another tag collector result into this one.

        Parameters
        ----------
        other : TagCollectorResult
            The result to merge.

        Returns
        -------
        TagCollectorResult
            This result after merging.
        """
        if isinstance(other, TagCollectorResult):
            self.tag_set += other.tag_set
        return self

    def add(self, tag: SqlTag) -> None:
        """Add a tag to the result.

        Parameters
        ----------
        tag : SqlTag
            The tag to add.
        """
        self.tag_set += tag

    def add_extra(self, s: str) -> None:
        """Add an extra string value to the result.

        Parameters
        ----------
        s : str
            The extra value to add.
        """
        self.extras.add(s)

    def __str__(self) -> str:
        """Return string representation of the tag set."""
        return str(self.tag_set)
