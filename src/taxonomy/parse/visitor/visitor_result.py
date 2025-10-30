"""Abstract base class for mergeable visitor results."""

from abc import ABC, abstractmethod
from typing import Self


class MergeableVisitorResult(ABC):
    """Contains the result of visiting an AstNode.

    The result of a node children can be merged to compose
    the result of visiting parent node.
    """

    def __add__(self, other: Self) -> Self:
        """
        Add two visitor results by merging them.

        Parameters
        ----------
        other : MergeableVisitorResult
            The other result to merge with.

        Returns
        -------
        MergeableVisitorResult
            The merged result.
        """
        return self.merge(other)

    @abstractmethod
    def merge(self, other: Self) -> Self:
        """
        Merge this result with another result.

        Parameters
        ----------
        other : MergeableVisitorResult
            The other result to merge with.

        Returns
        -------
        MergeableVisitorResult
            The merged result.
        """
        pass
