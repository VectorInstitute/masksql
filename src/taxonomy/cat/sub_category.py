"""SQL statement sub-category representation."""

from dataclasses import dataclass, replace
from typing import FrozenSet, Type

from src.taxonomy.cat.tags.sql_tag import SqlTag


@dataclass(eq=True, frozen=True)
class SubCategory:
    """Represents a sub-category of SQL statements with associated tags."""

    name: str
    tags: FrozenSet[SqlTag]
    description: str = ""

    def __ge__(self, other: "SubCategory"):
        """Check if this sub-category is at least as complex as another."""
        return all(self.has_greater(tag) for tag in other.tags)

    def __lt__(self, other):
        """Check if this sub-category is less complex than another."""
        return not (self >= other)

    def has_greater(self, tag: SqlTag):
        """Check if this sub-category has a tag greater than or equal to the given tag.

        Parameters
        ----------
        tag : SqlTag
            The tag to compare against.

        Returns
        -------
        bool
            True if this sub-category contains a greater or equal tag.
        """
        return any(t >= tag for t in self.tags)

    def __str__(self):
        """Return string representation of the sub-category."""
        return self.name

    def __add__(self, other):
        """Add a tag or another sub-category's tags to this sub-category."""
        if isinstance(other, SqlTag):
            return replace(self, tags=self.tags.union({other}))
        if isinstance(other, SubCategory):
            return replace(self, tags=self.tags.union(other.tags))
        raise RuntimeError(f"Invalid add operand type {type(other)}")

    def get_val(self, tag_type: Type[SqlTag]) -> str:
        """Get the value of a specific tag type from this sub-category.

        Parameters
        ----------
        tag_type : Type[SqlTag]
            The type of tag to retrieve.

        Returns
        -------
        str
            The name of the tag if found, otherwise "None".
        """
        intersection = self.tags.intersection(tag_type.__members__.values())
        if len(intersection) > 0:
            return next(iter(intersection)).name
        return "None"

    # def reduce(self):
    #     """Remove any tag if some other tag harder or equal than it exists"""
    #     to_remove = set()
    #     for t in self.tags:
    #         for ot in self.tags:
    #             if t != ot and ot >= t:
    #                 to_remove.add(t)
    #     return SubCategory(frozenset(self.tags.difference(to_remove)))
    #
    def __repr__(self):
        """Return string representation of the sub-category."""
        return str(self)
