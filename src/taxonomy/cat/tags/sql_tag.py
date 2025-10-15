"""Base SQL tag classes."""

from enum import Enum


class SqlTag(Enum):
    """Base class for SQL tags."""

    def __ge__(self, other):
        """Check if this tag is greater than or equal to another."""
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __str__(self):
        """Return string representation of the tag."""
        return self.name


class OrderedTag(SqlTag):
    """SQL tag with ordering based on complexity."""

    def __ge__(self, other):
        """Check if this tag is at least as hard as another.

        (t1 >= t2 ==> t1 is at least as hard as t2).
        """
        if not isinstance(other, self.__class__):
            return False
        return self.value >= other.value
