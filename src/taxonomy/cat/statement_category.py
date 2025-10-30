"""SQL statement category representation."""

from typing import Set

from src.taxonomy.cat.sub_category import SubCategory


class StatementCategory:
    """Represents a category of SQL statements with a complexity rank."""

    rank: int
    sub_cats: Set[SubCategory]

    def __init__(self, rank: int, *tag_sets: SubCategory):
        self.rank = rank
        self.sub_cats = set(tag_sets)

    @property
    def name(self) -> str:
        """Get the category name.

        Returns
        -------
        str
            Category name in format 'cN' where N is the rank.
        """
        return f"c{self.rank}"

    def __str__(self) -> str:
        """Return string representation of the category."""
        return self.name

    def __le__(self, other: "StatementCategory") -> bool:
        """Compare categories by rank (less than or equal)."""
        if not isinstance(other, StatementCategory):
            raise RuntimeError(f"Invalid operand: {type(other)}")
        return self.rank <= other.rank

    def matches(self, feature_set: SubCategory) -> list[SubCategory] | None:
        """Check if a feature set matches any sub-categories.

        Parameters
        ----------
        feature_set : SubCategory
            The feature set to match against.

        Returns
        -------
        list or None
            List of matching sub-categories or None if no matches.
        """
        matches = []
        for fs in self.sub_cats:
            if feature_set >= fs:
                matches.append(fs)
        if len(matches) > 0:
            return matches
        return None
