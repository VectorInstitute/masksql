"""SQL statement categorizer."""

from typing import List

from natsort import natsorted

from src.taxonomy.cat.categories import CAT_INF, CATS, SUB_INF
from src.taxonomy.cat.statement_category import StatementCategory
from src.taxonomy.cat.sub_category import SubCategory


class Categorizer:
    """Categorizes SQL statements based on their tags."""

    categories: List[StatementCategory]

    def __init__(self, categories=None):
        if categories is None:
            categories = CATS
        self.categories = categories

    def get_category(self, tag_set: SubCategory):
        """Get the statement category for a given tag set.

        Parameters
        ----------
        tag_set : SubCategory
            The tag set to categorize.

        Returns
        -------
        StatementCategory
            The matching category or CAT_INF if no match found.
        """
        for c in reversed(self.categories):  # Check to find a match starting from
            # harder categories
            sub_cat = c.matches(tag_set)
            if sub_cat:
                # return f"{c.name}_{sub_cat.name}"
                # return f"{sub_cat.name}"
                # return f"{c.name}"
                return c
        return CAT_INF

    def get_sub_category(self, tag_set: SubCategory):
        """Get the sub-category for a given tag set.

        Parameters
        ----------
        tag_set : SubCategory
            The tag set to categorize.

        Returns
        -------
        SubCategory
            The matching sub-category or SUB_INF if no match found.
        """
        for c in reversed(self.categories):  # Check to find a match starting from
            # harder categories
            sub_cats = c.matches(tag_set)
            if sub_cats:
                sorted_sub_cats = natsorted(sub_cats, key=lambda s: s.name)
                return sorted_sub_cats[-1]
                # return f"{c.name}_{sub_cat.name}"
                # return f"{sub_cat.name}"
                # return f"{c.name}"

        return SUB_INF
